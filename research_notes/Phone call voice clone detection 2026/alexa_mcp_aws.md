# Connecting a self-hosted MCP server to Alexa+ (hackathon track) and cheap AWS scam-language detection — as of 2026-10-21

Scope: "Build, Ship, Shape: Amazon Developer Hackathon" (Devpost), Alexa+ track + AWS Builder mini-challenge, for the Voice Shield project (Python `mcp` SDK 2.x, uvicorn :8000, Streamable HTTP, MCP spec 2025-11-25).

Headline for the report writer: **hackathon participants cannot connect a self-hosted MCP server to a real Alexa+ device or to Amazon's gated add-on tooling** (Devpost FAQ, Oct 2026). The accepted path is: run your own Streamable HTTP MCP server + demo it through your own web page acting as a real MCP client ("simulated Alexa+ experience"). Everything below about the official Alexa+ MCP Toolkit is still useful as the *spec to build against* (so the server would drop into Alexa+ unchanged), and is good material for the Product Feedback / Friction Log sections that judges score.

---

## Key Question 1 — Alexa+ developer onboarding for MCP in 2026: console, registration flow, auth, hosting requirements, tool-description guidance

### Takeaway
Amazon shipped an official "Alexa+ MCP Toolkit" (part of "Alexa+ for Builders", preview since July 2026) with a CLI (`npm install -g @alexa-ai/cli`, `alexa-ai new mcp` / `alexa-ai deploy`), an `addon.json` manifest, a web simulator, and a Local Inspector — but it is a **private preview for select partners only; hackathon entrants have no way to apply**. Spec requirements are public: MCP 2025-11-25, Streamable HTTP only (legacy HTTP+SSE must be migrated), public HTTPS URL (cloudflared explicitly OK for dev), OAuth 2.1 auth-code + PKCE S256 with **static** client registration (no DCR), `401` without `WWW-Authenticate` + RFC 9728 protected-resource metadata, Bearer in `Authorization` header, round-trip under 500 ms.

### Cited Findings

**Program / console / preview status**
- Alexa+ MCP Toolkit overview: "Alexa+ acts as the MCP client"; you can bring an existing MCP server; the toolkit "supports the 2025-11-25 version of the MCP specification" and "also supports the MCP Apps extension"; runtime requests route "through your add-on to your MCP server using streamable HTTP"; deploy/configure via "the add-on Agent Skill (agentic onboarding experience)" or "the Alexa AI CLI directly"; after any tool change run `alexa-ai deploy` — [Alexa+ MCP Toolkit Overview](https://developer.amazon.com/docs/alexaplus/add-ons/mcp-toolkit-overview.html)
- July 23, 2026 Amazon blog: "service providers can bring their own MCP server"; via Alexa+ for Builders "Alexa+ inspects the server, proposes an integration path, and delivers a simulator-ready package"; "The integration paths are in Preview"; MCP partners named: Canva, Cengage, Headspace, Priceline, Viator, Virgin Atlantic, Lyft, FlixBus, Greyhound etc. — [Alexa+ launches new ways to build experiences](https://developer.amazon.com/alexaplus/blogs/2026/07/alexa-plus-new-ways-to-build-experiences)
- July 27, 2026: "Alexa+ for Builders portal" launched with three preview integration paths: Category SDK, MCP Toolkit, Smart Home AI Toolkit — [Amazon Developer Community, July 27 2026](https://community.amazondeveloper.com/t/july-27-2026-alexa-for-builders-portal/28918)
- Add-on dev process: "you request access to the Private Preview. After approval, you receive credentials and install the tooling" (Alexa-AI CLI + add-on agent skill) — [Build Alexa+ Add-ons: Development Stages](https://developer.amazon.com/docs/alexaplus/add-ons/alexa-plus-add-on-development-stages.html) (snippet via search; page body not fetched)
- **Hackathon FAQ (official, Devpost)**: "Will hackathon participants get access to the gated Alexa+ developer tools (Category SDK, MCP Toolkit, CLI, or Web Simulator)? — No. Amazon's Alexa+ Add-on developer tools … are in preview and available to select partners only - there is currently no way for hackathon participants to apply for or gain access … You do not need these tools for your submission: build a self-hosted MCP server (or Agent Skill) per the Official Rules, and demo it via your own web-based simulator or front end." — [Devpost FAQs](https://amazonappdev2026.devpost.com/details/faqs)
- Docs home for the toolkit family: [Alexa+ Add-ons home](https://developer.amazon.com/docs/alexaplus/add-ons/home.html); [Alexa+ Add-ons overview](https://developer.amazon.com/docs/alexaplus/add-ons/overview.html) (lists add-on properties incl. "Geographic availability (which countries the add-on can operate in)" — no country list given)

**Exact registration flow (for reference; gated)**
- Prereqs: Alexa developer account (CLI authenticates via Login with Amazon); dev environment; MCP server meeting requirements. Step 1 `alexa-ai configure` (opens LWA browser; `--no-browser` for SSH); creds at `~/.alexa-ai/credentials`. Path A = add-on Agent Skill in "Claude Code, Kiro, Cursor, and VS Code Copilot, or any agent with shell access": give it your MCP server URL -> it introspects over Streamable HTTP/JSON-RPC 2.0, runs `alexa-ai new mcp`, drafts descriptions, collects privacy/terms URLs + icons, deploys to development stage, returns Add-on ID, then `alexa-ai submit` after testing in the web simulator. Path B manual: `alexa-ai new mcp --name "Hotel Finder" --locale en-US --mcp-server-url "https://mcp.example.com"` -> edit `addon-package/addon.json` -> `alexa-ai deploy` — [Alexa+ MCP QuickStart](https://developer.amazon.com/docs/alexaplus/add-ons/mcp-toolkit-quickstart)
- `addon.json` fields: `manifestVersion "1.0"`, `storeListing.distributionCountries` (e.g. `["US"]`), `locales.en-US.{name (<=30 chars, optional spokenForm), shortDescription (<=123), fullDescription (<=4000), examplePhrases (3-4, <=200 chars each), privacyAndCompliance.{privacyPolicyUrl, termsOfUseUrl}, mediaAssets.icons.light (72/64/88/126/180/241 px, all required), carouselImages (>=1 at 600x900), bannerImages (1200x600 optional)}`, `integrations[] = {type: "MCP", config.endpoints.default: {type: "HTTPS", uri}}` — [Alexa+ MCP QuickStart](https://developer.amazon.com/docs/alexaplus/add-ons/mcp-toolkit-quickstart)
- CLI install: `npm install -g @alexa-ai/cli`; verify `alexa-ai --version`; Node.js 24+; **before install you complete AWS setup (IAM user, `alexa-ai` profile, Git for CodeCommit, and CodeArtifact npm login for `@alexa-ai` packages)** — i.e. the package is served from a gated CodeArtifact repo, not public npm — [Set Up Your Development Environment](https://developer.amazon.com/docs/alexaplus/add-ons/set-up-your-development-environment)
- Account requirements on the same page: complete Alexa App profile (phone, address), "Set your preferred marketplace on the Retail Website to an Alexa+ supported marketplace", device language set to an Alexa+ supported locale — [Set Up Your Development Environment](https://developer.amazon.com/docs/alexaplus/add-ons/set-up-your-development-environment)
- Full CLI surface: `alexa-ai configure [--profile] [--no-browser]`; `alexa-ai new [mcp|action] [--name] [--locale] [--mcp-server-url] [--category] [--language] [--hosting] [--non-interactive] [--requires-auth] [--auth-client-id] [--auth-scopes]`; `alexa-ai deploy [--ignore-hash] [--skip-validation] [--json]`; `alexa-ai test [--stage development|live] [--test-suite <path>] [--filter]`; `alexa-ai submit [--yes]`; `alexa-ai list`; `alexa-ai status [--addon-id] [--deployment-id]`; `alexa-ai configure-account-linking --addon-id <id> --config-file <path>`; `alexa-ai get-account-linking`; catalog + metrics commands; state file `.alexa-ai/config.json` — [Alexa AI CLI Reference](https://developer.amazon.com/docs/alexaplus/add-ons/alexa-ai-cli-reference)

**Auth requirements**
- "Account linking is optional" — enable only if tools need user identity. Uses OAuth 2.1; only Authorization Code Grant; "Dynamic Client Registration (DCR) isn't supported" (static client id/secret); PKCE `code_challenge_method=S256` mandatory (CLI validates; deploy fails without it); authorization request params `client_id, redirect_uri, response_type=code, scope, state, code_challenge, code_challenge_method=S256, resource`; token POST `application/x-www-form-urlencoded` with `grant_type=authorization_code, code, redirect_uri, client_id, code_verifier, resource`; token endpoint must return `refresh_token` with every access token; return `401`/`403` on unauthenticated tool call to trigger linking (example body `{"error":"unauthorized","message":"Access token required to use this tool."}`); PRM at `https://your-mcp-server.com/.well-known/oauth-protected-resource` with `resource` (must equal manifest URL), `authorization_servers` (only first used), `scopes_supported`; secret via masked prompt or `ALEXA_CLIENT_SECRET` env; Alexa caches auth metadata at deploy time; register all Alexa redirect URIs listed in the Alexa+ Developer Hub — [Account Linking for MCP Add-ons](https://developer.amazon.com/docs/alexaplus/add-ons/mcp-toolkit-account-linking)
- Quickstart auth checklist: "Unauthenticated requests get `401` without a `WWW-Authenticate` header"; PRM per RFC 9728; `/.well-known/oauth-authorization-server` must list `S256` in `code_challenge_methods_supported`; send `resource` on both auth and token requests; "Send the Bearer token in the `Authorization` header. Never put it in the query string"; **Not yet supported: Dynamic Client Registration, Client ID Metadata Documents, OpenID Connect, Step-Up Authorization, and `WWW-Authenticate` on 401 responses** — [Alexa+ MCP QuickStart](https://developer.amazon.com/docs/alexaplus/add-ons/mcp-toolkit-quickstart)
- Supported Capabilities page covers only "service-level and user-level authentication for your MCP server, using OAuth 2.1" and account linking; mentions "payments, and permissions" without detail — [Supported Capabilities](https://developer.amazon.com/docs/alexaplus/add-ons/mcp-toolkit-supported-capabilities)

**Hosting / transport / timing**
- "Transport: Streamable HTTP. The legacy HTTP+SSE transport must be migrated"; "Reachability: A remote URL. For local development, a tunnel such as cloudflared works"; "Latency: Round-trip query response under 500 ms"; "Alexa+ refreshes tool information only on deployment" — [Alexa+ MCP QuickStart](https://developer.amazon.com/docs/alexaplus/add-ons/mcp-toolkit-quickstart)
- Client behaviour: on deploy Alexa+ connects and registers tools/resources; client sends `initialize` with **`protocolVersion` `2025-03-26`**, declares `roots` capability (`listChanged: true`), identifies as "Alexa+ MCP Client" v1.0.0; "There is no explicit MCP session identifier. Context comes from the customer's prior Alexa+ conversations"; Alexa+ uses conversation history to build a tool-selection prompt then sends `tools/call`; tool results may carry `structuredContent`, a text block with the same JSON, and `_meta.ui {resourceUri, invoking, invoked}`; supports MCP **elicitation** when details are missing; if `resourceUri` present it renders your MCP App UI, else a data-only flow — [Alexa+ MCP Client and App Lifecycle](https://developer.amazon.com/docs/alexaplus/add-ons/mcp-toolkit-client-lifecycle)
- Testing: web simulator (text chat + device-frame preview), must deploy first, optionally route a simulator session to a physical Alexa device; Local Inspector CLI `addon-local-inspector https://your-mcp-server.example.com/mcp [--server-port 6277 --client-port 6274]` (Node 24+), inspects tool definitions, request/response payloads, errors and latency; visual analysis only for tools with `_meta.ui.resourceUri` (`ui://`); verdicts CERTIFIED / CONDITIONAL / NOT_CERTIFIED; proxy MCP calls use `Accept: application/json` — [Test Your MCP Add-ons](https://developer.amazon.com/docs/alexaplus/add-ons/mcp-toolkit-test-add-ons); [Local Inspector](https://developer.amazon.com/docs/alexaplus/add-ons/mcp-toolkit-local-inspector)
- Design guide (landing page): Alexa+ is "a multimodal conversational surface"; "MCP responses may include a visual and/or a spoken reply"; "you can't script what Alexa says" but can design your data so responses are useful; sub-sections: conversation surface, display modes (inline, fullscreen, voice-only), components, layout — [Alexa+ MCP Add-on Design Guide](https://developer.amazon.com/docs/alexaplus/add-ons/mcp-addon-design-guide)
- MCP spec 2025-11-25 Streamable HTTP: single endpoint for POST+GET; client `Accept` must list `application/json` and `text/event-stream`; notifications -> `202 Accepted`; a request may be answered with `application/json` or an SSE stream; GET may return `405`; optional `MCP-Session-Id` (server may assign; clients must echo; 404 => re-initialize); `MCP-Protocol-Version: 2025-11-25` header on subsequent requests, server assumes `2025-03-26` if absent; "Servers MUST validate the `Origin` header … respond with HTTP 403" and SHOULD bind localhost locally — [MCP spec 2025-11-25 Transports](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)

**Hackathon-provided links for the Alexa+ track (the only "official resources")**
- Rules "How to enter" for Alexa+: "Develop an MCP following the open-source docs: modelcontextprotocol.io/docs/latest/getting-started/intro" — [Devpost Rules](https://amazonappdev2026.devpost.com/rules)
- Resources tab, Alexa+ section: "Build a working MCP (Model Context Protocol) integration on the open standards for Agent Skills and Streamable HTTP transports. You can simulate an Alexa+ experience using your preferred agentic tools via a web app." Links: "Build with Agent Skills" -> https://apps.extensions.modelcontextprotocol.io/api/#build-with-agent-skills ; "Streamable HTTP transport" -> https://modelcontextprotocol.io/specification/2025-11-25/basic/transports#streamable-http — [Devpost Resources](https://amazonappdev2026.devpost.com/resources)
- "Amazon Devices Builder Tools - an MCP server and Agent Skills that bring Amazon device knowledge into your AI coding assistant" (Fire TV/Vega oriented) — https://developer.amazon.com/docs/vega/0.24/mcp-server — [Devpost Resources](https://amazonappdev2026.devpost.com/resources)
- Build Session recording (Chris Traganos + Moses Roth, Sept 3 2026, covers "Using the MCP open standard to build Alexa+ add-ons"): https://youtu.be/ws61g53S2b4 ; office hours were Oct 6 and Oct 19 (Zoom, both past); Discord https://discord.com/invite/HP4BhW3hnp — [Devpost Updates](https://amazonappdev2026.devpost.com/updates)

### Inferences
- The official toolkit is irrelevant to *access* but highly relevant to *design*: build the server so it would pass Amazon's checklist unchanged (Streamable HTTP, JSON responses, `structuredContent` + text block, optional `_meta.ui`, <500 ms, no auth or static-client OAuth). Stating this explicitly in the write-up ("designed to Amazon's published MCP Toolkit requirements; blocked only by preview gating") is exactly the kind of Friction Log entry that earns the up-to-10% bonus.
- Alexa+ initializes with `protocolVersion 2025-03-26` even though the toolkit says it supports 2025-11-25; a server should accept version negotiation gracefully (the `mcp` Python SDK does).
- Because Alexa+ has "no explicit MCP session identifier", a stateless server (`stateless_http=True` / `json_response=True` in FastMCP) matches Alexa+'s model and also avoids tunnel SSE problems (see Q4).

### Gaps
- No public page lists the Alexa+ developer-preview application form, eligible countries, or the Developer Hub URL; the FAQ says there is no application path at all for entrants.
- The MCP design guide's sub-pages (tool naming/description length, annotations such as `readOnlyHint`) were not retrievable; only the landing page was readable. No Amazon-published tool-annotation best practices were found.
- Amazon docs do not state request timeout, max tools, or response-size limits beyond the 500 ms round-trip guidance.
- Devpost FAQ/Resources pages returned 403 to automated fetchers; content above was captured via a browser-UA download on 2026-10-21 and may change.

---

## Key Question 2 — What "Agent Skill" means in the Alexa+ / hackathon context

### Takeaway
In this hackathon "Agent Skill" means the open **Agent Skills standard (agentskills.io, SKILL.md folders, Anthropic-originated)** — the Resources tab's "Build with Agent Skills" link goes to the MCP Apps extension repo's SKILL.md-based skills, not to any Alexa-specific format. In Amazon's own Alexa+ docs the phrase "add-on Agent Skill" refers to Amazon's gated SKILL.md that drives Claude Code/Kiro/Cursor through onboarding an MCP server. Neither is the classic Alexa Skills Kit "skill".

### Cited Findings
- Hackathon Resources, Alexa+ section: "Build a working MCP … integration on the open standards for Agent Skills and Streamable HTTP transports"; link "Build with Agent Skills" -> https://apps.extensions.modelcontextprotocol.io/api/#build-with-agent-skills — [Devpost Resources](https://amazonappdev2026.devpost.com/resources)
- That target page: the ext-apps repo "ships four Agent Skills" (links to agentskills.io) usable by "any AI coding agent that supports Agent Skills"; files are `SKILL.md`; Claude Code install: `/plugin marketplace add modelcontextprotocol/ext-apps` then `/plugin install mcp-apps@modelcontextprotocol-ext-apps`; skills: `create-mcp-app` ("Scaffolds a new MCP App with an interactive UI from scratch"), `add-app-to-server` (adds UI to an existing MCP server's tools), `migrate-oai-app`, `convert-web-app`; repo https://github.com/modelcontextprotocol/ext-apps ; MCP Apps = tools declare a `ui://` resource rendered in a sandboxed iframe — [MCP Apps API page](https://apps.extensions.modelcontextprotocol.io/api/)
- Rules Alexa+ requirement: "A working Agent Skill or a self-hosted MCP server, implementing MCP spec version 2025-11-25 (or a later version, once confirmed) over Streamable HTTP." Judging "Creative" examples for Alexa+: "agentic workflow that orchestrates across services autonomously, context-aware add-on that maintains state across sessions, purchasing capabilities, media support (cards, carousels, etc), MCP Apps, Agent Skills" (MCP Apps linked to https://modelcontextprotocol.io/extensions/apps/overview) — [Devpost Rules](https://amazonappdev2026.devpost.com/rules)
- Amazon's usage: "deploy and configure your Alexa+ add-on using the add-on Agent Skill (agentic onboarding experience) or directly with the Alexa AI CLI" — [MCP Toolkit Overview](https://developer.amazon.com/docs/alexaplus/add-ons/mcp-toolkit-overview.html); the skill "guides an AI coding agent through onboarding … Claude Code, Kiro, Cursor, and VS Code Copilot" — [MCP QuickStart](https://developer.amazon.com/docs/alexaplus/add-ons/mcp-toolkit-quickstart)
- Same term used by other tracks: Bee track accepts "Bee's CLI, MCP, or Agent Skills" with repo https://github.com/bee-computer/bee-skill; Fire TV "Amazon Devices Builder Tools - an MCP server and Agent Skills" — [Devpost Resources](https://amazonappdev2026.devpost.com/resources)
- Classic ASK skills are a different thing (developer console, Lambda hosting) — [About the Alexa Developer Console](https://developer.amazon.com/en-US/docs/alexa/devconsole/about-the-developer-console.html)

### Inferences
- A cheap way to satisfy "Agent Skill" *and* MCP in one repo: ship a `SKILL.md` (agentskills.io format) alongside the MCP server — e.g. a `voice-shield` skill that teaches any coding agent how to call the server's tools / interpret the risk score. Judges list "Agent Skills" under "creative".
- Nothing indicates Amazon has forked the format; the agentskills.io SKILL.md layout is what the organisers link to.

### Gaps
- Amazon's own add-on Agent Skill file is not publicly downloadable (gated with the CLI); its exact contents could not be reviewed.

---

## Key Question 3 — No Alexa+ preview access (India, no Echo): the accepted "simulated Alexa+ experience" path and Amazon-provided simulators

### Takeaway
The official rules and FAQ explicitly accept a "simulated Alexa+ experience" and even say a web page that acts as a real MCP client (initialize / tools/list / tools/call over Streamable HTTP) satisfies the track. No Amazon-provided Alexa+ simulator or sample UI is available to entrants (the web simulator is partner-only); Ring's simulator does not apply. India is an eligible country; Alexa+ itself launched in India (Early Access from Sept 16, 2026, English/Hindi/Hinglish) but that is consumer access, not developer access.

### Cited Findings
- Rules: "Alternatively, entrants may submit a simulated Alexa+ experience instead — built using any AI or agentic tool of their choice, no specific framework, SDK, or MCP-shaped surface required. This alternate path is exempt from the runtime-technology-hook requirement above; the code repository must still include the simulation's source code, and the demo video must clearly show the simulated experience." — [Devpost Rules](https://amazonappdev2026.devpost.com/rules)
- Rules (runtime hook for Alexa+/Bee/Ring): "The repository must demonstrate use of your track's required technology at runtime in your code — imported and actually called (a library import, an app/backend entry point, or a loaded agent/flow/MCP config), not just named in the README." — [Devpost Rules](https://amazonappdev2026.devpost.com/rules)
- FAQ: "can I demo my self-hosted MCP server through a web page that acts as a real MCP client, instead of a device? — Yes. A web page that acts as an actual MCP client (sending initialize, tools-list, and tools-call requests over Streamable HTTP) satisfies the requirement - this is the simulated-experience path … since there's no way for any participant to connect a self-hosted MCP server to a real Alexa+ device or developer console (that tooling is select-partners-only). Showing an existing AI assistant app calling the same server is a nice bonus, but not required." — [Devpost FAQs](https://amazonappdev2026.devpost.com/details/faqs)
- FAQ: "Alexa+: build a self-hosted MCP server or Agent Skill, or a simulated experience - no physical device needed." and "A locally runnable public repo plus your demo video is enough - judges can download, build, and test it themselves, so hosting isn't required." and "Your MCP server doesn't need to stay running after you submit." — [Devpost FAQs](https://amazonappdev2026.devpost.com/details/faqs)
- Eligibility: open worldwide except "Brazil, Quebec, Russia, Crimea, Cuba, Iran, and North Korea" and OFAC-sanctioned countries; India not excluded — [Devpost Rules](https://amazonappdev2026.devpost.com/rules)
- Submission mechanics: video "less than three (3) minutes", public on YouTube or Vimeo, must show the project functioning; materials in English; GitHub only (GitLab rejected per FAQ); public repo with visible OSS license OR private repo shared with Devpost + Amazon reviewers `knmeiss, giolaq, anishamalde, mosesroth, emersonsklar` (invites expire in 7 days); required Product Feedback answers per tool; optional Feature Requests and Friction Log entries ("up to 10% bonus") — [Devpost Rules](https://amazonappdev2026.devpost.com/rules); [Devpost FAQs](https://amazonappdev2026.devpost.com/details/faqs)
- Dates: Submission Period ends "Friday, October 23, 2026 (12:00 pm Pacific Time)" (site banner: "Oct 23, 2026 @ 12:00pm PDT" / "October 23 at 3:00pm EDT"); Judging Nov 9–20, 2026; winners "On or around Thursday, December 3, 2026" — [Devpost Rules](https://amazonappdev2026.devpost.com/rules)
- Prizes: Alexa+ 1st $25,000 + $15,000 AWS credits + meeting with Amazon Developer team; 2nd $15,000 + $5,000 credits; 3rd $4,000 + $1,000 credits; "A project can only win one (1) track prize and one (1) mini challenge prize." — [Devpost Rules](https://amazonappdev2026.devpost.com/rules)
- Judging criteria (equal weight): technical execution / use of required tech; product experience; creativity ("Obvious: single-turn Q&A bot, basic MCP wrapper around an existing API") — [Devpost Rules](https://amazonappdev2026.devpost.com/rules)
- Amazon simulators: the Alexa+ "web simulator" exists only inside the gated toolkit (deploy required) — [Test Your MCP Add-ons](https://developer.amazon.com/docs/alexaplus/add-ons/mcp-toolkit-test-add-ons); Ring offers the "Ring Developer Playground" simulator (Ring track only) — [Devpost FAQs](https://amazonappdev2026.devpost.com/details/faqs)
- Alexa+ in India: Early Access rollout began Sept 16, 2026; "speaks English, Hindi, and Hinglish, and can switch between them within a sentence"; free during Early Access and for Prime; INR 2,000/month standalone otherwise; request at amazon.in/alexaplus; runs on Echo, Fire TV and the Alexa app, browser "coming soon to India" — [aboutamazon: Alexa+ arrives in India](https://www.aboutamazon.com/news/devices/alexa-plus-international-launch); Alexa+ now in 12 countries (US, Italy, Mexico, Canada, UK, Spain, Austria, Germany, France, Brazil, Australia, India) — [Amazon Dev News Sept 21 2026](https://community.amazondeveloper.com/t/sept-21-2026-alexa-in-india-aws-builder-app/29198)

### Inferences
- Deadline in India time: Oct 23 12:00 PDT = **Sat Oct 24, 00:30 IST** (my conversion). The user's "24 Oct" is correct only in IST.
- Minimum compliant demo: (1) the Python MCP server (the "runtime hook": `mcp` import + Streamable HTTP app entry point), (2) a small web page that POSTs `initialize` -> `notifications/initialized` -> `tools/list` -> `tools/call` to `/mcp` with `Accept: application/json, text/event-stream` and renders the reply in an Alexa-like card, (3) a <3-min video showing both. Mentioning Alexa+'s own lifecycle (protocolVersion handshake, `structuredContent`, `_meta.ui`) in the simulator makes the "simulation" credibly Alexa-shaped.
- Because Alexa+ India speaks Hindi/Hinglish, a Hindi/Hinglish scam-script classifier (Q5) is on-theme for the India launch and worth citing in the write-up.

### Gaps
- No Amazon-provided Alexa+ UI kit, device frame assets, or sample "simulator" web app was found for entrants; the Build Session video (https://youtu.be/ws61g53S2b4) was not transcribed and may contain additional guidance.

---

## Key Question 4 — Cheapest way to expose the laptop MCP server over public HTTPS for a demo, and MCP-specific gotchas

### Takeaway
Cloudflare quick tunnel (`cloudflared tunnel --url http://localhost:8000`) is free, needs no account, and is the tunnel Amazon's own quickstart names — but it **does not support SSE**, so run the Python server in JSON-response/stateless mode. ngrok free is fine too (3 endpoints, 1 GB, 20k requests, free dev domain) but adds an interstitial on browser requests. Tailscale Funnel works on ports 443/8443/10000 only and needs the open-source macOS build. The main MCP gotcha is the SDK's DNS-rebinding guard returning `421 Invalid Host header` when a tunnel hostname is not in `allowed_hosts`.

### Cited Findings
- Cloudflare: "cloudflared tunnel --url http://localhost:8080"; "Each Quick Tunnel supports up to 200 in-flight requests. Additional requests return a 429 response"; "Quick Tunnels have no uptime guarantee"; "**Quick Tunnels do not support Server-Sent Events (SSE)**"; "The hostname changes each time you create a Quick Tunnel" — [Cloudflare TryCloudflare docs](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/)
- Amazon: "For local development, a tunnel such as cloudflared works" — [Alexa+ MCP QuickStart](https://developer.amazon.com/docs/alexaplus/add-ons/mcp-toolkit-quickstart)
- Third-party confirmation of the SSE limitation for MCP: "Cloudflare Quick Tunnels do not support Server-Sent Events (SSE) … you must use the Streamable HTTP transport" — [Beeper desktop API docs](https://developers.beeper.com/desktop-api/advanced/remote-access/cloudflare)
- ngrok Free (pricing page): "Up to 3 online endpoints", "Up to 1GB data transfer", "Up to 20k HTTP/S requests", "Assigned dev domain for public endpoints" (1 development domain), "Interstitial page on HTTP/S endpoints"; TCP endpoints need a verified card (not charged); Hobbyist tier removes the interstitial — [ngrok pricing](https://ngrok.com/pricing). Third-party 2026 guides claim 2-hour session limits on free; unverified — [merginit comparison](https://merginit.com/blog/19062026-free-developer-tunnels-comparison)
- Tailscale Funnel: `tailscale funnel 8000`; requires Tailscale >= 1.38.3, MagicDNS, HTTPS certs, `funnel` nodeAttr (auto-added); only ports 443, 8443, 10000; only `*.ts.net` names; TLS only; unconfigurable bandwidth limits; "On macOS, you must use an open source variant of the Tailscale app"; Let's Encrypt rate-limit warning — [Tailscale Funnel KB](https://tailscale.com/kb/1223/funnel)
- Other free options surfaced: Pinggy free (60-min tunnel timeout), LocalXpose (2 tunnels, no time limit) — [pinggy blog](https://pinggy.io/blog/best_cloudflare_tunnel_alternatives/)
- Python MCP SDK DNS-rebinding protection: a 421 "Invalid Host header" means the Host isn't in the allowlist; fix by passing `transport_security=` to `streamable_http_app()` listing the hostname bare and with `:*`; "Setting a non-localhost `host=` does not add that hostname to the allowlist"; FastMCP auto-enables protection when host is localhost-like with allowlist `127.0.0.1:*`, `localhost:*`, `[::1]:*`; requests with no Origin are allowed, a disallowed Origin gets 403; disabling is reasonable only behind a trusted proxy — [MCP Python SDK: transport security](https://py.sdk.modelcontextprotocol.io/v2/api/mcp/server/transport_security/); [MCP Python SDK deploy guide](https://py.sdk.modelcontextprotocol.io/v2/run/deploy/)
- Spec: servers MUST validate Origin (403 if invalid); POST responses may be `application/json` or SSE; GET may return 405; `MCP-Session-Id` optional — [MCP spec Transports](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)
- Cloudflare proxy read timeout for free plans reported as ~100 s (sources conflict 100 vs 120 s) — [hjarni MCP SSE timeout note](https://hjarni.com/mcp-fix/mcp-sse-timeout)
- Hackathon FAQ hosting suggestion: "AWS Lambda is a good fit for an MCP server during a hackathon … typical usage falls within the AWS free tier" — [Devpost FAQs](https://amazonappdev2026.devpost.com/details/faqs)

### Inferences
- Recommended demo setup (no account, ~1 minute): `brew install cloudflared && cloudflared tunnel --url http://localhost:8000`. Since quick tunnels drop SSE, construct the server with JSON responses and no SSE GET stream (in the Python SDK: `FastMCP(..., json_response=True, stateless_http=True)` or equivalent `TransportSecuritySettings(enable_dns_rebinding_protection=True, allowed_hosts=["<rand>.trycloudflare.com", "<rand>.trycloudflare.com:*", "localhost:*", "127.0.0.1:*"])`). The quick-tunnel hostname is random per run, so either set `allowed_hosts` after reading the printed URL, or disable rebinding protection only for the demo (document this as a deliberate corner cut).
- ngrok's interstitial only hits browser-like requests; a web-page MCP client calling the ngrok URL from the browser will trigger it unless the request sets `ngrok-skip-browser-warning` — simpler to use Cloudflare.
- The 500 ms round-trip guidance from Amazon is irrelevant for the simulated path but worth measuring and reporting.

### Gaps
- No official Cloudflare statement on quick-tunnel idle/read timeouts; the Host header the origin receives through a quick tunnel is not documented on the Cloudflare page (empirically it is the trycloudflare hostname, hence the 421 issue — treat as inference).

---

## Key Question 5 — AWS Builder mini-challenge: cheapest documented integration for a scam-script classifier (Bedrock models/regions/pricing, Guardrails, Transcribe Hindi, Strands, AgentCore, Kiro Crew, free tier)

### Takeaway
The mini-challenge accepts "any primary track project that incorporates AWS services … with documented integrations", and **Kiro Crew alone qualifies** without any runtime AWS call. The cheapest documentable runtime integration is a single Bedrock `Converse` call to **Amazon Nova Micro** (~$0.035 in / $0.14 out per 1M tokens; ≈ $0.02 per 1,000 short classifications) — but judges call "single Bedrock call for text generation" *obvious*; adding Bedrock Guardrails ($0.15 per 1,000 text units per policy) and/or a Strands agent moves it toward "multi-service pipeline". Transcribe streaming supports `hi-IN` and `en-IN` (Hinglish only via language identification between the two). Hackathon $150 AWS promo credits ran out Oct 7; new AWS accounts get $100–$200 credits.

### Cited Findings

**What counts**
- "AWS Builder (Mini Challenge): Any primary track project that incorporates AWS services (i.e. Amazon Bedrock, AgentCore, Strands SDK, Kiro Crew, SageMaker, etc.) with documented integrations. Kiro Crew qualifies on its own as a development tool used during the hackathon — a submission does not need to also call a runtime AWS service"; submission must "Describe which AWS service(s) you used and how, in your Product Feedback answer"; prize $5,000 cash + $5,000 AWS credits; judging: "Obvious: single Bedrock call for text generation, S3 for storage. Creative: multi-service pipeline (Bedrock + AgentCore + Strands), agentic architecture with Claude/Kiro for development workflow, agent orchestration patterns." — [Devpost Rules](https://amazonappdev2026.devpost.com/rules)
- Resources: "The AWS free tier is enough to get started"; "Learn on Builder Center" https://builder.aws.com/learn ; "October 7th Update: Unfortunately, we are out of credit codes and are no longer accepting credit requests." — [Devpost Resources](https://amazonappdev2026.devpost.com/resources)
- FAQ cost advice: "Judging runs November 9-20, so you don't need Bedrock or other AWS services running continuously … There isn't an official offline emulator for Bedrock, so for early development consider mocking or stubbing the Bedrock calls" — [Devpost FAQs](https://amazonappdev2026.devpost.com/details/faqs)
- Kiro Crew: open-source (Apache 2.0 orchestration layer) autonomous agent workspace launched by AWS on Aug 4, 2026, extends the Kiro CLI, multi-agent coordination, heartbeat monitoring, reachable via Slack/Telegram/Discord — [devops.com](https://devops.com/aws-adds-agentic-workspace-to-kiro-ai-coding-tool/); [DigitalToday](https://www.digitaltoday.co.kr/cn/view/89218/aws-launches-autonomous-orchestrator-kiro-crew-for-24-hour-code-development-support)

**Bedrock models, regions, prices**
- Guardrails (official): content filters $0.15 per 1,000 text units; denied topics $0.15 per 1,000 text units; image content filters $0.00075/image; word filters and regex sensitive-info filters free — [Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/)
- Nova Micro on-demand: $0.035 input / $0.14 output per 1M tokens (aggregators; one source rounds to $0.03) — [Layer3 Labs price table](https://www.layer3labs.io/ai-model-pricing); [anotherwrapper Nova Micro](https://anotherwrapper.com/llm-pricing/nova-micro); Nova 2 Lite $0.30 / $2.50 per 1M (aggregator, Sept 2026) — [anotherwrapper Nova 2 Lite](https://anotherwrapper.com/llm-pricing/nova-2-lite)
- Claude Haiku 4.5 on Bedrock: $1.00 input / $5.00 output per 1M tokens (aggregators, July 2026) — [Layer3 Labs](https://www.layer3labs.io/ai-model-pricing); [pricepertoken](https://pricepertoken.com/pricing-page/model/anthropic-claude-haiku-4.5). (One outlier source lists $0.80/$4.00 — [factualminds](https://www.factualminds.com/blog/aws-bedrock-nova-models-guide/) — treat as unreliable.)
- Regional availability (official): Nova Micro / Lite / Pro are in-region in us-east-1 and reachable in ap-south-1 (Mumbai) only via geographic cross-region inference; Nova 2 Lite is Geo/Global-only in us-east-1 and Global-only from Mumbai; `apac` prefix routes to Asia Pacific regions — [Bedrock regional availability](https://docs.aws.amazon.com/bedrock/latest/userguide/models-region-compatibility.html)
- Claude in India: Haiku 4.5 available from ap-south-1 via Global CRIS profile `global.anthropic.claude-haiku-4-5-20251001-v1:0` — [AWS ML blog: Claude in India with Global CRIS](https://aws.amazon.com/blogs/machine-learning/access-anthropic-claude-models-in-india-on-amazon-bedrock-with-global-cross-region-inference); a later AWS post describes an India-only geographic profile (Mumbai + Hyderabad, data stays in India) adding Claude models (reported as Opus 5 / Sonnet 5 / Haiku 4.5 on Sept 29) — [AWS ML blog: India cross-region inference](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-expands-claude-model-availability-to-india-cross-region-inference/) (snippet only; profile IDs not verified)
- Model card for Haiku 4.5 lists profiles `global.`, `au.`, `jp.` — [Haiku 4.5 model card (docs mirror)](https://docs.aws.eu/bedrock/latest/userguide/model-card-anthropic-claude-haiku-4-5.html)

**Transcribe**
- `hi-IN` (Hindi, Indian): batch, streaming; numbers batch+streaming; acronyms batch+streaming; CLM batch; redaction no; Call Analytics post-call. `en-IN`: batch, streaming; redaction batch+streaming; Call Analytics post-call. Python streaming SDK: https://github.com/awslabs/amazon-transcribe-streaming-sdk (CLI not supported for streaming) — [Transcribe supported languages](https://docs.aws.amazon.com/transcribe/latest/dg/supported-languages.html)
- Streaming language identification requires at least two language codes and "only one language dialect per language per stream" — [Transcribe language ID with streaming](https://docs.aws.amazon.com/transcribe/latest/dg/lang-id-stream.html)

**Strands / AgentCore**
- Strands Agents: Python 3.10+, `pip install strands-agents` (+ `strands-agents-tools`), default provider Amazon Bedrock, minimal `from strands import Agent; agent = Agent(tools=[...]); agent("…")` — [Strands quickstart](https://strandsagents.com/docs/user-guide/quickstart/python/); [PyPI strands-agents](https://pypi.org/project/strands-agents/)
- AgentCore: "the harness in AgentCore is free of extra charge, you pay only for the underlying resources you use. New AWS customers also receive up to $200 in Free Tier credits" — [AgentCore pricing](https://aws.amazon.com/bedrock/agentcore/pricing/); third-party runtime rates ~$0.0895/vCPU-hr + $0.00945/GB-hr (v1) or $0.1276 / $0.0169 (v2) — [cloudburn](https://cloudburn.io/blog/amazon-bedrock-agentcore-pricing); [eesel](https://www.eesel.ai/blog/bedrock-managed-agents-pricing) (unverified against AWS)

**Free tier (2026)**
- Accounts created on/after July 15, 2025 choose Free or Paid plan; both start with $100 credit, up to $200 via onboarding tasks; Free plan closes when credits expire or after 6 months (one source says credits last 12 months — conflict); 30+ always-free services remain — [Rackspace Spot free-tier explainer](https://spot.rackspace.com/blog/aws-free-tier); [tech-insider](https://tech-insider.org/what-changed-in-the-aws-free-tier-for-2026/)

### Inferences
- Cost per 1,000 classifications (my arithmetic, assuming ~400 input tokens of transcript + ~50 output tokens of JSON): Nova Micro ≈ 1000 × (400×$0.035e-6 + 50×$0.14e-6) ≈ **$0.021**; Claude Haiku 4.5 ≈ 1000 × (400×$1e-6 + 50×$5e-6) ≈ **$0.65**; Nova 2 Lite ≈ $0.245. Adding one Guardrails policy (≈1 text unit per call) adds **$0.15 per 1,000 calls**. A whole hackathon demo (few hundred calls) is cents.
- "Documentable in a day" stack that reads as a pipeline rather than a single call: Transcribe streaming (`hi-IN`/`en-IN`) -> Bedrock Nova Micro structured scam-script classification (JSON: tactic, urgency, impersonation, confidence) -> Bedrock Guardrails denied-topic/PII check on the transcript -> fused with the acoustic clone score -> exposed as the MCP tool. Optional: wrap the classifier in a Strands `Agent` (one import) and note Kiro Crew usage in the feedback answer (qualifies on its own).
- Use us-east-1 for simplicity (Nova Micro in-region); from India, call via geo/global CRIS profile IDs — latency acceptable for a demo but note data leaves ap-south-1 unless the India geographic profile is used.
- Bedrock model prices were not readable on the official page in this session; cite aggregator numbers with the "verify on aws.amazon.com/bedrock/pricing" caveat.

### Gaps
- Official Bedrock per-token prices for Nova and Claude could not be extracted from aws.amazon.com (page content rendered client-side); only Guardrails figures were captured.
- Whether Nova 2 Lite/Pro or Haiku 4.5 are in-region in ap-south-1 was not confirmed (page too long; only the first section was read).
- Bedrock Guardrails standard-tier region availability for ap-south-1 not checked.
- Transcribe has no documented Hinglish code-switching mode; only per-stream language identification between `hi-IN` and `en-IN`.

---

## Key Question 6 — Amazon-published guidance on Alexa+ safety / caregiving / scam-call features to align with or cite

### Takeaway
Amazon has no published Alexa+ scam-*call* detection feature; the closest first-party items are (a) the Sept 2, 2026 **Alexa for Shopping scam-verification tool** (US-only; checks whether an email/text/WhatsApp/call claiming to be Amazon is genuine; ~360k such customer questions/yr), (b) **Alexa Emergency Assist** (paid caregiver/emergency subscription; Alexa Together discontinued), and (c) the hackathon's own "caretaking" priority (listed for Ring). Alexa+ India's Hindi/Hinglish support is the most relevant localisation hook.

### Cited Findings
- Sept 2026 Alexa for Shopping tool: users describe a suspicious communication (email, text, WhatsApp, phone call) and Alexa checks it against Amazon's record of all communications sent; returns "confirmed as official", "not appearing to be from Amazon", or "unable to verify"; every submission auto-reported to Amazon's customer protection and enforcement teams; US first, more regions later; Amazon fields ~360,000 message-authenticity questions a year; verify@amazon.com also available — [PYMNTS](https://www.pymnts.com/amazon/2026/amazon-adds-alexa-scam-protection-as-consumer-fraud-losses-rise/); [AARP](https://www.aarp.org/money/scams-fraud/amazon-alexa-shopping-fraud-detector/); [ConsumerAffairs](https://www.consumeraffairs.com/news/amazons-alexa-can-now-help-identify-scam-messages-090326.html)
- Alexa Together "is no longer available … subscribe to Alexa Emergency Assist for remote caregiver service" — [aboutamazon Alexa Together page](https://www.aboutamazon.com/news/devices/alexa-together-launches-to-help-customers-remotely-care-for-loved-ones); Emergency Assist pricing reported as $5.99/mo or $59/yr with Prime, up to 25 emergency contacts, agent can call emergency services — [Fox News](https://www.foxnews.com/tech/set-up-your-smart-speaker-emergencies); another source gives $7.99/mo or $79/yr — [Scary Mommy](https://www.scarymommy.com/parenting/whats-the-difference-between-alexa-emergency-assist-calling-911-well-a-few-things) (conflict; verify on amazon.com)
- Alexa Together (2021, historical): "Alexa, call for help" 24/7 Urgent Response, fall-detection partners Vayyar/ATS, caregiver activity feed — [TechCrunch 2021](https://techcrunch.com/2021/12/07/amazon-launches-its-19-99-per-month-alexa-together-elder-care-subscription-for-families/)
- Hackathon priority categories include "caretaking" (Ring) and "family entertainment" (Fire TV); Alexa+ "creative" examples emphasise agentic/cross-session/multimodal — [Devpost Rules](https://amazonappdev2026.devpost.com/rules)
- Alexa+ India page: "Alexa+ recognizes family members and personalizes recommendations"; privacy dashboard lets users hear what Alexa heard; no scam or caregiving features mentioned — [aboutamazon: Alexa+ in India](https://www.aboutamazon.com/news/devices/alexa-plus-international-launch)
- Alexa+ docs list "payments, and permissions" among supported capabilities for MCP add-ons (context for a future "block/transfer" action) — [Supported Capabilities](https://developer.amazon.com/docs/alexaplus/add-ons/mcp-toolkit-supported-capabilities)

### Inferences
- Positioning line that is accurate and citable: "Amazon's Sept 2026 Alexa scam-check verifies *whether a message is from Amazon*; Voice Shield extends the same 'Alexa, is this real?' gesture to *any* live call, using acoustic clone detection plus AWS-based scam-language detection, and is Hindi/Hinglish-aware for the Alexa+ India launch."
- Framing the project as caregiving (an adult child configuring it for an elderly parent's Echo) aligns with Emergency Assist's caregiver model and the hackathon's "caretaking" vocabulary.

### Gaps
- The aboutamazon.com primary announcement for the Alexa scam-verification tool was not located (only press coverage); no Amazon statement ties it to Alexa+ specifically.
- No Amazon developer guidance on safety/vulnerable-user design for Alexa+ add-ons was found beyond the (unfetched) certification guidelines page: https://developer.amazon.com/docs/alexaplus/add-ons/certification-guidelines

---

## Appendix — exact snippets worth copying

```bash
# Expose laptop server (no account needed); hostname is random per run
cloudflared tunnel --url http://localhost:8000     # prints https://<rand>.trycloudflare.com
# Alternatives
ngrok http 8000                                    # free: 3 endpoints, 1GB, 20k req, interstitial on browser hits
tailscale funnel 8000                              # ports 443/8443/10000 only; macOS needs open-source client
```

```python
# MCP Python SDK: avoid 421 "Invalid Host header" behind a tunnel, and avoid SSE (Cloudflare quick tunnels drop SSE)
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
mcp = FastMCP("voice-shield", json_response=True, stateless_http=True,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=["localhost:*", "127.0.0.1:*", "<rand>.trycloudflare.com", "<rand>.trycloudflare.com:*"]))
app = mcp.streamable_http_app()   # serve with uvicorn on :8000; endpoint path /mcp
```
(Argument names per the SDK docs cited in Q4; confirm against the installed `mcp` 2.x before relying on them.)

```text
# Minimal "simulated Alexa+" web client sequence (what the Devpost FAQ says satisfies the track)
POST /mcp  {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"VoiceShield Alexa+ Simulator","version":"0.1"}}}
POST /mcp  {"jsonrpc":"2.0","method":"notifications/initialized"}            # expect 202
POST /mcp  {"jsonrpc":"2.0","id":2,"method":"tools/list"}
POST /mcp  {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"is_this_call_real","arguments":{}}}
# headers on every request: Content-Type: application/json; Accept: application/json, text/event-stream; MCP-Protocol-Version: 2025-11-25
```

```text
# Official (gated) Alexa+ toolkit commands, for the write-up / friction log
npm install -g @alexa-ai/cli            # requires CodeArtifact login granted in private preview
alexa-ai configure
alexa-ai new mcp --name "Voice Shield" --locale en-US --mcp-server-url "https://<host>/mcp"
alexa-ai deploy
addon-local-inspector https://<host>/mcp
alexa-ai submit
```
