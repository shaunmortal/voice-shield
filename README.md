# Voice Shield — "Alexa, is this really my son calling?"

**Alexa+ track · Amazon Developer Hackathon 2026 · self-hosted MCP server (spec 2025-11-25, Streamable HTTP)**

A scammer clones your voice from a 10-second Instagram clip, calls your father and says *"Papa, mera accident ho gaya, abhi ₹25,000 bhej do, kisi ko mat batana."* Voice Shield listens to the **real SIM call** on the phone, scores the voice for AI-generation, reads the conversation for scam pressure, and, the part no clone can beat, **asks the real son on his own phone: "Are you calling right now?"** Alexa+ then tells Papa what to do.

> India reported ₹22,495 crore of cyber-fraud losses in 2025; "digital arrest" alone peaked at 1.24 lakh complaints in 2024. Every official advisory (FBI, FTC, RBI, Indian police) says the same thing: *don't trust the voice, call them back.* Voice Shield automates exactly that advice.

## What it does

```
 📞 live SIM call (Oppo, no root)     🎙️ laptop mic / 📁 clip
          └──────── 16 kHz PCM via ffmpeg ────────┘
                           │
        ┌──────────────────┼──────────────────────┐
  Layer 1: voice      Layer 2: words        Layer 0: caller
  DF_Arena_500M       scam-pressure         metadata (unknown /
  anti-spoof, 4 s     classifier (Bedrock   international number)
  windows, 3-of-5     Nova Micro or
  consensus           offline keywords)
        └──────────────────┼──────────────────────┘
                           ▼
                 MCP server  /mcp  (4 tools)
                           ▼
    Alexa+ (simulated web client, speaks Hindi/English)
                           ▼
  Layer 3: verify_with_family → Telegram "Are you calling?" ✅/❌
```

**Fusion rule (`engine.fuse`):** words risk ≥ 0.6 → alert; words ≥ 0.3 *and* voice alert → alert; voice alone → at most suspicious. A human decides via `verify_with_family`. The voice score alone never tells the user to hang up; it tells them to verify.

## MCP tools

| Tool | Returns | Alexa+ use |
|---|---|---|
| `get_call_status()` | `level` (listening/safe/suspicious/alert), calibrated `risk`, `say` | "Alexa, is this call real?" |
| `verify_with_family(claimed_person, reason)` | `answer` yes/no/no_answer + `say` | "Alexa, ask Rohan if it's him" → button on Rohan's phone |
| `get_alert_history(limit)` | recent alerts | "Alexa, were there scam calls this week?" |
| `reset_call()` | — | call ended |

All tools return `structuredContent` plus a text block, the shape Alexa+'s MCP client expects. `SKILL.md` teaches any agent how to use them.

## Run it

Needs macOS/Linux, Python 3.12+, ffmpeg, ~3 GB disk for the model (downloaded on first run).

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python test_engine.py        # detector self-check (synthetic → alert, silence → nothing)
.venv/bin/python test_mcp.py           # MCP 2025-11-25 handshake + tools over Streamable HTTP
.venv/bin/python server.py --source file:demo.wav   # replay a clip
.venv/bin/python server.py --source mic             # call on speakerphone, laptop listens
.venv/bin/python server.py --source phone           # live SIM call from a USB-connected Android (scrcpy)
```
Open **http://localhost:8000/** — the page is a real MCP client (initialize → tools/list → tools/call) rendered as an Alexa light ring with spoken replies. Press *"Alexa, is this call real?"* and *"Alexa, ask Rohan if it's him"*.

Public HTTPS for a remote client: `cloudflared tunnel --url http://localhost:8000`, then restart with `PUBLIC_HOST=<name>.trycloudflare.com`. The server runs in JSON-response, stateless mode because quick tunnels do not pass SSE.

Optional: `.env` with `TELEGRAM_BOT_TOKEN` / `TELEGRAM_FAMILY_CHAT_ID` (family verification) and AWS credentials (`AWS_ACCESS_KEY_ID`…) to route the words layer through **Amazon Bedrock Nova Micro** (code path written, not yet run against the live service); without them the words layer uses an offline keyword classifier, and only transcript text ever leaves the device, never audio.

### Live SIM call capture (Android, no root)
`scrcpy --audio-source=voice-call` returns both sides of a VoLTE call on **Oppo F25 Pro / ColorOS 16 / Android 16** with USB debugging on ("Disable permission monitoring" + USB mode *File transfer*). Many other OEM builds return silence; the engine is source-agnostic, so the mic path works everywhere. Production would move the same engine into an OEM dialer or carrier IMS layer, as Google's Pixel Scam Detection and LG U+ ixi-O do.

## The numbers (measured, our own voice)

Test set: one consenting team member's voice (bona fide, 4 recordings, 512 four-second windows) versus clones of that voice made with two open tools on the same laptop, **F5-TTS** (MLX) and **Chatterbox-Multilingual** (Hindi + English), reading scam scripts from `data/scripts.txt`. Channel conditions simulated with ffmpeg (`eval.py`).

| Condition | EER | TPR @ 1 % FPR | real-call false alarms (3-of-5 consensus) |
|---|---|---|---|
| Clean 16 kHz | **0.0 %** | 100 % | 0 / 4 |
| Band-limited 300–3400 Hz | 0.8 % | 90 % | — |
| G.711 µ-law (landline) | 1.2 % | 90 % | 0 / 4 |
| Opus narrowband 12 kb/s | **8.9 %** | 80 % | **3 / 4** |
| **Real VoLTE call** (laptop speaker → friend's phone → Jio/Airtel network → our Oppo, captured by scrcpy) | **≈ 35–40 %** | 0 % | 2 / 3 (audio alone) |

Read these honestly:
- **On simulated codecs the detector works; on a real phone call it does not.** Played over the air into a real call, clone scores fell from 0.95 to ≈0.45 and real speech rose to ≈0.30, so the two overlap. This matches the literature (SAFE 2025: over-the-air re-recording is the most damaging condition) and it is the most important number in this README.
- So the design does not trust audio: **the voice layer alone can only raise "suspicious" ("verify this caller"), never "alert".** An alert needs scam language in the live transcript (Whisper on-device → scam classifier) or a ❌ from the real family member. Both of those work identically on a bad phone line, because a clone can copy a voice but not the script it must say or the button on the real son's phone.
- Two clone families are *seen* only in the sense that we chose the calibration on them; the model was not trained on them. Published results for unseen 2024-era generators are 25–33 % EER and 40–50 % on multilingual in-the-wild sets that include Hindi ([Deepfake-Eval-2024](https://arxiv.org/abs/2503.02857), [ML-ITW](https://arxiv.org/abs/2603.05852)). Real-time voice conversion (RVC/Seed-VC) was not tested.
- Model swap evidence: NII AntiDeepfake-Small (ported without fairseq in `antideepfake.py`) scored our own voice 0.00 but **missed** the F5 clones (0.02–0.47); DF_Arena_500M caught them all, so it is the live model.
- `ffmpeg loudnorm` on the real recordings turned them "synthetic" (logit margin −11 → +4.6). Static gain only. Details in `docs/friction_log.md`.
- Latency on M1 (8 GB): ~230 ms per 4 s window on MPS, 1 s hop → first alert 3–5 s after cloned speech starts.

## Privacy

Audio is processed on the laptop and discarded after each window; only aggregate risk events are kept. The remote caller's voice is personal data under India's DPDP Act, so no audio is uploaded; the optional Bedrock call receives transcript text only. The clone test set was made from the author's own voice with consent; we declined services that required publishing the voice model.

## What was built during the hackathon

Everything in this repository (21–23 Oct 2026). The idea descends from our SIH 2026 problem-statement design (voice-clone detection on cellular calls), of which no code survived; the capture path, detector evaluation, MCP server, Alexa+ client, Telegram verification and scam-language layer are new.

## Licenses

Code: MIT. Model weights are downloaded at runtime and keep their own licenses: `Speech-Arena-2025/DF_Arena_500M_V_1` (non-commercial), `nii-yamagishilab/wav2vec-small-anti-deepfake` (CC BY-NC-SA 4.0, evaluation only). Clone tools used for testing: F5-TTS (CC BY-NC weights), Chatterbox (MIT).
