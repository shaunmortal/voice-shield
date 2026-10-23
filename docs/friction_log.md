# Friction log

Format per entry: task · steps · expected vs actual · severity · workaround · suggestion.

## 1. MCP Python SDK 2.x renamed FastMCP
- **Task:** build the Streamable HTTP server with the official `mcp` package.
- **Steps:** `pip install mcp`, `from mcp.server.fastmcp import FastMCP` as every tutorial and the hackathon snippets show.
- **Expected:** import works. **Actual:** `ModuleNotFoundError` with a pointer to a migration guide; the class is now `mcp.server.mcpserver.MCPServer`, and a plain `dict` return type is rejected for `structured_output=True` (needs `TypedDict`).
- **Severity:** medium (30 min).
- **Workaround:** read the installed package source; declare `TypedDict` result shapes.
- **Suggestion:** Amazon's Alexa+ MCP docs should state which SDK major version their snippets target.

## 2. Cloudflare quick tunnel + SSE
- **Task:** expose the laptop server over HTTPS for the web MCP client.
- **Expected:** default Streamable HTTP (SSE responses) works through `cloudflared tunnel --url`. **Actual:** quick tunnels do not pass SSE; Python SDK also returns `421 Invalid Host header` until the tunnel hostname is added to `allowed_hosts`.
- **Severity:** medium.
- **Workaround:** `json_response=True, stateless_http=True`, `PUBLIC_HOST` env var in `TransportSecuritySettings`.
- **Suggestion:** document `json_response` mode as the recommended dev path in the Alexa+ MCP QuickStart.

## 3. Hugging Face remote-code model with relative imports
- **Task:** load `Speech-Arena-2025/DF_Arena_500M_V_1` through `transformers.pipeline(..., trust_remote_code=True)`.
- **Expected:** one-line load as on the model card. **Actual:** `FileNotFoundError: conformer.py` (the dynamic loader fetched the entry module but not its sibling imports); also needs `einops` that is not declared.
- **Severity:** low-medium (20 min).
- **Workaround:** `snapshot_download` the whole repo and load from the local path.

## 4. Loudness normalisation poisons anti-spoof scores
- **Task:** build the bona fide (real voice) set from Voice Memos recordings that were too quiet (mean -42 dBFS).
- **Steps:** `ffmpeg -af loudnorm` → score with DF_Arena.
- **Expected:** gain does not change "real vs fake". **Actual:** the same speech went from logit margin -11 (clearly real) to +4.6 at the 90th percentile (looks synthetic); 2 of 4 real recordings raised a call-level alert. Static gain (`volume=12dB`) does not do this.
- **Severity:** high (would have shipped a detector that flags real people).
- **Workaround:** static gain only; never dynamic processing before the detector.
- **Suggestion:** anti-spoof model cards should list "do not apply AGC/loudnorm" as an input constraint; Alexa devices apply AGC on far-field mics, so an Alexa+ voice-safety add-on needs raw-ish audio or a model trained with AGC augmentation.

## 5. Softmax saturation hides calibration
- **Task:** set an alert threshold. **Actual:** every clone scored exactly 1.000 and real speech up to 0.99, so `p > 0.5` is meaningless. **Workaround:** score on logit margin, calibrate shift/scale on our own data. **Suggestion:** expose logits in the pipeline output (DF_Arena does, most HF audio-classification models do not).

## 6. Voice-cloning tools on Apple Silicon / 8 GB
- `f5-tts-mlx 0.2.6` crashes with `mx.random.normal(... dur)` because `dur` is an array → patched `int(dur)`; also requires a 24 kHz reference and the error only appears after model download.
- `chatterbox-tts` on Python 3.10: scipy wheel fails to `dlopen` on macOS 27 (pin scipy 1.13.1); `perth` watermarker constructor is `None` → monkey-patch `DummyWatermarker`. ~2 min per Hindi sentence on M1.
- Running a cloner and the detector at the same time freezes an 8 GB machine; one large model at a time.
- **Severity:** medium (≈1.5 h total).

## 7. Commercial clone tiers
- ElevenLabs: instant voice clone requires a paid plan ($1 first month). Fish Audio: free tier only allows *public* voices (your voice becomes usable by anyone). We refused both; the test set therefore has two local clone families (F5-TTS, Chatterbox) and no commercial family. **Suggestion for the ecosystem:** a privacy-preserving "clone my own voice for testing" tier would let defenders build evaluation sets without publishing their voice.

## 8. Phone-call capture
- `scrcpy --audio-source=voice-call` on Oppo F25 Pro (ColorOS 16 / Android 16) returns both sides of a VoLTE call as a mixed mono stream (left=right); earlier Android/OEM builds return silence. Developer options needed "Disable permission monitoring" and USB mode "File transfer". macOS has no `timeout` binary; use `--time-limit`.
- Whisper transcription of a quiet Hindi/Hinglish reference clip hallucinated until the clip was amplified; `language=None` (auto) gave the correct English transcript where `language='hi'` produced garbage Devanagari.

## 9. Android playback capture mutes the call (scrcpy)
- **Task:** capture the remote side of a WhatsApp call digitally (no loudspeaker). **Steps:** `scrcpy --audio-source=playback`.
- **Expected:** a copy of the call audio. **Actual:** it worked, but the call went silent on the phone, so the user thought the call had dropped; `voice-call*` sources return silence for VoIP calls; starting the capture before any audio plays crashes scrcpy (exit 139).
- **Severity:** high (looked like a broken call). **Workaround:** `--audio-dup`; start capture only once the call is connected.
- **Suggestion (for Alexa/Echo + phone integrations):** a documented, consented "call companion" audio API on Android/Fire OS would remove this whole class of hacks.

## 10. Codec simulation is not channel simulation
- **Task:** estimate detector accuracy on WhatsApp calls. **Steps:** ffmpeg Opus 24 kb/s round-trip → EER 0 %. Then a real WhatsApp call with a consenting friend → ≈59 % EER (live human scored more synthetic than his clone).
- **Expected:** the codec drives the degradation. **Actual:** WhatsApp's noise suppression / AGC does; we had already seen loudness normalisation flip real speech to "synthetic".
- **Severity:** critical for anyone shipping voice-deepfake detection. **Workaround:** audio alone may only say "verify"; alerts need words, timing or human confirmation.
- **Suggestion:** benchmark suites (and Alexa+ safety guidance) should include real VoIP-app recordings, not only codec round-trips.

## 11. Telegram inline buttons feel dead under polling
- **Task:** "Are you calling right now? ✅/❌" for the family member. **Actual:** inline-keyboard taps spin until the bot answers the callback, so the user kept tapping and thought it was broken; one long-poll request hung and swallowed the answer.
- **Severity:** medium. **Workaround:** reply keyboard (the tap becomes a visible chat message) + short polling with retry.

## 12. MCP Python SDK 2.x field names
- `mcp.Client.list_tools()` returns tools with `input_schema` (snake_case) and `call_tool` returns `structured_content` / `is_error`, while the JSON wire format and most docs say `inputSchema` / `structuredContent` / `isError`. **Severity:** low (one AttributeError). **Suggestion:** note the Pythonic field names in the migration guide.

## 13. Alexa+ add-on tools are partner-only
- **Task:** test Voice Shield inside real Alexa+ (Web Simulator / Local Inspector) and deploy it as an add-on.
- **Steps:** read the Alexa+ MCP Toolkit QuickStart, looked for the `alexa-ai` CLI and simulator sign-up, checked the hackathon FAQ.
- **Expected:** a sandbox or simulator for hackathon entrants. **Actual:** the Category SDK, MCP Toolkit, CLI and Web Simulator are "available to select partners only", with no way to apply.
- **Severity:** critical (the track's target platform cannot be tested end to end).
- **Workaround:** built to the published checklist (2025-11-25, Streamable HTTP, structuredContent, measured 1-3 ms vs the 500 ms limit), wrote `alexa/addon.json` in the QuickStart format, and simulated Alexa+ with a real MCP web client plus a Claude agent that reaches the server only through MCP; also verified with Claude Code as a second MCP client.
- **Suggestion:** give hackathon entrants time-limited Web Simulator access, or publish the Local Inspector so add-ons can be validated against Alexa+'s real MCP client before partner approval.
