"""Layer 4: conversational timing. Humans answer ~0.2 s after the other person stops (Stivers et al. 2009) and say
"haan / hmm" while listening; TTS-scripted callers and AI voice agents answer after 1-4 s and almost never backchannel.
Timing comes from WHO speaks WHEN, not from the spectrum, so the phone codec does not erase it.

Input: two 16 kHz mono streams, one per side of the call (scrcpy voice-call-uplink = our user,
voice-call-downlink = the caller). Feed 20 ms frames with Turns.push(user_frame, caller_frame).
"""
import numpy as np

FRAME_S = 0.02
SPEECH_DBFS = -42      # per-frame energy gate
HANG_S = 0.35          # silence shorter than this does not end a turn
MIN_TURN_S = 0.6       # user turn long enough to deserve a reply
BACKCHANNEL_MAX_S = 0.9


def _db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)


class Side:
    """Energy VAD with hangover; tracks the current talk spurt."""

    def __init__(self):
        self.talking, self.start, self.last_voice = False, 0.0, -1e9

    def update(self, frame, t):
        voiced = _db(frame) > SPEECH_DBFS
        ended = None
        if voiced:
            if not self.talking:
                self.talking, self.start = True, t
            self.last_voice = t
        elif self.talking and t - self.last_voice > HANG_S:
            self.talking = False
            ended = (self.start, self.last_voice + FRAME_S)
        return voiced, ended


class Turns:
    def __init__(self):
        self.t = 0.0
        self.user, self.caller = Side(), Side()
        self.waiting_since = None   # user finished a real turn at this time, caller has not replied yet
        self.gaps = []              # caller reply latencies (s)
        self.backchannels = 0       # caller spurts < BACKCHANNEL_MAX_S while the user is talking
        self.user_turns = 0

    def push(self, user_frame, caller_frame):
        self.t += FRAME_S
        _, u_end = self.user.update(user_frame, self.t)
        c_voiced, c_end = self.caller.update(caller_frame, self.t)
        if u_end and u_end[1] - u_end[0] >= MIN_TURN_S:
            self.user_turns += 1
            self.waiting_since = u_end[1]
        if c_voiced and self.waiting_since is not None and not self.user.talking:
            self.gaps.append(self.t - self.waiting_since)
            self.waiting_since = None
        if c_end and self.user.talking and c_end[1] - c_end[0] <= BACKCHANNEL_MAX_S:
            self.backchannels += 1

    def summary(self):
        g = np.array(self.gaps)
        median = float(np.median(g)) if len(g) else None
        # ponytail: hand-set thresholds from published human vs voice-agent medians; refit on recorded calls
        bot_like = bool(len(g) >= 3 and median > 1.0 and self.backchannels == 0)
        return {'replies': len(g), 'median_gap_s': None if median is None else round(float(median), 2),
                'gaps_s': [round(float(x), 2) for x in g[-8:]], 'backchannels': self.backchannels,
                'user_turns': self.user_turns, 'bot_like': bot_like}


if __name__ == '__main__':
    sr, n = 16000, int(16000 * FRAME_S)
    rng = np.random.default_rng(0)
    speech, quiet = lambda: 0.1 * rng.standard_normal(n), lambda: 0.0005 * rng.standard_normal(n)

    def simulate(gap_s, backchannel):
        tt = Turns()
        for _ in range(4):  # user talks 2 s, caller replies after gap_s and talks 2 s
            for k in range(100):
                caller = speech() if backchannel and 40 <= k < 55 else quiet()
                tt.push(speech(), caller)
            for _ in range(int(gap_s / FRAME_S)):
                tt.push(quiet(), quiet())
            for _ in range(100):
                tt.push(quiet(), speech())
            for _ in range(20):
                tt.push(quiet(), quiet())
        return tt.summary()

    human, bot = simulate(0.25, True), simulate(2.5, False)
    print('human', human); print('bot  ', bot)
    assert not human['bot_like'] and human['backchannels'] >= 3
    assert bot['bot_like'] and 2.0 < bot['median_gap_s'] < 3.2, bot
    print('ok')
