// End-to-end check: real MCP client over Streamable HTTP against an in-memory DB.
process.env.DB_PATH = ':memory:';
import assert from 'node:assert/strict';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js';
const { httpServer } = await import('./server.js');

await new Promise((r) => httpServer.listen(0, r));
const url = new URL(`http://localhost:${httpServer.address().port}/mcp`);
const client = new Client({ name: 'test', version: '1' });
await client.connect(new StreamableHTTPClientTransport(url));
const call = async (name, args) => (await client.callTool({ name, arguments: args }));

const tools = (await client.listTools()).tools.map((t) => t.name).sort();
assert.deepEqual(tools, ['add_medication', 'adherence_report', 'check_status', 'log_dose']);

await call('add_medication', { person: 'Mom', name: 'Lisinopril', dose: '10 mg', times: ['00:00', '23:59'] });
let s = await call('check_status', { person: 'mom' });
assert.match(s.content[0].text, /missed Lisinopril at 00:00/);

await call('log_dose', { person: 'Mom', name: 'lisinopril', logged_by: 'Sam' });
s = await call('check_status', { person: 'Mom' });
assert.equal(s.structuredContent.slots[0].state, 'taken');
assert.match(s.content[0].text, /on track/);

assert.equal((await call('log_dose', { person: 'Mom', name: 'Nope' })).isError, true);
assert.match((await call('adherence_report', { person: 'Mom', days: 1 })).content[0].text, /Lisinopril: 50%/);

await client.close();
httpServer.close();
console.log('ok');
