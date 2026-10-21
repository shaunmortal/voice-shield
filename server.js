// CareCircle: an MCP server (spec 2025-11-25, Streamable HTTP) that lets Alexa+
// answer "Did Mom take her pills?" and log doses by voice for a caregiving circle.
import http from 'node:http';
import { DatabaseSync } from 'node:sqlite';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import { z } from 'zod';

const db = new DatabaseSync(process.env.DB_PATH ?? 'carecircle.db');
db.exec(`
  CREATE TABLE IF NOT EXISTS meds (
    id INTEGER PRIMARY KEY, person TEXT NOT NULL, name TEXT NOT NULL,
    dose TEXT NOT NULL, times TEXT NOT NULL, -- comma-separated HH:MM
    UNIQUE(person, name));
  CREATE TABLE IF NOT EXISTS doses (
    id INTEGER PRIMARY KEY, med_id INTEGER NOT NULL REFERENCES meds(id),
    taken_at TEXT NOT NULL, logged_by TEXT);
`);

const text = (s) => ({ content: [{ type: 'text', text: s }] });
const today = (now = new Date()) => now.toISOString().slice(0, 10);
const findMed = (person, name) =>
  db.prepare('SELECT * FROM meds WHERE person = ? COLLATE NOCASE AND name = ? COLLATE NOCASE').get(person, name);

// Returns one row per scheduled slot today with whether a dose covers it.
// ponytail: doses are matched to slots in order (nth dose covers nth slot); fine for daily schedules.
export function statusFor(person, now = new Date()) {
  const meds = db.prepare('SELECT * FROM meds WHERE person = ? COLLATE NOCASE').all(person);
  const hhmm = now.toISOString().slice(11, 16);
  return meds.flatMap((m) => {
    const taken = db.prepare("SELECT COUNT(*) n FROM doses WHERE med_id = ? AND substr(taken_at,1,10) = ?")
      .get(m.id, today(now)).n;
    return m.times.split(',').sort().map((t, i) => ({
      med: m.name, dose: m.dose, time: t,
      state: i < taken ? 'taken' : t <= hhmm ? 'missed' : 'upcoming',
    }));
  });
}

function buildServer() {
  const server = new McpServer({ name: 'carecircle', version: '1.0.0' });

  server.registerTool('add_medication', {
    description: 'Add or update a medication schedule for a person in the care circle.',
    inputSchema: {
      person: z.string().describe('Who takes it, e.g. "Mom"'),
      name: z.string().describe('Medication name'),
      dose: z.string().describe('e.g. "10 mg"'),
      times: z.array(z.string().regex(/^\d{2}:\d{2}$/)).min(1).describe('Daily times, 24h HH:MM (UTC)'),
    },
  }, ({ person, name, dose, times }) => {
    db.prepare(`INSERT INTO meds (person, name, dose, times) VALUES (?, ?, ?, ?)
      ON CONFLICT(person, name) DO UPDATE SET dose = excluded.dose, times = excluded.times`)
      .run(person, name, dose, times.join(','));
    return text(`Saved: ${person} takes ${name} ${dose} at ${times.join(', ')}.`);
  });

  server.registerTool('log_dose', {
    description: 'Record that a person just took a medication.',
    inputSchema: { person: z.string(), name: z.string(), logged_by: z.string().optional() },
  }, ({ person, name, logged_by }) => {
    const m = findMed(person, name);
    if (!m) return { ...text(`No medication "${name}" found for ${person}.`), isError: true };
    db.prepare('INSERT INTO doses (med_id, taken_at, logged_by) VALUES (?, ?, ?)')
      .run(m.id, new Date().toISOString(), logged_by ?? null);
    return text(`Logged ${m.name} ${m.dose} for ${m.person}.`);
  });

  server.registerTool('check_status', {
    description: "Today's medication status for a person: what was taken, missed, or still upcoming. Use for questions like 'Did Mom take her pills?'",
    inputSchema: { person: z.string() },
    annotations: { readOnlyHint: true },
  }, ({ person }) => {
    const rows = statusFor(person);
    if (!rows.length) return text(`${person} has no medications on file.`);
    const missed = rows.filter((r) => r.state === 'missed');
    const summary = missed.length
      ? `${person} has missed ${missed.map((r) => `${r.med} at ${r.time}`).join(' and ')}.`
      : `${person} is on track today.`;
    return { ...text(summary), structuredContent: { person, slots: rows } };
  });

  server.registerTool('adherence_report', {
    description: 'Percent of scheduled doses taken over the last N days, for sharing with family or a doctor.',
    inputSchema: { person: z.string(), days: z.number().int().min(1).max(90).default(7) },
    annotations: { readOnlyHint: true },
  }, ({ person, days }) => {
    const meds = db.prepare('SELECT * FROM meds WHERE person = ? COLLATE NOCASE').all(person);
    if (!meds.length) return text(`${person} has no medications on file.`);
    const since = new Date(Date.now() - days * 864e5).toISOString();
    const lines = meds.map((m) => {
      const taken = db.prepare('SELECT COUNT(*) n FROM doses WHERE med_id = ? AND taken_at >= ?').get(m.id, since).n;
      const expected = m.times.split(',').length * days;
      return `${m.name}: ${Math.min(100, Math.round((taken / expected) * 100))}%`;
    });
    return text(`${person}, last ${days} days. ${lines.join('; ')}.`);
  });

  return server;
}

// Stateless Streamable HTTP: a fresh server+transport per request, POST /mcp only.
export const httpServer = http.createServer(async (req, res) => {
  if (req.url !== '/mcp') return res.writeHead(404).end();
  if (req.method !== 'POST') return res.writeHead(405, { Allow: 'POST' }).end();
  const token = process.env.MCP_TOKEN;
  if (token && req.headers.authorization !== `Bearer ${token}`) return res.writeHead(401).end();
  const server = buildServer();
  const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });
  res.on('close', () => { transport.close(); server.close(); });
  await server.connect(transport);
  await transport.handleRequest(req, res);
});

if (import.meta.main) {
  const port = Number(process.env.PORT ?? 3000);
  httpServer.listen(port, () => console.log(`CareCircle MCP on http://localhost:${port}/mcp`));
}
