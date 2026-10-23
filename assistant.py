"""Alexa+ stand-in: an LLM agent that reaches Voice Shield ONLY through MCP, the way Alexa+ reaches an add-on.

Each user utterance: connect to the MCP server over Streamable HTTP -> tools/list -> give the tool schemas to Claude ->
run the tools Claude picks via tools/call -> return Claude's short spoken reply. Nothing here imports engine.py;
if the MCP contract breaks, this breaks, which is the point.
"""
import json
import os

import anthropic
from mcp import Client

MODEL = os.environ.get('ASSISTANT_MODEL', 'claude-opus-5-5')
SYSTEM = """You are Alexa+ in an Indian family home, speaking to an older parent who is on a phone call right now.
The Voice Shield add-on (its tools) watches that call. Reply in the language the user used (Hindi, Hinglish or English),
in at most two short spoken sentences (under 35 words), warm and calm, no lists, no markdown.
- "Is this call real / is it really my son / scam?" -> call get_call_status and explain the level in plain words.
- The caller claims to be family and asks for money, an OTP or secrecy -> call verify_with_family with that person's name.
- The user already sent money or shared an OTP, or asks what to do -> call what_should_i_do with money_sent /
  shared_otp_or_pin set, language "hi" if they spoke Hindi or Hinglish; read the first step aloud.
Never say a voice is certainly fake: the voice score alone only means "verify"."""


async def answer(text, mcp_url='http://127.0.0.1:8000/mcp', on_event=None):
    """Returns {'reply': str, 'tools': [{'name', 'input', 'result'}]}."""
    emit = on_event or (lambda *a: None)
    claude = anthropic.AsyncAnthropic(timeout=60.0)
    async with Client(mcp_url) as mcp:
        listed = (await mcp.list_tools()).tools
        tools = [{'name': t.name, 'description': t.description or '', 'input_schema': t.input_schema} for t in listed]
        messages = [{'role': 'user', 'content': text}]
        used = []
        for _ in range(4):
            r = await claude.messages.create(model=MODEL, max_tokens=2048, system=SYSTEM, tools=tools,
                                             output_config={'effort': 'low'}, messages=messages)
            if r.stop_reason == 'refusal':
                return {'reply': 'Maaf kijiye, main isme madad nahi kar sakti.', 'tools': used}
            if r.stop_reason != 'tool_use':
                reply = ' '.join(b.text for b in r.content if b.type == 'text').strip()
                return {'reply': reply, 'tools': used}
            messages.append({'role': 'assistant', 'content': r.content})
            results = []
            for b in r.content:
                if b.type != 'tool_use':
                    continue
                emit('tool', b.name, b.input)
                res = await mcp.call_tool(b.name, b.input)
                payload = res.structured_content if res.structured_content is not None else \
                    ' '.join(getattr(c, 'text', '') for c in res.content)
                used.append({'name': b.name, 'input': b.input, 'result': payload})
                results.append({'type': 'tool_result', 'tool_use_id': b.id,
                                'content': json.dumps(payload, ensure_ascii=False), 'is_error': bool(res.is_error)})
            messages.append({'role': 'user', 'content': results})
        return {'reply': 'Main abhi jawab nahi de pa rahi, kripya phone kaat kar unhe khud call kijiye.', 'tools': used}
