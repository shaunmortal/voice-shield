"""Voice Shield MCP server (spec 2025-11-25, Streamable HTTP at /mcp) + simulated Alexa+ page at /.

  .venv/bin/python server.py --source phone        # live SIM call from the USB-connected Android phone
  .venv/bin/python server.py --source mic          # call on speakerphone, laptop mic listens
  .venv/bin/python server.py --source file:x.wav   # replay a clip
"""
import argparse
import json
import os
import time
from pathlib import Path
from typing import TypedDict

import uvicorn
from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations
from starlette.responses import FileResponse, JSONResponse

from engine import Shield
import verify
from payguard import PayGuard

READ_ONLY = ToolAnnotations(readOnlyHint=True)


class Words(TypedDict):
    transcript: str
    tactic: str  # family_emergency | bank_kyc_otp | digital_arrest | lottery_job | none
    risk: float


class Timing(TypedDict):
    replies: int
    median_gap_s: float | None
    backchannels: int
    bot_like: bool


class CallStatus(TypedDict):
    level: str  # fused: listening | safe | suspicious | alert
    audio_level: str  # voice layer alone
    risk: float  # smoothed P(AI-generated voice), 0-1
    words: Words | None  # scam-language layer on the live transcript
    timing: Timing | None  # who-speaks-when: caller reply gaps and backchannels
    speech_seconds: float
    audio_live: bool
    payment: str | None  # Payment Guard: UPI app opened during/after the call -> family answer (asking|yes|no|no_answer)
    say: str  # a sentence the assistant can speak as-is


class Alert(TypedDict):
    time: str
    risk: float
    source: str
mcp = MCPServer(
    'voice-shield',
    version='0.1.0',
    instructions='Voice Shield listens to the phone call happening in this home and estimates whether the caller '
                 'voice is AI-generated (cloned). Use get_call_status when the user asks if a call is safe, real, '
                 'or a scam. Never say a voice is definitely fake: report the risk and tell the user to verify the '
                 'caller another way before sending money.',
)
shield: Shield | None = None
guard: PayGuard | None = None

SAY = {
    'listening': 'I am listening to the call, but I have not heard enough speech yet.',
    'safe': 'The caller voice sounds like a real human so far. Still, never share an OTP or send money under pressure.',
    'suspicious': 'Some parts of the caller voice look machine-generated. Do not send money yet. '
                  'Hang up and call the person back on the number you have saved.',
    'alert': 'Warning: the caller voice is very likely AI-generated. This may be a voice-cloning scam. '
             'Do not send money or share any OTP. Hang up and call the real person on their saved number.',
}


@mcp.tool(annotations=READ_ONLY, structured_output=True)
def get_call_status() -> CallStatus:
    """Live risk that the voice on the current phone call is AI-generated or cloned.
    Use for questions like 'Is this call real?', 'Is my son really calling?', 'Is this a scam?'."""
    status, _ = shield.snapshot()
    stale = time.time() - status['updated'] > 5
    level = status['level']  # keep the verdict after audio stops; reset_call() starts the next call
    w = status['words']
    say = SAY[level]
    if status.get('family') == 'no':
        say = 'Your family member says they are not calling. Treat this as a scam: hang up, do not pay.'
    elif status.get('family') == 'yes':
        say = 'Your family member confirmed it is them.'
    if w and w.get('risk', 0) >= 0.6:
        say = w['say'] + ' ' + say
    pay = guard.state if guard else None
    if pay and pay['family'] in ('asking', 'no_answer'):
        say = f"Wait: {pay['app']} was just opened during this call. I have asked your family member to confirm first. " + say
    return {'level': level, 'audio_level': status['audio_level'], 'risk': status['risk'], 'speech_seconds': status['speech_seconds'],
            'audio_live': not stale, 'say': say,
            'payment': None if not pay else f"{pay['app']} opened; family: {pay['family']}",
            'words': None if not w else {'transcript': w['transcript'], 'tactic': w['tactic'], 'risk': w['risk']},
            'timing': None if not status.get('timing') else {k: status['timing'][k] for k in ('replies', 'median_gap_s', 'backchannels', 'bot_like')}}


@mcp.tool(annotations=READ_ONLY, structured_output=True)
def get_alert_history(limit: int = 5) -> list[Alert]:
    """Most recent calls where a likely AI-generated voice was detected, newest first."""
    _, events = shield.snapshot()
    return [{'time': time.strftime('%d %b %H:%M', time.localtime(e['at'])), 'risk': e['risk'], 'source': e['source']}
            for e in reversed(events[-limit:])]


class Verification(TypedDict):
    answer: str  # yes | no | no_answer | unconfigured
    say: str


@mcp.tool(structured_output=True)
def verify_with_family(claimed_person: str, reason: str = 'the caller is asking for money urgently') -> Verification:
    """Ask the REAL family member, on their own phone, whether they are the one calling right now.
    Use when the caller claims to be a relative and asks for money, an OTP, or secrecy, whatever the voice score says.
    Waits up to 45 seconds for their answer."""
    v = verify.verify(claimed_person, reason)
    shield.set_family(v['answer'])
    return v


DATA = Path(__file__).parent / 'data'
ROUTES = json.loads((DATA / 'trusted_routes.json').read_text())   # from Digi Sanrakshak (MIT), authority-sourced
ACTION_TEXT = json.loads((DATA / 'action_text.json').read_text())


class Advice(TypedDict):
    tactic: str
    steps: list[str]
    say: str


@mcp.tool(annotations=READ_ONLY, structured_output=True)
def what_should_i_do(money_sent: bool = False, shared_otp_or_pin: bool = False, language: str = 'en') -> Advice:
    """What to do right now about the current suspicious call, in order. Steps are fixed text from RBI / I4C (1930,
    cybercrime.gov.in) guidance, not generated. Set money_sent or shared_otp_or_pin if the user already did that.
    language: 'en' or 'hi'."""
    lang = 'hi' if language.startswith('hi') else 'en'
    status, _ = shield.snapshot()
    tactic = 'family_emergency' if status.get('family') == 'no' else ((status.get('words') or {}).get('tactic') or 'default')
    routes, T = ROUTES.get(lang, ROUTES['en']), ACTION_TEXT[lang]
    if money_sent:
        steps = T['money']
    elif shared_otp_or_pin:
        steps = T['creds'] + [routes.get(tactic, routes['default'])]
    else:
        steps = [routes.get(tactic, routes['default'])] + T['do_not'][1:3]
    return {'tactic': tactic, 'steps': steps, 'say': ' '.join(steps[:2])}


@mcp.tool()
def reset_call() -> str:
    """Clear the live risk when a call ends, so the next call starts fresh. Alert history is kept."""
    shield.clear()
    if guard:
        guard.reset()
    return 'Ready for the next call.'


WEB = Path(__file__).parent / 'web'


@mcp.custom_route('/', methods=['GET'])
async def index(_):
    return FileResponse(WEB / 'index.html')


@mcp.custom_route('/api/status', methods=['GET'])
async def api_status(_):
    status, events = shield.snapshot()
    return JSONResponse({**get_call_status(), 'stage2': status['stage2'], 'alerts': len(events)})


EVENTS = []  # demo timeline from the web client (used to place the spoken replies when editing the video)


@mcp.custom_route('/api/event', methods=['POST', 'GET'])
async def api_event(request):
    if request.method == 'POST':
        EVENTS.append({'t': time.time(), **(await request.json())})
    return JSONResponse(EVENTS)


@mcp.custom_route('/api/assistant', methods=['POST'])
async def api_assistant(request):
    """Alexa+ stand-in: Claude agent that uses this server's tools over MCP (see assistant.py)."""
    import assistant
    text = (await request.json()).get('text', '')
    port = request.url.port or 8000
    out = await assistant.answer(text, mcp_url=f'http://127.0.0.1:{port}/mcp')
    EVENTS.append({'t': time.time(), 'name': 'assistant', 'text': text, 'reply': out['reply'], 'tools': [t['name'] for t in out['tools']]})
    return JSONResponse(out)


@mcp.custom_route('/api/tts', methods=['POST'])
async def api_tts(request):
    """Natural Alexa voice: Microsoft Edge neural TTS (Swara for Hindi/Hinglish, Neerja for English). Needs internet."""
    import edge_tts
    from starlette.responses import Response
    body = await request.json()
    voice = 'hi-IN-SwaraNeural' if body.get('lang', 'hi').startswith('hi') else 'en-IN-NeerjaExpressiveNeural'
    audio = b''
    async for chunk in edge_tts.Communicate(body.get('text', ''), voice, rate='+5%').stream():
        if chunk['type'] == 'audio':
            audio += chunk['data']
    return Response(audio, media_type='audio/mpeg')


@mcp.custom_route('/api/reset', methods=['POST'])
async def api_reset(_):
    return JSONResponse({'ok': reset_call()})


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', default='phone')
    ap.add_argument('--port', type=int, default=int(os.environ.get('PORT', 8000)))
    args = ap.parse_args()
    shield = Shield(args.source, timing=args.source in ('whatsapp', 'phone') or os.environ.get('TIMING') == '1').start()
    if args.source in ('phone', 'whatsapp') or os.environ.get('PAYGUARD') == '1':
        guard = PayGuard(shield).start()
    # PUBLIC_HOST: the tunnel hostname Alexa+ reaches us on (e.g. abc.trycloudflare.com)
    hosts = ['127.0.0.1:*', 'localhost:*'] + [h for h in [os.environ.get('PUBLIC_HOST')] if h]
    app = mcp.streamable_http_app(
        stateless_http=True, json_response=True,  # plain JSON replies: Cloudflare quick tunnels do not pass SSE
        transport_security=TransportSecuritySettings(allowed_hosts=hosts, allowed_origins=[f'https://{h}' for h in hosts] + ['http://localhost:*', 'http://127.0.0.1:*']),
    )
    print(f'Voice Shield: page http://localhost:{args.port}/  MCP http://localhost:{args.port}/mcp  source={args.source}')
    uvicorn.run(app, host='0.0.0.0', port=args.port, log_level='warning')
