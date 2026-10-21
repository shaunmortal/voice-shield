# CareCircle — Alexa+ MCP server for family caregiving

"Alexa, did Mom take her blood pressure pill?" CareCircle is a self-hosted
[MCP](https://modelcontextprotocol.io) server (spec **2025-11-25**, **Streamable HTTP**)
that gives Alexa+ the tools to track medications for someone you care for, so the
whole family can log doses and check status by voice.

## Tools
| Tool | What it does |
|---|---|
| `add_medication` | Add/update a person's med, dose and daily times |
| `log_dose` | Record a dose ("Alexa, Mom just took her Lisinopril") |
| `check_status` | Today's taken / missed / upcoming doses, with structured output |
| `adherence_report` | % of doses taken over the last N days, for family or a doctor |

## Run
Requires Node 24+ (uses built-in `node:sqlite`).
```sh
npm install
npm test          # end-to-end check over Streamable HTTP
npm start         # http://localhost:3000/mcp
MCP_TOKEN=secret npm start   # require Authorization: Bearer secret
```
Try it with the MCP Inspector: `npx @modelcontextprotocol/inspector`, transport
"Streamable HTTP", URL `http://localhost:3000/mcp`.

To reach Alexa+, expose it over HTTPS (e.g. `npx cloudflared tunnel --url http://localhost:3000`)
and register the `/mcp` URL.

## License
MIT
