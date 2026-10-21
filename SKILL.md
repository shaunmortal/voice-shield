---
name: voice-shield
description: Check whether the voice on a live phone call is AI-cloned, read the scam-language risk, and verify the caller with the real family member over Telegram. Use when a user asks "is this call real?", "is it really my son?", or "is this a scam?".
---

# Voice Shield

Voice Shield is an MCP server (spec 2025-11-25, Streamable HTTP, endpoint `/mcp`). Connect with a stateless client; every tool returns `structuredContent` plus a text block with the same JSON.

## Tools, in the order to call them

1. `get_call_status()` → `{level, risk, speech_seconds, audio_live, say}`
   `level` is `listening | safe | suspicious | alert`. `say` is a sentence you can speak as-is. Never tell the user a voice is *definitely* fake: `risk` is a calibrated probability on 4-second windows, and narrowband codecs raise it for real people too.
2. `verify_with_family(claimed_person, reason)` → `{answer, say}`
   Sends "are you calling right now?" to the real person's phone and waits up to 25 s. Call it whenever the caller claims to be a relative and asks for money, an OTP or secrecy, whatever the voice score says. `answer` is `yes | no | no_answer | unconfigured`.
3. `get_alert_history(limit)` → recent alerts for the family or a report.
4. `reset_call()` when the call ends.

## Rules for the assistant

- A high voice score alone only means "unverified caller": ask the family secret word or run `verify_with_family`; do not tell the user to hang up on audio alone.
- A `no` from `verify_with_family`, or scam language (urgent payment, OTP, "don't tell anyone", police/CBI threats), means: do not pay, hang up, call back on the saved number, report at cybercrime.gov.in or 1930.
- Keep spoken replies under two sentences; Hindi/Hinglish when the user speaks it.
