"""Measure the detector on OUR data: bona fide = the consenting speaker, spoof = clones of that speaker,
each passed through simulated telephone channels (and, when present, the real recorded call).

  .venv/bin/python eval.py            # builds data/eval/<condition>/... then prints EER / TPR@1%FPR per condition x tool
  .venv/bin/python eval.py --model antideepfake   # compare the rejected model

Layout expected:
  data/bonafide/*.wav             real speech of the speaker (any sr)
  data/clones/<tool>/*.wav        clones of the same speaker, one folder per tool
  data/realcall/<label>/*.wav     optional: clips recorded through the live phone call (label = bonafide | <tool>)
"""
import argparse
import glob
import os
import subprocess
import sys

import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.abspath(__file__))
D = lambda *p: os.path.join(ROOT, 'data', *p)
WIN = 4 * 16000

# name -> ffmpeg filter/codec chain producing 16 kHz mono wav. AMR-NB needs libopencore-amr, absent from brew ffmpeg.
CONDITIONS = {
    'clean': ['-ar', '16000', '-ac', '1'],
    'band': ['-af', 'highpass=f=300,lowpass=f=3400', '-ar', '16000', '-ac', '1'],
    'g711': None,   # built in two passes below
    'opus_nb': None,
}


def convert(src, dst, cond):
    if os.path.exists(dst):
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    base = ['ffmpeg', '-loglevel', 'error', '-y', '-i', src]
    if cond in ('clean', 'band'):
        subprocess.run(base + CONDITIONS[cond] + [dst], check=True)
        return
    band = dst + '.band.wav'
    subprocess.run(base + ['-af', 'highpass=f=300,lowpass=f=3400', '-ar', '8000', '-ac', '1', band], check=True)
    if cond == 'g711':
        mid = dst + '.ul'
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', band, '-c:a', 'pcm_mulaw', '-f', 'mulaw', mid], check=True)
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'mulaw', '-ar', '8000', '-ac', '1', '-i', mid, '-ar', '16000', dst], check=True)
    elif cond == 'opus_nb':
        mid = dst + '.ogg'
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', band, '-c:a', 'libopus', '-b:a', '12k', '-application', 'voip', mid], check=True)
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', mid, '-ar', '16000', '-ac', '1', dst], check=True)
    for f in (band, mid):
        os.remove(f)


def windows(path):
    a, sr = sf.read(path, dtype='float32')
    if a.ndim > 1:
        a = a.mean(1)
    assert sr == 16000, path
    from engine import dbfs, SPEECH_DBFS
    ws = [a] if len(a) <= WIN else [a[i:i + WIN] for i in range(0, len(a) - WIN + 1, WIN // 2)]
    return [w for w in ws if dbfs(w) >= SPEECH_DBFS]  # same silence gate as the live engine


def eer(scores, labels):
    """labels: 1 = spoof. Returns (EER, TPR at 1% FPR)."""
    s, y = np.asarray(scores), np.asarray(labels)
    ths = np.unique(s)
    fpr = np.array([(s[y == 0] >= t).mean() for t in ths])
    tpr = np.array([(s[y == 1] >= t).mean() for t in ths])
    fnr = 1 - tpr
    i = np.argmin(np.abs(fpr - fnr))
    ok = fpr <= 0.01
    return float((fpr[i] + fnr[i]) / 2), float(tpr[ok].max() if ok.any() else 0.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default='df_arena', choices=['df_arena', 'antideepfake'])
    args = ap.parse_args()
    if args.model == 'df_arena':
        from engine import Detector
        p_fake = Detector().p_fake
    else:
        from antideepfake import AntiDeepfake
        p_fake = AntiDeepfake().p_fake

    sources = [(f, 'bonafide') for f in glob.glob(D('bonafide', '*.wav'))]
    for tool in sorted(os.listdir(D('clones'))):
        sources += [(f, tool) for f in glob.glob(D('clones', tool, '*.wav'))]
    if not sources:
        sys.exit('no data under data/bonafide or data/clones')

    rows = []  # (condition, tool, score)
    for cond in CONDITIONS:
        for src, tool in sources:
            dst = D('eval', cond, tool, os.path.basename(src))
            convert(src, dst, cond)
            for w in windows(dst):
                rows.append((cond, tool, p_fake(w)))
    for label in glob.glob(D('realcall', '*')):
        tool = os.path.basename(label)
        for f in glob.glob(os.path.join(label, '*.wav')):
            for w in windows(f):
                rows.append(('realcall', tool, p_fake(w)))

    conds = sorted({r[0] for r in rows}, key=lambda c: (c != 'clean', c))
    tools = sorted({r[1] for r in rows} - {'bonafide'})
    print(f'\nmodel={args.model}  windows: ' + ', '.join(f'{t}={sum(r[1]==t for r in rows)}' for t in ['bonafide'] + tools))
    print(f'{"condition":10s} {"tool":12s} {"EER":>7s} {"TPR@1%FPR":>10s} {"mean p_fake(bona)":>18s} {"mean p_fake(spoof)":>19s}')
    for cond in conds:
        bona = [r[2] for r in rows if r[0] == cond and r[1] == 'bonafide']
        if not bona:
            continue
        for tool in tools + ['ALL']:
            spoof = [r[2] for r in rows if r[0] == cond and (r[1] == tool or (tool == 'ALL' and r[1] != 'bonafide'))]
            if not spoof:
                continue
            e, t1 = eer(bona + spoof, [0] * len(bona) + [1] * len(spoof))
            print(f'{cond:10s} {tool:12s} {e*100:6.1f}% {t1*100:9.1f}% {np.mean(bona):18.3f} {np.mean(spoof):19.3f}')


if __name__ == '__main__':
    main()
