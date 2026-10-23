"""Payment Guard: a scam ends at the payment, not at the call. If a UPI app opens on the parent's phone during a call
(or within a few minutes after it), ask the real family member on Telegram before any money moves.

Reads the USB-connected Android phone over adb (no root): foreground app + telephony call state, every 1.5 s.
Fires at most once per call; the family's answer feeds the same fusion as verify_with_family.
"""
import re
import subprocess
import threading
import time

import verify

UPI_APPS = {
    'com.phonepe.app': 'PhonePe',
    'com.google.android.apps.nbu.paisa.user': 'Google Pay',
    'net.one97.paytm': 'Paytm',
    'in.org.npci.upiapp': 'BHIM',
    'in.amazon.mShop.android.shopping': 'Amazon Pay',
}
AFTER_CALL_S = 300   # scammers keep the parent on the line, or call back, so the window outlives the call
POLL_S = 1.5


def _adb(*args):
    try:
        return subprocess.run(['adb', 'shell', *args], capture_output=True, text=True, timeout=5).stdout
    except (OSError, subprocess.TimeoutExpired):
        return ''


def foreground(dump):
    m = re.search(r'(?:topResumedActivity|mResumedActivity)[^\n]*? ([\w.]+)/', dump)
    return m.group(1) if m else None


def in_call(dump):
    return any(int(x) != 0 for x in re.findall(r'mCallState=(\d)', dump))


class PayGuard:
    def __init__(self, shield, claimed_person='Ayush'):
        self.shield, self.person = shield, claimed_person
        self.last_call = 0.0
        self.state = None   # {'app', 'at', 'family'} once fired for this call

    def start(self):
        threading.Thread(target=self._loop, daemon=True).start()
        return self

    def reset(self):
        self.state = None

    def _loop(self):
        while True:
            now = time.time()
            status, _ = self.shield.snapshot()
            live = in_call(_adb('dumpsys', 'telephony.registry')) or now - status.get('updated', 0) < 5
            if live:
                self.last_call = now
            app = UPI_APPS.get(foreground(_adb('dumpsys', 'activity', 'activities')))
            if app and self.state is None and now - self.last_call < AFTER_CALL_S:
                self.state = {'app': app, 'at': now, 'family': 'asking'}
                threading.Thread(target=self._ask, args=(app,), daemon=True).start()
            time.sleep(POLL_S)

    def _ask(self, app):
        v = verify.verify(self.person, f'Papa ne call ke dauraan abhi {app} khola hai, paise bhejne wale hain')
        self.state = {**self.state, 'family': v['answer']}
        self.shield.set_family(v['answer'])


assert foreground('  topResumedActivity=ActivityRecord{1 u0 com.phonepe.app/.ui.MainActivity t5}') == 'com.phonepe.app'
assert in_call('mCallState=0\n mCallState=2') and not in_call('mCallState=0')

if __name__ == '__main__':
    print('foreground:', foreground(_adb('dumpsys', 'activity', 'activities')),
          '| in call:', in_call(_adb('dumpsys', 'telephony.registry')))
