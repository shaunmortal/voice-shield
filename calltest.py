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
    print('recording started. Put the OTHER phone on a call to the Oppo, hold it next to this laptop speaker,')
    input('then press Enter to play the playlist... ')
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


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'run':
        run()
    elif len(sys.argv) > 1 and sys.argv[1] == 'split':
        split(os.path.join(OUT, 'call.mka'), json.load(open(os.path.join(OUT, 'log.json'))))
    else:
        print(__doc__)
