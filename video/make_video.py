"""Assemble the <3 min submission video from slides, the screen recording and synthetic voice-over.

  .venv/bin/python video/make_video.py   -> video/voice_shield_demo.mp4
"""
import json
import os
import subprocess

from PIL import Image, ImageDraw, ImageFont

V = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(V)
B = os.path.join(V, 'build')
os.makedirs(B, exist_ok=True)
W, H, SR = 1920, 1080, 48000
BG, FG, DIM, RED, AMB, GRN, BLUE = '#0b0f14', '#e8eef5', '#8a97a8', '#ff3b4e', '#ffb020', '#2ee6a0', '#2ec4ff'
HEL = '/System/Library/Fonts/Helvetica.ttc'
UNI = '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
font = lambda size, f=HEL: ImageFont.truetype(f, size)


def run(*a):
    subprocess.run(a, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def dur(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                         capture_output=True, text=True).stdout
    return float(out)


def tts(name, text, voice, rate=None):
    aiff, wav = os.path.join(B, name + '.aiff'), os.path.join(B, name + '.wav')
    run('say', '-v', voice, *(['-r', str(rate)] if rate else []), '-o', aiff, text)
    run('ffmpeg', '-y', '-i', aiff, '-ar', str(SR), '-ac', '2', wav)
    return wav


# ---------- slides ----------
def slide(name, lines):
    """lines: list of (text, size, color, font_path, gap_after)."""
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    total = sum(s + g for _, s, _, _, g in lines)
    y = (H - total) // 2
    for text, size, color, fp, gap in lines:
        f = font(size, fp)
        w = d.textlength(text, font=f)
        d.text(((W - w) / 2, y), text, font=f, fill=color)
        y += size + gap
    p = os.path.join(B, name + '.png')
    im.save(p)
    return p


def table_slide(name):
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((160, 110), 'Measured on my own voice', font=font(64), fill=FG)
    d.text((160, 195), 'clones: F5-TTS + Chatterbox (Hindi + English) · detector: DF_Arena_500M', font=font(34), fill=DIM)
    rows = [('Channel', 'EER', 'Clones caught @1% false alarms', FG),
            ('Clean 16 kHz', '0.0 %', '100 %', GRN),
            ('G.711 landline codec', '1.2 %', '90 %', GRN),
            ('Opus narrowband', '8.9 %', '80 %', AMB),
            ('REAL VoLTE call, over the air', '≈ 35-40 %', '0 %', RED)]
    y = 310
    for i, (a, b, c, col) in enumerate(rows):
        f = font(44 if i else 36)
        d.text((160, y), a, font=f, fill=col if i else DIM)
        d.text((980, y), b, font=f, fill=col if i else DIM)
        d.text((1270, y), c, font=f, fill=col if i else DIM)
        y += 95
        if i == 0:
            d.line((160, y - 20, 1760, y - 20), fill='#2a3442', width=2)
    d.text((160, y + 40), 'So the voice score never decides alone: it only says "verify".', font=font(44), fill=FG)
    d.text((160, y + 110), 'Scam words, or a “No” from the real family member, raise the alert.', font=font(44, UNI), fill=FG)
    p = os.path.join(B, name + '.png')
    im.save(p)
    return p


def arch_slide(name):
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((160, 90), 'How it works', font=font(64), fill=FG)
    boxes = [(160, 260, 'Real SIM call', 'Oppo · scrcpy voice-call\nno root, both sides', BLUE),
             (620, 200, 'Voice layer', 'DF_Arena anti-spoof\n4 s windows, 3-of-5', AMB),
             (620, 400, 'Words layer', 'on-device Whisper +\nscam-pressure classifier', AMB),
             (1080, 260, 'MCP server', 'spec 2025-11-25\nStreamable HTTP · 4 tools', GRN),
             (1500, 160, 'Alexa+', '"Is this call real?"', BLUE),
             (1500, 400, 'Telegram', 'real son: Haan / Nahi', RED)]
    for x, y, t, sub, col in boxes:
        d.rounded_rectangle((x, y, x + 380, y + 170), 22, outline=col, width=4)
        d.text((x + 24, y + 20), t, font=font(40, UNI), fill=FG)
        d.multiline_text((x + 24, y + 80), sub, font=font(28, UNI), fill=DIM, spacing=8)
    for (x1, y1), (x2, y2) in [((540, 345), (620, 285)), ((540, 345), (620, 485)), ((1000, 285), (1080, 345)),
                               ((1000, 485), (1080, 345)), ((1460, 345), (1500, 245)), ((1460, 345), (1500, 485))]:
        d.line((x1, y1, x2, y2), fill='#5b6878', width=4)
    d.text((160, 660), 'Fusion: words or the family gate · voice boosts · a human decides', font=font(44), fill=FG)
    d.text((160, 740), 'Audio stays on the laptop. Only text could ever go to the cloud.', font=font(38), fill=DIM)
    d.text((160, 810), 'The web page is a real MCP client: initialize, tools/list, tools/call', font=font(38), fill=DIM)
    p = os.path.join(B, name + '.png')
    im.save(p)
    return p


def caption(name, text, color=FG):
    im = Image.new('RGBA', (W, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((60, 10, W - 60, 110), 18, fill=(0, 0, 0, 200))
    f = font(40, UNI)
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, 36), text, font=f, fill=color)
    p = os.path.join(B, name + '.png')
    im.save(p)
    return p


def still_clip(name, png, seconds, audio_parts):
    """audio_parts: list of (wav, start_s, volume)."""
    out = os.path.join(B, name + '.mp4')
    inputs, filt, labels = ['-loop', '1', '-t', f'{seconds:.2f}', '-i', png], [], []
    for i, (wav, start, vol) in enumerate(audio_parts):
        inputs += ['-i', wav]
        filt.append(f'[{i+1}]volume={vol},adelay={int(start*1000)}|{int(start*1000)}[a{i}]')
        labels.append(f'[a{i}]')
    filt.append(f'{"".join(labels)}amix=inputs={len(labels)}:normalize=0,apad,atrim=0:{seconds:.2f}[aout]')
    run('ffmpeg', '-y', *inputs, '-filter_complex', ';'.join(filt), '-map', '0:v', '-map', '[aout]',
        '-r', '30', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', str(SR), '-ac', '2', '-shortest', out)
    return out


# ---------- 1. hook ----------
clone = os.path.join(B, 'hook_clone.wav')
run('ffmpeg', '-y', '-i', os.path.join(ROOT, 'data/clones/chatterbox/e01.wav'), '-i', os.path.join(ROOT, 'data/clones/f5/e02.wav'),
    '-filter_complex', '[0]aresample=48000,apad=pad_dur=0.6[a];[1]aresample=48000[b];[a][b]concat=n=2:v=0:a=1,pan=stereo|c0=c0|c1=c0',
    '-ar', str(SR), clone)
n1 = tts('n_hook', "That was not me. It is an A I clone of my voice, made on this laptop from two minutes of audio. "
                   "Now imagine my father hearing it on a phone call.", 'Aman')
c_len = dur(clone)
hook_png = slide('s_hook', [('“Papa, mera accident ho gaya hai…', 70, FG, UNI, 18),
                            ('abhi pachaas hazaar bhej do, kisi ko mat batana.”', 70, FG, UNI, 70),
                            ('This voice is an AI clone of me.', 54, RED, HEL, 20),
                            ('Voice Shield  ·  Alexa+ MCP add-on', 40, DIM, HEL, 0)])
hook = still_clip('c_hook', hook_png, c_len + dur(n1) + 1.5, [(clone, 0.3, 1.0), (n1, c_len + 0.8, 1.0)])

# ---------- 2. problem ----------
n2 = tts('n_problem', "India lost over twenty two thousand crore rupees to cyber fraud in 2025. "
                      "Every police and bank advisory says the same thing: don't trust the voice, call the person back. "
                      "In a panic, nobody does. Voice Shield does it for you, through Alexa.", 'Aman')
prob_png = slide('s_problem', [('₹22,495 crore', 120, RED, UNI, 20), ('lost to cyber fraud in India, 2025', 48, DIM, HEL, 80),
                               ('“Don\'t trust the voice. Call them back.”', 60, FG, UNI, 20),
                               ('— FBI, FTC, RBI, Indian police advisories', 36, DIM, UNI, 0)])
prob = still_clip('c_problem', prob_png, dur(n2) + 1.2, [(n2, 0.4, 1.0)])

# ---------- 3. live demo (screen recording) ----------
SCREEN = os.path.join(V, 'screen.mp4')
t0 = float(open(os.path.join(V, 't0.txt')).read())
events = [{**e, 'rt': e['t'] - t0} for e in json.load(open(os.path.join(V, 'events.json')))]
CUT_IN, CUT_OUT = 13.0, 62.0
demo_len = CUT_OUT - CUT_IN
lines = []  # (wav, start in demo clip, volume)
spoken = set()
for i, e in enumerate(events):
    if not (CUT_IN <= e['rt'] <= CUT_OUT) or e['name'] not in ('speak', 'user'):
        continue
    key = (e['name'], e['text'])
    if key in spoken:
        continue
    spoken.add(key)
    txt = e['text']
    if e['name'] == 'user':
        voice = 'Rishi'
    else:
        voice = 'Lekha' if any(w in txt for w in ('Saavdhaan', 'Chetavani', 'Theek hai')) else 'Tara'
    wav = tts(f'l{i}', txt, voice, rate=185)
    lines.append((wav, e['rt'] - CUT_IN, 1.0))
# real call audio, quiet, under the Alexa lines (it was replayed from the real VoLTE capture)
call = os.path.join(B, 'call.wav')
run('ffmpeg', '-y', '-i', os.path.join(V, 'demo_input.wav'), '-ar', str(SR), '-ac', '2', call)
AUDIO_START_RT = -4.5  # file playback began ~4.5 s before the recording (server ready -> window open -> 3 s)
lines.append((call, max(0.0, AUDIO_START_RT - CUT_IN), 0.45))

caps = [(0, 9, caption('cap1', 'Audio: clones of my voice, captured from a REAL VoLTE call on the Oppo (scrcpy, no root)')),
        (9, 22, caption('cap2', 'Voice layer: "suspicious" → Alexa warns in Hindi; user asks "is this call real?"', AMB)),
        (22, 33, caption('cap3', 'Rohan\'s real phone (Telegram): “Kya aap abhi ye call kar rahe ho?” → he taps “Nahi, main nahi”', RED)),
        (33, demo_len, caption('cap4', 'Family denies → ALERT: "This is a scam. Hang up, do not pay."', RED))]
demo = os.path.join(B, 'c_demo.mp4')
inp = ['-ss', f'{CUT_IN}', '-t', f'{demo_len}', '-i', SCREEN]
for _, _, p in caps:
    inp += ['-i', p]
inp += ['-i', os.path.join(V, 'telegram.png')]  # Rohan's real Telegram screen from this run
for wav, _, _ in lines:
    inp += ['-i', wav]
# crop menu bar, tab strip, automation banner and dock; keep 16:9
vf = ['[0]crop=1560:878:180:232,scale=1920:1080,setsar=1[v0]']
for k, (a, b, _) in enumerate(caps):
    vf.append(f"[v{k}][{k+1}]overlay=0:H-150:enable='between(t,{a},{b})'[v{k+1}]")
TG = len(caps) + 1
tg_in, tg_out = 37.5 - CUT_IN - 1, demo_len  # from the question until the end
vf.append(f"[{TG}]scale=-2:900,pad=iw+12:ih+12:6:6:color=#2ec4ff[tg]")
vf.append(f"[v{len(caps)}][tg]overlay=W-w-70:40:enable='between(t,{tg_in},{tg_out})'[vtg]")
na = len(caps) + 2
af, labels = [], []
for j, (_, start, vol) in enumerate(lines):
    af.append(f'[{na+j}]volume={vol},adelay={int(start*1000)}|{int(start*1000)}[x{j}]')
    labels.append(f'[x{j}]')
af.append(f'{"".join(labels)}amix=inputs={len(labels)}:normalize=0,atrim=0:{demo_len}[aout]')
run('ffmpeg', '-y', *inp, '-filter_complex', ';'.join(vf + af), '-map', '[vtg]', '-map', '[aout]',
    '-r', '30', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', str(SR), '-ac', '2', '-t', f'{demo_len}', demo)

# ---------- 4. how ----------
n4 = tts('n_how', "Here is how. Voice Shield captures both sides of a real SIM call from an Android phone, without root. "
                  "A voice layer scores every four seconds for synthetic speech. A words layer transcribes on device and looks for scam pressure: "
                  "urgent money, O T P, keep it secret. Both feed a self hosted M C P server, spec 2025 11 25, over streamable H T T P, "
                  "which Alexa plus calls. And when the caller claims to be family, Alexa asks the real person, on their own phone.", 'Aman')
how = still_clip('c_how', arch_slide('s_how'), dur(n4) + 1.0, [(n4, 0.4, 1.0)])

# ---------- 5. honest numbers ----------
n5 = tts('n_numbers', "We measured it on my own voice. On simulated phone codecs the detector catches the clones. "
                      "But over a real phone call, played over the air, it falls to around forty percent error. "
                      "So we designed around that: the voice score alone only says verify. "
                      "Scam words, or a no from the real family member, raise the alert. A clone can copy a voice. It cannot press the button on my phone.", 'Aman')
nums = still_clip('c_numbers', table_slide('s_numbers'), dur(n5) + 1.0, [(n5, 0.4, 1.0)])

# ---------- 6. close ----------
n6 = tts('n_close', "Voice Shield is open source under M I T, runs on a laptop today, and belongs inside every Echo tomorrow.", 'Aman')
close_png = slide('s_close', [('Voice Shield', 110, FG, HEL, 30), ('“Alexa, is this really my son calling?”', 52, BLUE, UNI, 70),
                              ('github.com/shaunmortal/voice-shield', 48, FG, HEL, 20),
                              ('MIT · MCP 2025-11-25 · Streamable HTTP · Alexa+ track', 36, DIM, HEL, 0)])
close = still_clip('c_close', close_png, dur(n6) + 2.0, [(n6, 0.4, 1.0)])

# ---------- concat ----------
lst = os.path.join(B, 'list.txt')
with open(lst, 'w') as f:
    for c in (hook, prob, demo, how, nums, close):
        f.write(f"file '{c}'\n")
out = os.path.join(V, 'voice_shield_demo.mp4')
run('ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', '30',
    '-c:a', 'aac', '-ar', str(SR), '-ac', '2', '-movflags', '+faststart', out)
print(f'{out}  {dur(out):.1f}s  (hook {dur(hook):.0f}, problem {dur(prob):.0f}, demo {dur(demo):.0f}, how {dur(how):.0f}, numbers {dur(nums):.0f}, close {dur(close):.0f})')
