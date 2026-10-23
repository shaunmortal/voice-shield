# Devpost submission draft

**Project name:** Voice Shield
**Tagline:** "Alexa, is this really my son calling?" — live voice-clone scam defence for the family phone, as an Alexa+ MCP add-on.
**Track:** Alexa+ (self-hosted MCP server, spec 2025-11-25, Streamable HTTP) · **Mini challenge:** Open Source (MIT). Not entering AWS Builder: the Bedrock path is written but our AWS account was not activated in time, so it was never run against the live service.

## Description (what it does, how it works)

Voice-cloning scams work because the victim is alone with an urgent, familiar-sounding voice. Voice Shield puts a second opinion in the room. It listens to the phone call that is actually happening (we capture both sides of a real VoLTE call from an Android phone over USB, no root), scores every 4-second window for AI-generated speech with an open anti-spoofing model (DF_Arena_500M, XLS-R based), reads the conversation for scam pressure (urgent payment, OTP, "don't tell anyone", police/CBI threats; Amazon Bedrock Nova Micro when configured, offline keywords otherwise), and exposes the result to Alexa+ through four MCP tools. When Papa asks "Alexa, is this call real?", Alexa reports the risk in plain Hindi or English. When the caller claims to be a relative, Alexa calls `verify_with_family`, which sends "Are you calling right now?" to the real relative's phone over Telegram; a ❌ ends the scam in one tap. The voice score never decides alone: metadata and words gate, audio boosts, a human verifies, which is how shipped systems (Pixel Scam Detection, LG U+ ixi-O) are built and what FBI, FTC and RBI advisories prescribe.

We measured it honestly, on our own and a consenting friend's voice: clones are caught on simulated codecs (EER 0-9 %), but on real calls the voice detector collapses: ≈35-40 % EER over a VoLTE call and ≈59 % on a live WhatsApp call, where WhatsApp's own noise suppression makes real speech look synthetic. So Voice Shield never alerts on audio alone; the alert comes from scam language in the live transcript (Claude) or a "No" from the real family member, which survive any phone line. The demo client is a web page that is a genuine MCP client (initialize → tools/list → tools/call over Streamable HTTP) rendered as an Alexa light ring with spoken replies, because the Alexa+ MCP Toolkit is not open to hackathon entrants.

## Product feedback (required)

**MCP (Python SDK 2.x, spec 2025-11-25).** Used for the whole server. The spec is clear and `structuredContent` maps well to a voice assistant. What needs work: the SDK's 2.x rename (`FastMCP` → `MCPServer`) broke every snippet we found, including Amazon's; `dict` return types are rejected for structured output; and the DNS-rebinding guard's `421` is cryptic when you first put a tunnel in front. Onboarding: a day of reading package source. Would build with it again: yes.

**Alexa+ MCP Toolkit / Add-on docs.** Read, not used, since access is partner-only. The published requirements (Streamable HTTP, <500 ms, OAuth 2.1 with static client) were a useful design target; we hit 230 ms per window locally. Feedback: give hackathon entrants a sandbox Alexa+ client or at least the local inspector, and state in the docs which MCP SDK major version the snippets target. Would build for Alexa+ again: yes, the caretaking use case fits the device exactly.

**Amazon Bedrock (Nova Micro, Converse API).** Written as the words-layer classifier behind a feature flag but NOT run against the live service (our account's sign-up was still pending activation, "up to 24 hours", on deadline day); cost at ~₹2 per 1,000 classifications is right for an always-on home feature. Feedback: Nova Micro is us-east-1 only for Indian accounts without cross-region inference; the pricing page does not render without JavaScript.

**scrcpy (voice-call audio source).** Not an Amazon tool but the enabling one: it is the only non-root path we found to real cellular call audio, and it worked on an Oppo F25 Pro. OEM-dependent; Amazon/Ring could offer a privileged on-device hook for exactly this.

**Hugging Face anti-spoof models.** DF_Arena_500M generalised to clones it never saw; community models we tried first (and NII's small model) did not. Model cards rarely state input constraints: we lost hours to `loudnorm` making real voices look fake.

## Feature requests
- Alexa+ "trusted caller" primitive: let an add-on ask the device to confirm a household member on their own Alexa app with one tap (critical for this use case).
- Raw-ish audio access for safety add-ons on Echo devices, or a model-side AGC augmentation note (important).
- Hackathon sandbox for the Alexa+ MCP client (important).

## Friction log
See `docs/friction_log.md` (8 entries with severity, workaround and suggestion).

## Video script (≤3 min, English voice-over, Hindi dialogue on screen with subtitles)

0:00–0:15 **Hook.** Phone rings on a table. Screen: "Papa, mera accident ho gaya… abhi ₹25,000 bhej do." Caption: *This is an AI clone of my voice. It took 10 seconds of audio.*
0:15–0:35 **Problem.** ₹22,495 crore lost to cyber-fraud in India in 2025. Every advisory says "don't trust the voice, call them back." Nobody does that in a panic.
0:35–1:05 **Live demo 1.** Oppo on USB, call on. Alexa page: ring turns red within seconds, "⚠️ AI-cloned voice likely". Papa: "Alexa, is this call real?" → spoken reply.
1:05–1:40 **Live demo 2 (the moment).** "Alexa, ask Rohan if it's him." Cut to Rohan's phone: Telegram card, ❌ pressed. Alexa: "Rohan says he is NOT calling you. This is a scam. Hang up."
1:40–2:10 **How.** 15-second architecture: real call audio → anti-spoof + scam-language → MCP tools → Alexa+. Show the MCP log on the page (initialize, tools/list, tools/call).
2:10–2:40 **Honesty.** The numbers table. "Clones caught every time; the risk is false alarms on bad phone lines, so audio never decides alone."
2:40–3:00 **Close.** Open source, MIT, runs on a laptop today, belongs in the Echo tomorrow. Repo link.
