"""Self-check: synthetic speech must alert, silence must not. Run: .venv/bin/python test_engine.py"""
import os, subprocess, tempfile, time
from engine import Detector, Risk, Shield

r = Risk()
assert [r.update(p) for p in (0.9, 0.1, 0.9)][-1] != 'alert'          # 2 hot windows: not an alarm yet
r = Risk(); levels = [r.update(0.9) for _ in range(3)]
assert levels[-1] == 'alert', levels

d = tempfile.mkdtemp()
tts = os.path.join(d, 'tts.aiff')
subprocess.run(['say', '-o', tts, 'Papa, I had an accident. Please send twenty five thousand rupees right now. '
                'Do not tell anyone, I will explain later. Please hurry, the hospital is asking for money.'], check=True)
silence = os.path.join(d, 'silence.wav')
subprocess.run(['ffmpeg', '-loglevel', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=16000:cl=mono', '-t', '6', silence], check=True)

det = Detector()
for path, want in ((tts, 'alert'), (silence, 'listening')):
    s = Shield(f'file:{path}', det)
    s.run()  # file sources end, so run synchronously
    status, events = s.snapshot()
    assert status['level'] == want, (path, status)
    print(os.path.basename(path), status)
print('ok')
