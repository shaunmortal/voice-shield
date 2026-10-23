"""Real-call test set. Records the Oppo's live SIM call with scrcpy while the laptop speaker plays, next to the
OTHER phone, a playlist of real recordings and clones. Afterwards the recording is cut by the logged timestamps
into data/realcall/<label>/*.wav, which eval.py picks up as the 'realcall' condition.

  .venv/bin/python calltest.py run      # start recording, wait for Enter, play the playlist, stop, split
"""
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
D = lambda *p: os.path.join(ROOT, 'data', *p)
OUT = D('calltest')
GAP = 1.5  # seconds of silence between clips

PLAYLIST = [  # (label, path, max seconds)
    ('bonafide', D('bonafide', 'ref1_a.wav'), 40),
    ('f5', D('clones', 'f5', 'e04.wav'), 10),
    ('chatterbox', D('clones', 'chatterbox', 'e01.wav'), 12),
    ('f5', D('clones', 'f5', 'e02.wav'), 10),
    ('chatterbox', D('clones', 'chatterbox', 'a01.wav'), 12),
    ('bonafide', D('bonafide', 'ref2_a.wav'), 40),
    ('f5', D('clones', 'f5', 'b03.wav'), 10),
    ('chatterbox', D('clones', 'chatterbox', 'e02.wav'), 12),
    ('chatterbox', D('clones', 'chatterbox', 'e04.wav'), 12),
    ('bonafide', D('bonafide', 'ref1_b.wav'), 30),
]


def run():
    os.makedirs(OUT, exist_ok=True)
    rec = os.path.join(OUT, 'call.mka')
    if os.path.exists(rec):
        os.remove(rec)
    scr = subprocess.Popen(['scrcpy', '--no-video', '--no-window', '--no-playback', '--audio-source=voice-call',
                            f'--record={rec}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t0 = time.time()
    print('recording started. Put the OTHER phone on a call to the Oppo and hold it next to this laptop speaker.')
    for i in range(30, 0, -5):
        print(f'playlist starts in {i}s'); time.sleep(5)
    log = []
    for label, path, limit in PLAYLIST:
        start = time.time() - t0
        print(f'{start:6.1f}s  {label:10s} {os.path.basename(path)}')
        subprocess.run(['afplay', '-t', str(limit), path])
        log.append({'label': label, 'file': os.path.basename(path), 'start': start, 'end': time.time() - t0})
        time.sleep(GAP)
    time.sleep(2)
    scr.terminate(); scr.wait()
    json.dump(log, open(os.path.join(OUT, 'log.json'), 'w'), indent=1)
    split(rec, log)


def split(rec, log):
    for i, e in enumerate(log):
        d = D('realcall', e['label']); os.makedirs(d, exist_ok=True)
        dst = os.path.join(d, f"{i:02d}_{e['file']}")
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', f"{e['start'] + 0.3:.2f}", '-to', f"{e['end'] - 0.2:.2f}",
                        '-i', rec, '-ar', '16000', '-ac', '1', dst], check=True)
    print('split into data/realcall/; now run: .venv/bin/python eval.py')


def build():
    """One file the remote friend plays once: beep + clip + gap, so the recording can be cut by beep positions."""
    import numpy as np, soundfile as sf
    sr = 16000
    beep = (0.4 * np.sin(2 * np.pi * 1000 * np.arange(int(0.4 * sr)) / sr)).astype('float32')
    gap = np.zeros(int(GAP * sr), 'float32')
    parts, log, t = [np.zeros(sr, 'float32')], [], 1.0
    for label, path, limit in PLAYLIST:
        a, asr = sf.read(path, dtype='float32')
        if a.ndim > 1: a = a.mean(1)
        if asr != sr:
            n = int(len(a) * sr / asr); a = np.interp(np.linspace(0, len(a) - 1, n), np.arange(len(a)), a).astype('float32')
        a = a[:limit * sr]; a = a / (np.abs(a).max() + 1e-6) * 0.8
        parts += [beep, gap, a, gap]; t += len(beep) / sr + GAP
        log.append({'label': label, 'file': os.path.basename(path), 'start': t, 'end': t + len(a) / sr}); t += len(a) / sr + GAP
    os.makedirs(OUT, exist_ok=True)
    sf.write(os.path.join(OUT, 'playlist.wav'), np.concatenate(parts), sr)
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', os.path.join(OUT, 'playlist.wav'), '-b:a', '128k', os.path.join(OUT, 'playlist.m4a')], check=True)
    json.dump(log, open(os.path.join(OUT, 'playlist.json'), 'w'), indent=1)
    print(f'playlist {t:.0f}s -> data/calltest/playlist.m4a')


def record():
    """Just record the Oppo call until Ctrl-C / time limit; the friend plays playlist.m4a on their side."""
    os.makedirs(OUT, exist_ok=True)
    rec = os.path.join(OUT, 'call.mka')
    subprocess.run(['scrcpy', '--no-video', '--no-window', '--no-playback', '--audio-source=voice-call',
                    '--time-limit=420', f'--record={rec}'])


def split_remote(rec=None):
    """Find the first 1 kHz beep in the recording, then cut by playlist.json offsets."""
    import numpy as np, soundfile as sf
    rec = rec or os.path.join(OUT, 'call.mka'); wav = rec + '.16k.wav'
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', rec, '-ar', '16000', '-ac', '1', wav], check=True)
    a, sr = sf.read(wav, dtype='float32')
    # 1 kHz energy via Goertzel on 50 ms frames
    n = int(0.05 * sr); w = np.exp(-2j * np.pi * 1000 * np.arange(n) / sr)
    frames = a[:len(a) // n * n].reshape(-1, n)
    tone = np.abs(frames @ w) / (np.sqrt((frames ** 2).sum(1)) * np.sqrt(n) + 1e-6)
    hot = np.where(tone > 0.6)[0]
    assert len(hot), 'no beep found'
    first = hot[0] * n / sr
    log = json.load(open(os.path.join(OUT, 'playlist.json')))
    offset = first - (1.0)  # playlist has 1 s lead-in before the first beep
    print(f'first beep at {first:.2f}s in recording -> offset {offset:.2f}s')
    for e in log:
        e['start'] += offset; e['end'] += offset
    split(rec, log)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'build': build()
    elif cmd == 'record': record()
    elif cmd == 'split-remote': split_remote(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == 'run':
        run()
    elif len(sys.argv) > 1 and sys.argv[1] == 'split':
        split(os.path.join(OUT, 'call.mka'), json.load(open(os.path.join(OUT, 'log.json'))))
    else:
        print(__doc__)
