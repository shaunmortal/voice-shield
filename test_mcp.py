"""End-to-end: server on a synthetic 'scam' clip, spoken to the way Alexa+ would (MCP 2025-11-25 over
Streamable HTTP, raw JSON-RPC). Run: .venv/bin/python test_mcp.py"""
import json, os, subprocess, sys, tempfile, time
import urllib.request, urllib.error

d = tempfile.mkdtemp(); clip = os.path.join(d, 'scam.aiff')
subprocess.run(['say', '-o', clip, 'Papa, I had an accident. Please send twenty five thousand rupees right now. '
                'Do not tell anyone. Please hurry, the hospital is asking for money, I will explain later.'], check=True)
srv = subprocess.Popen([sys.executable, 'server.py', '--source', f'file:{clip}', '--port', '8766'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
URL = 'http://localhost:8766/mcp'
H = {'Accept': 'application/json, text/event-stream', 'Content-Type': 'application/json'}

def rpc(method, params=None, id=1, headers=H):
    data = json.dumps({'jsonrpc': '2.0', 'id': id, 'method': method, 'params': params or {}}).encode()
    with urllib.request.urlopen(urllib.request.Request(URL, data, headers), timeout=30) as r:
        text, ctype = r.read().decode(), r.headers['content-type']
    body = text if ctype.startswith('application/json') else next(l[5:] for l in text.splitlines() if l.startswith('data:'))
    return json.loads(body)['result']

try:
    for _ in range(120):
        try: urllib.request.urlopen('http://localhost:8766/api/status'); break
        except OSError: time.sleep(0.5)
    init = rpc('initialize', {'protocolVersion': '2025-11-25', 'capabilities': {}, 'clientInfo': {'name': 'alexa-sim', 'version': '1'}})
    assert init['protocolVersion'] == '2025-11-25', init
    h = {**H, 'MCP-Protocol-Version': '2025-11-25'}
    tools = sorted(t['name'] for t in rpc('tools/list', id=2, headers=h)['tools'])
    assert tools == ['get_alert_history', 'get_call_status', 'reset_call', 'verify_with_family', 'what_should_i_do'], tools
    levels = []
    for i in range(20):
        levels.append(rpc('tools/call', {'name': 'get_call_status', 'arguments': {}}, id=10 + i, headers=h)['structuredContent']['level'])
        if levels[-1] == 'alert': break
        if i == 19: print(rpc('tools/call', {'name': 'get_call_status', 'arguments': {}}, id=98, headers=h)['structuredContent'])
        time.sleep(1)
    assert levels[-1] == 'alert', levels
    hist = rpc('tools/call', {'name': 'get_alert_history', 'arguments': {}}, id=99, headers=h)['structuredContent']
    assert len(hist['result']) == 1, hist
    print('levels seen:', levels, '\nok')
finally:
    srv.terminate()
