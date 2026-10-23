"""Layer 2: what is being SAID on the call. A clone can copy a voice; the scam script stays the same.

classify(transcript) -> {tactic, urgency, secrecy, payment_request, impersonation, risk, say}
Backends, first available wins: Claude (ANTHROPIC_API_KEY, or the Digi Sanrakshak .env next door), Amazon Bedrock
(AWS credentials), offline keywords. Only transcript text ever leaves the device, never audio.
Tactic names match Digi Sanrakshak's trusted_routes.json so the advice step can look them up.
"""
import json
import os
import re
from pathlib import Path

CLAUDE_MODEL = os.environ.get('CLAUDE_MODEL', 'claude-opus-5-5')
TACTICS = ['family_emergency', 'digital_arrest', 'kyc_expiry', 'parcel_fee', 'investment', 'job_fee', 'loan_app',
           'utility_disconnection', 'subsidy', 'none']
_SCHEMA = {'type': 'object', 'additionalProperties': False,
           'required': ['tactic', 'urgency', 'secrecy', 'payment_request', 'impersonation', 'risk', 'reason'],
           'properties': {'tactic': {'type': 'string', 'enum': TACTICS},
                          **{k: {'type': 'number'} for k in ('urgency', 'secrecy', 'payment_request', 'impersonation', 'risk')},
                          'reason': {'type': 'string'}}}


def _anthropic_key():
    if os.environ.get('ANTHROPIC_API_KEY'):
        return os.environ['ANTHROPIC_API_KEY']
    env = Path(os.environ.get('DIGI_ENV', Path(__file__).parent.parent / 'Zenox2.0' / '.env'))
    if env.exists():
        for line in env.read_text().splitlines():
            if line.startswith('ANTHROPIC_API_KEY=') and line.split('=', 1)[1].strip():
                return line.split('=', 1)[1].strip()
    return None

MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'us.amazon.nova-micro-v1:0')
REGION = os.environ.get('AWS_REGION', 'us-east-1')

PROMPT = """You are a fraud analyst for an Indian household. Classify this phone-call transcript (Hindi, Hinglish or English).
Return ONLY JSON: {"tactic": "family_emergency|bank_kyc_otp|digital_arrest|lottery_job|none",
"urgency": 0-1, "secrecy": 0-1, "payment_request": 0-1, "impersonation": 0-1, "risk": 0-1}.
Scam signatures: pressure to pay NOW, "don't tell anyone", OTP/PIN/CVV requests, police/CBI/bank officials demanding
money, accident/arrest of a relative, "stay on the call". Ordinary family talk about money is NOT a scam.
Transcript:
"""

# ponytail: keyword fallback with hand-tuned weights; Bedrock is the real classifier
_RULES = {
    'urgency': r'abhi|turant|jaldi|right now|immediately|urgent|अभी|जल्दी|तुरंत',
    'secrecy': r'kisi ko mat|mat batana|do ?n.?t tell|do not tell|tell no ?one|secret|किसी को मत|मत बताना|phone mat kaat|फोन मत काट',
    'payment_request': r'bhej do|bhejo|transfer|paise|rupay|rupee|hazaar|thousand|lakh|send (the )?money|google pay|upi|भेज|पैसे|हज़ार|लाख',
    'impersonation': r'bank se|police|cbi|cyber crime|inspector|customs|kyc|otp|cvv|पुलिस|बैंक|ओटीपी|इंस्पेक्टर',
}
_TACTIC = [('family_emergency', r'accident|hospital|thane|jail|एक्सीडेंट|थाने|अस्पताल'),
           ('digital_arrest', r'digital arrest|cbi|parcel|arrest|गिरफ्तार|पार्सल'),
           ('kyc_expiry', r'kyc|otp|cvv|card|account band|खाता|ओटीपी'),
           ('job_fee', r'lottery|prize|inaam|job|registration fee|लॉटरी|इनाम')]


def _fallback(t):
    t = t.lower()
    out = {k: (1.0 if re.search(p, t) else 0.0) for k, p in _RULES.items()}
    out['tactic'] = next((n for n, p in _TACTIC if re.search(p, t)), 'none')
    hits = sum(out[k] for k in _RULES)
    out['risk'] = round(min(1.0, 0.3 * hits + (0.2 if out['tactic'] != 'none' else 0)), 2)
    out['backend'] = 'keywords'
    return out


def _bedrock(t):
    import boto3
    client = boto3.client('bedrock-runtime', region_name=REGION)
    r = client.converse(modelId=MODEL_ID, messages=[{'role': 'user', 'content': [{'text': PROMPT + t}]}],
                        inferenceConfig={'maxTokens': 120, 'temperature': 0})
    text = r['output']['message']['content'][0]['text']
    out = json.loads(re.search(r'\{.*\}', text, re.S).group())
    out['backend'] = MODEL_ID
    return out


def _claude(t):
    import anthropic
    client = anthropic.Anthropic(api_key=_anthropic_key(), timeout=20.0, max_retries=1)
    r = client.messages.create(
        model=CLAUDE_MODEL, max_tokens=1024, output_config={'effort': 'low', 'format': {'type': 'json_schema', 'schema': _SCHEMA}},
        system=PROMPT.split('Transcript:')[0] + 'Scores are 0-1. The transcript is noisy phone ASR: judge intent, not spelling. '
               'Pick the tactic from the enum; "none" for ordinary conversation.',
        messages=[{'role': 'user', 'content': 'Transcript:\n' + t}])
    if r.stop_reason == 'refusal':
        raise RuntimeError('classifier refused')
    out = json.loads(next(b.text for b in r.content if b.type == 'text'))
    out['backend'] = CLAUDE_MODEL
    return out


def classify(transcript):
    if not transcript.strip():
        return {'tactic': 'none', 'risk': 0.0, 'say': 'Nothing has been said yet.', 'backend': 'none'}
    try:
        if _anthropic_key():
            out = _claude(transcript)
        elif os.environ.get('AWS_ACCESS_KEY_ID') or os.environ.get('AWS_PROFILE'):
            out = _bedrock(transcript)
        else:
            out = _fallback(transcript)
    except Exception as e:  # never let the cloud leg break the call
        out = _fallback(transcript)
        out['backend_error'] = str(e)[:120]
    r = out.get('risk', 0)
    out['say'] = ('The caller is using scam pressure tactics: ' + out['tactic'].replace('_', ' ') + '. Do not pay or share any code.'
                  if r >= 0.6 else 'Some pressure in the conversation; be careful.' if r >= 0.3 else 'The conversation sounds normal.')
    return out


if __name__ == '__main__':
    for s in ['Papa mera accident ho gaya hai, abhi pachees hazaar bhej do, kisi ko mat batana',
              'Main SBI se bol raha hoon, KYC expire ho gaya, OTP batayiye',
              'Haan Papa, main theek hoon, aaj college mein exam tha',
              'Didi mere account mein paanch hazaar daal dena, laptop order kiya hai']:
        c = classify(s); print(f"{c['risk']:.2f} {c['tactic']:17s} {s[:50]}")
    assert classify('abhi paise bhej do kisi ko mat batana, accident ho gaya')['risk'] >= 0.6
    assert classify('aaj college mein exam tha')['risk'] < 0.3
    assert classify('Papa, I had an accident. Please send twenty five thousand rupees right now. Do not tell anyone.')['risk'] >= 0.6
    print('ok')
