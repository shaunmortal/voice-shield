# Devpost "Additional info" answers (copy each block into its field)

## Upload a File
(skip, optional)

## Submitter Type
Individual (or Team, if you add teammates on Devpost)

## Organization Name
N/A

## Submitter Country of Residence
India

## Canada province
N/A

## Primary Track(s)
Alexa+

## GitHub repository URL
https://github.com/shaunmortal/voice-shield

## New or existing prior to August 31, 2026?
New

## If existing, what changed
(leave empty — new. Optional note:)
Built 21–23 Oct 2026. It reuses two MIT-licensed data files (authority-sourced Hindi/English action steps and a scam-tactic taxonomy) from our team's earlier project Digi Sanrakshak; all code in this repository is new.

## AWS Builder Mini Challenge?
No

## AWS services incorporated
Not entering. A Bedrock (Nova Micro) path for the words layer is written in content.py but our AWS account was not activated in time, so it was never run against the live service and we do not claim it.

## Open Source Mini Challenge?
Yes

## Contribution URL
https://github.com/shaunmortal/voice-shield

## Project Repository URL
https://github.com/shaunmortal/voice-shield

## GitHub Username
shaunmortal

## Open Source description
New MIT-licensed project created during the hackathon window. Voice Shield is a self-hosted MCP server (spec 2025-11-25, Streamable HTTP) that protects families from AI voice-clone scam calls. What it does: captures real SIM and WhatsApp call audio from a stock Android phone without root (scrcpy voice-call / playback --audio-dup), scores three layers (DF_Arena anti-spoof voice score, Whisper + Claude scam-language classification, and a who-speaks-when timing layer that measures reply gaps and "haan/hmm" backchannels), and exposes five MCP tools so an assistant like Alexa+ can answer "is this call real?", ask the real family member to confirm over Telegram, and give RBI/1930 next steps in Hindi. How it works: README.md, engine.py (fusion: audio alone can never raise an alert), turns.py, server.py, assistant.py (a Claude agent that uses the server only through MCP). Why it matters: voice-clone and "digital arrest" fraud cost Indian families thousands of crores; the repo also publishes reproducible evaluation code (eval.py, calltest.py) and, to our knowledge, the first real-call measurements of an open anti-spoof model on Indian VoLTE and WhatsApp calls (it fails: ≈35–40 % and ≈59 % EER), plus a 13-entry friction log, so others don't repeat our mistakes.

## Feature Requests
1. Alexa+ "trusted caller" primitive — let an add-on ask a household member to confirm on their own Alexa app with one tap ("Is this you calling Papa?"). Why: it is the one check a voice clone cannot pass; we had to build it on Telegram. Priority: Critical.
2. A consented "call companion" audio API on Android / Fire OS (or Echo-paired phones) so a safety add-on can analyse an ongoing call without scrcpy/ADB. Why: today it needs developer-mode hacks and mutes the call by default. Priority: Important.
3. Hackathon/developer sandbox access to the Alexa+ MCP client or the local inspector. Why: we had to simulate Alexa+ with our own MCP client and a Claude agent. Priority: Important.
4. Guidance in Alexa+ safety docs that voice-artifact deepfake scores are unreliable on real VoIP calls (we measured ≈59 % EER on WhatsApp). Priority: Nice-to-have.

## Friction Log (URL)
https://github.com/shaunmortal/voice-shield/blob/master/docs/friction_log.md

## Project Testing Link
https://github.com/shaunmortal/voice-shield#run-it

## Testing instructions
No credentials needed. `pip install -r requirements.txt`, `python test_engine.py`, `python test_mcp.py` (MCP 2025-11-25 handshake + all tools over Streamable HTTP), then `python server.py --source file:<any wav>` and open http://localhost:8000/. Live call capture needs an Android phone with USB debugging; Telegram verification and the Claude words layer need TELEGRAM_* / ANTHROPIC_API_KEY in .env (optional; offline fallbacks run without them).

## Feedback Q1: Which tools/APIs/SDKs and for what
- MCP Python SDK 2.x (`mcp`): the Streamable HTTP server (5 tools, structured output) and a real MCP client in assistant.py.
- Alexa+ MCP Toolkit docs: design target (Streamable HTTP, stateless, <500 ms, structuredContent + text).
- Anthropic API (Claude Opus 5.5): scam-language classification with structured JSON output, and the agent that stands in for Alexa+ and calls our MCP tools.
- Hugging Face transformers + PyTorch (MPS): DF_Arena_500M anti-spoof model; NII AntiDeepfake (ported without fairseq) for comparison.
- mlx-whisper: on-device Hindi/Hinglish transcription.
- scrcpy + adb: real SIM and WhatsApp call audio from an Android phone without root.
- Telegram Bot API: one-tap family verification.
- F5-TTS (MLX) and Chatterbox: cloning our own and a consenting friend's voice to build the test set.
- Microsoft Edge neural TTS: Alexa's spoken replies; ffmpeg for codecs, capture and video.
- Amazon Bedrock (Nova Micro): words-layer path written, not run (account activation pending).

## Feedback Q2: What worked well
- MCP spec 2025-11-25: stateless Streamable HTTP + structuredContent maps naturally onto a voice assistant; a stateless JSON-response server worked through tunnels and with our own client first time once configured.
- Claude structured output: reliable JSON every call; robust to garbled phone transcripts; tool use over MCP tool schemas needed no adapter code.
- DF_Arena_500M: one-line transformers pipeline, exposes logits (so we could calibrate), caught every clone on clean and codec audio.
- scrcpy: the only rootless path we found to real call audio; voice-call worked for SIM calls on Android 16.
- Telegram Bot API: zero setup, works from Python stdlib.

## Feedback Q3: What needs work
- MCP Python SDK 2.x: FastMCP → MCPServer rename broke every tutorial; plain dict returns rejected for structured output (TypedDict needed); DNS-rebinding 421 is cryptic behind a tunnel; Python client uses snake_case (`input_schema`, `structured_content`) unlike the wire format.
- Alexa+: no developer access for hackathon entrants, so the core integration had to be simulated; no "trusted caller" or call-safety primitives.
- Anti-spoof models: no input-constraint notes (AGC/loudness processing makes real speech look fake); none publish real VoIP/VoLTE results — on a real WhatsApp call DF_Arena reached ≈59 % EER.
- scrcpy playback capture mutes the call unless `--audio-dup`; crashes if started before audio plays; VoIP calls invisible to voice-call sources.
- Remote-code HF models: sibling modules not fetched by the dynamic loader; undeclared `einops`.
- Voice-cloning tools on Apple Silicon/8 GB: F5-TTS-MLX array-shape bug; Chatterbox watermarker/scipy breakage.
- AWS: new-account activation "up to 24 hours" blocked Bedrock on deadline day.
Full details with workarounds: docs/friction_log.md.

## Feedback Q4: Onboarding (zero to hello world)
- MCP server: ~30 min once we read the installed SDK source instead of tutorials; client + test ~20 min.
- Claude API: <10 min from key to structured JSON.
- DF_Arena via transformers: ~20 min (local snapshot workaround).
- scrcpy call capture: ~15 min to first recorded SIM call on Android 16; the WhatsApp path took ~1 h (playback + --audio-dup discovery).
- Telegram bot: 5 min. AWS Bedrock: blocked by account activation.

## Feedback Q5: Build with these again?
Yes. MCP made the "add-on for an assistant" design clean: the same server works with Alexa+, a Claude agent or any MCP client, and the Alexa+ checklist (stateless, Streamable HTTP, structured content) was a good target. Alexa is exactly where an older parent would ask "is this call real?", so we would ship this as an Alexa+ add-on the day partner access opens. We would not build on voice-artifact detection alone again; real calls taught us that.

## AI tools leveraged
Claude Code (Anthropic) as the main coding and research assistant (code, tests, evaluation scripts, research reports, video build script); Claude Opus 5.5 via the Anthropic API inside the product (scam-language classifier and the Alexa+ stand-in agent); Whisper (speech recognition); DF_Arena_500M / AntiDeepfake (anti-spoof models); F5-TTS and Chatterbox (to clone our own voices for testing); Microsoft Edge neural TTS (voices).

## Level of learning
(choose the highest option, e.g. "Significant / a lot")

## AI value for your career
Yes
