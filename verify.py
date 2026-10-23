"""Human verification over Telegram: ask the real family member "are you calling right now?".

Uses only the Bot API over urllib (no SDK). Needs TELEGRAM_BOT_TOKEN and TELEGRAM_FAMILY_CHAT_ID in .env.
A clone can copy a voice; it cannot press the button on the real person's phone.
"""
import json
import os
import time
import urllib.parse
import urllib.request

ENV = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(ENV):
    for line in open(ENV):
        k, _, v = line.strip().partition('=')
        if k and v:
            os.environ.setdefault(k, v)

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT = os.environ.get('TELEGRAM_FAMILY_CHAT_ID')
_offset = 0


def _api(method, **params):
    data = urllib.parse.urlencode({k: json.dumps(v) if isinstance(v, dict) else v for k, v in params.items()}).encode()
    with urllib.request.urlopen(f'https://api.telegram.org/bot{TOKEN}/{method}', data, timeout=10) as r:
        return json.load(r)['result']


def ask(claimed_person, reason):
    """Send the yes/no question. Returns the message id used to match the answer."""
    text = (f'⚠️ Voice Shield\n\nGhar par ek call aayi hai jisme caller khud ko *{claimed_person}* bata raha hai.\n'
            f'Shak ki wajah: {reason}\n\n*Kya aap abhi ye call kar rahe ho?*')
    # reply keyboard: the tap becomes a visible chat message at once (inline buttons spin until the bot answers)
    kb = {'keyboard': [[{'text': '✅ Haan, main hi hoon'}, {'text': '❌ Nahi, main nahi'}]],
          'one_time_keyboard': True, 'resize_keyboard': True}
    return _api('sendMessage', chat_id=CHAT, text=text, parse_mode='Markdown', reply_markup=kb)['message_id']


def parse(text):
    t = text.lower()
    if '❌' in t or any(w in t for w in ('nahi', 'nahin', 'no', 'नहीं')):
        return 'no'
    if '✅' in t or any(w in t for w in ('haan', 'han', 'yes', 'हाँ', 'हां')):
        return 'yes'
    return None


def wait_answer(message_id, timeout=25):
    """Poll for the button press on that message. Returns 'yes', 'no' or None on timeout."""
    global _offset
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:  # short polling: a hung long-poll once swallowed the answer
            updates = _api('getUpdates', offset=_offset, timeout=0)
        except OSError:
            updates = []
        time.sleep(0.7)
        for u in updates:
            _offset = u['update_id'] + 1
            m = u.get('message') or {}
            if str(m.get('chat', {}).get('id')) != str(CHAT) or m.get('message_id', 0) <= message_id:
                continue
            answer = parse(m.get('text', ''))
            if answer:
                try:  # cosmetic: confirm and hide the keyboard
                    _api('sendMessage', chat_id=CHAT, text='Shukriya. Papa ko bata diya. 🙏', reply_markup={'remove_keyboard': True})
                except OSError:
                    pass
                return answer
    return None


def verify(claimed_person, reason, timeout=45):
    if not (TOKEN and CHAT):
        return {'answer': 'unconfigured', 'say': 'Family verification is not set up on this device.'}
    try:
        answer = wait_answer(ask(claimed_person, reason), timeout)
    except OSError as e:  # Telegram unreachable: fall back to the advice every police advisory gives
        return {'answer': 'error', 'say': f'I could not reach {claimed_person} ({e}). Hang up and call them back on their saved number before sending anything.'}
    say = {
        'yes': f'{claimed_person} confirmed on their own phone that they are calling you. This call is genuine.',
        'no': f'{claimed_person} says they are NOT calling you. This is a scam. Hang up now and do not send anything.',
        None: f'{claimed_person} has not answered yet. Do not send money until they confirm. Call them back on their saved number.',
    }[answer]
    return {'answer': answer or 'no_answer', 'say': say}


assert parse('❌ Nahi, main nahi') == 'no' and parse('✅ Haan, main hi hoon') == 'yes' and parse('nahi') == 'no' and parse('ok') is None


if __name__ == '__main__':
    print(verify('Ayush', 'awaaz AI-generated lag rahi hai aur paise maang raha hai', timeout=60))
