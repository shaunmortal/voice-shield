"""Voice Shield engine: live call audio -> 2-stage anti-spoof -> calibrated risk.

Audio sources (all become 16 kHz mono PCM through ffmpeg, so the detector never
cares where speech came from):
  phone       real SIM call audio from an Android phone over USB (scrcpy voice-call source)
  mic         laptop microphone (call on speakerphone)
  file:PATH   a recorded clip, played in real time (demo / tests)
"""
import os
import subprocess
import tempfile
import threading
import time
from collections import deque

import numpy as np

SR = 16000
HOP_S = 1.0          # run Stage 1 every second
WIN_S = 2.0          # on the last 2 s of audio
CONFIRM_WIN_S = 4.0  # Stage 2 looks at a longer window
SPEECH_DBFS = -45    # below this RMS the window is treated as silence
# Stage 1: NII AntiDeepfake Wav2Vec2-Small (95M, ~75 ms / 4 s on M1 MPS, CC BY-NC-SA 4.0 weights)
# Stage 2: Speech-Arena DF_Arena_500M (~230 ms, non-commercial), only run when Stage 1 is suspicious
STAGE2 = 'Speech-Arena-2025/DF_Arena_500M_V_1'


def pcm_stream(source):
    """Yield float32 chunks of HOP_S seconds from the chosen source."""
    procs = []
    if source == 'phone':
        fifo = os.path.join(tempfile.mkdtemp(), 'call.wav')
        os.mkfifo(fifo)
        procs.append(subprocess.Popen(
            ['scrcpy', '--no-video', '--no-window', '--no-playback', '--audio-source=voice-call',
             '--audio-codec=raw', '--record-format=wav', f'--record={fifo}'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        ff_in = ['-i', fifo]
    elif source == 'mic':
        ff_in = ['-f', 'avfoundation', '-i', ':default']
    elif source.startswith('file:'):
        ff_in = ['-re', '-i', source[5:]]
    else:
        raise ValueError(f'unknown source {source!r}')
    ff = subprocess.Popen(['ffmpeg', '-loglevel', 'error', *ff_in, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'],
                          stdout=subprocess.PIPE)
    procs.append(ff)
    n = int(SR * HOP_S) * 2
    try:
        while chunk := ff.stdout.read(n):
            yield np.frombuffer(chunk, np.int16).astype(np.float32) / 32768
    finally:
        for p in procs:
            p.terminate()


def dbfs(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)


class Detector:
    """Two-stage anti-spoof. Returns P(synthetic) for a window, or None for silence."""

    def __init__(self, device='mps'):
        from huggingface_hub import snapshot_download
        from transformers import pipeline
        from antideepfake import AntiDeepfake
        self.fast = AntiDeepfake(device)
        local = snapshot_download(STAGE2, local_dir=os.path.join(os.path.dirname(__file__), 'models', 'df_arena_500m'))
        self.confirm = pipeline('antispoofing', model=local, trust_remote_code=True, device=device)

    def score(self, short, long):
        if dbfs(short) < SPEECH_DBFS:
            return None, None
        s1 = self.fast.p_fake(short)
        if s1 < 0.5:
            return s1, None
        s2 = self.confirm(long)['all_scores']['spoof']
        return (s1 + s2) / 2, s2


class Risk:
    """Temporal smoothing: EMA for the gauge, k-of-n consensus for the level,
    so one odd window never raises an alarm on its own."""

    def __init__(self, alpha=0.4, n=5):
        self.alpha, self.ema, self.recent = alpha, 0.0, deque(maxlen=n)

    def update(self, p):
        self.ema = self.alpha * p + (1 - self.alpha) * self.ema
        self.recent.append(p)
        hot = sum(x >= 0.7 for x in self.recent)
        if hot >= 3:
            return 'alert'
        if hot >= 2 or self.ema >= 0.5:
            return 'suspicious'
        # never call a voice safe on less than 3 s of speech
        return 'safe' if len(self.recent) >= 3 else 'listening'


class Shield:
    """Runs the pipeline on a background thread and exposes a status snapshot."""

    def __init__(self, source, detector=None):
        self.source = source
        self.detector = detector or Detector()
        self.lock = threading.Lock()
        self.events = []  # alerts, newest last
        self._reset()

    def _reset(self):
        self.risk = Risk()
        self.status = {'level': 'listening', 'risk': 0.0, 'speech_seconds': 0, 'stage2': None, 'updated': time.time()}

    def start(self):
        threading.Thread(target=self.run, daemon=True).start()
        return self

    def run(self):
        buf = np.zeros(0, np.float32)
        for chunk in pcm_stream(self.source):
            buf = np.concatenate([buf, chunk])[-int(SR * CONFIRM_WIN_S):]
            p, s2 = self.detector.score(buf[-int(SR * WIN_S):], buf)
            with self.lock:
                st = self.status
                st['updated'] = time.time()
                if p is None:
                    continue
                prev = st['level']
                st['level'] = self.risk.update(p)
                st['risk'] = round(self.risk.ema, 3)
                st['stage2'] = None if s2 is None else round(s2, 3)
                st['speech_seconds'] += HOP_S
                if st['level'] == 'alert' and prev != 'alert':
                    self.events.append({'at': time.time(), 'risk': st['risk'], 'source': self.source})

    def snapshot(self):
        with self.lock:
            return dict(self.status), list(self.events)

    def clear(self):
        with self.lock:
            self._reset()
