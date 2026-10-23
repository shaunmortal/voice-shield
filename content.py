"""Layer 2: what is being SAID on the call. A clone can copy a voice; the scam script stays the same.

classify(transcript) -> {tactic, urgency, secrecy, payment_request, impersonation, risk, say}
Backend: Amazon Bedrock (Nova Micro via the Converse API) when AWS credentials are present, otherwise a
keyword fallback so the demo runs offline. Only transcript text ever leaves the device, never audio.
"""
import json
import os
import re

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
           ('bank_kyc_otp', r'kyc|otp|cvv|card|account band|खाता|ओटीपी'),
           ('lottery_job', r'lottery|prize|inaam|job|registration fee|लॉटरी|इनाम')]


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


def classify(transcript):
    if not transcript.strip():
        return {'tactic': 'none', 'risk': 0.0, 'say': 'Nothing has been said yet.', 'backend': 'none'}
    try:
        out = _bedrock(transcript) if os.environ.get('AWS_ACCESS_KEY_ID') or os.environ.get('AWS_PROFILE') else _fallback(transcript)
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
