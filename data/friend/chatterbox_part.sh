.venv-tts/bin/python - <<'PY'
import os, torch, torchaudio as ta, perth
perth.PerthImplicitWatermarker = perth.DummyWatermarker
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
m = ChatterboxMultilingualTTS.from_pretrained(device='mps' if torch.backends.mps.is_available() else 'cpu')
lines = {'e01': ('hi', 'पापा, मेरा एक्सीडेंट हो गया है, प्लीज़ अभी पच्चीस हज़ार भेज दो।'),
         'e02': ('hi', 'मम्मी, मैं थाने में हूँ, अभी पचास हज़ार चाहिए, किसी को मत बताना।'),
         'b01': ('hi', 'नमस्ते, मैं एसबीआई से बोल रहा हूँ, आपका केवाईसी एक्सपायर हो गया है, ओटीपी बताइए।'),
         'a01': ('hi', 'मैं मुंबई साइबर क्राइम से इंस्पेक्टर शर्मा बोल रहा हूँ, आपके नाम पर पार्सल पकड़ा गया है।'),
         'n01': ('hi', 'हाँ पापा, मैं ठीक हूँ, आज कॉलेज में एग्ज़ाम था, शाम को घर आऊँगा।'),
         'e04': ('en', "Dad, I'm in trouble, please send the money right now and don't tell anyone."),
         'b03': ('en', "This is your bank's fraud department. Share the one-time password to secure your account."),
         'n05': ('hi', 'पापा, बैंक वाले का कॉल आया था, मैंने बोला मैं खुद ब्रांच जाके बात करूँगा।')}
for k, (lang, text) in lines.items():
    wav = m.generate(text, language_id=lang, audio_prompt_path='data/friend/ref_10s.wav')
    ta.save(f'data/friend/clones/chatterbox/{k}.wav', wav, m.sr); print('chatterbox', k, flush=True)
PY
