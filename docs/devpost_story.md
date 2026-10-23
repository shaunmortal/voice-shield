## Inspiration
"Papa, mera accident ho gaya hai, abhi pachaas hazaar bhej do, kisi ko mat batana." With 10 seconds of someone's voice, anyone can now make that call. India lost about ₹22,495 crore to cyber fraud in 2025, and every advisory (FBI, FTC, RBI, Indian police) gives the same advice: *don't trust the voice, call the person back.* In a panic, nobody does. We wanted the assistant already sitting in Indian living rooms to do it for them, in Hindi.

## What it does
Voice Shield is a self-hosted **MCP server (spec 2025-11-25, Streamable HTTP)** for Alexa+. While a parent is on a phone or WhatsApp call, it:
- **listens to the real call**: both sides of a SIM (VoLTE) call, or the remote side of a WhatsApp call, captured from a stock Android phone with no root (Oppo F25 Pro, Android 16, via scrcpy `voice-call` / `playback --audio-dup`);
- scores three independent layers: **voice** (DF_Arena_500M anti-spoof, 4 s windows, 3-of-5 consensus), **words** (on-device Whisper transcript → Claude with structured output, classifying scam pressure: urgent money, OTP, secrecy, police/CBI threats), and **timing** (who speaks when: caller reply gap and "haan/hmm" backchannels);
- exposes it as 5 MCP tools: `get_call_status`, `verify_with_family`, `what_should_i_do`, `get_alert_history`, `reset_call`.

So Papa can just ask: *"Alexa, mera beta bol raha hai accident ho gaya, ye call asli hai kya?"*, and Alexa can **ask the real son on his own phone** (Telegram: "Are you calling right now? ✅/❌"). A clone can copy a voice; it cannot press the button on the real son's phone. If money already went, *"Alexa, maine das hazaar bhej diye, ab kya karun?"* returns the RBI / 1930 / cybercrime.gov.in steps in Hindi, fixed text from official guidance, never generated.

Since Alexa+ developer tools are partner-only, our demo client is a web page that is a **real MCP client**, plus a **Claude agent standing in for Alexa+**: it discovers our tools over MCP (`tools/list`), picks and calls them (`tools/call`) from spoken Hindi, and answers in a natural voice. Nothing in that agent imports our engine; it only speaks MCP.

## How we built it
Python, the official `mcp` SDK 2.x (stateless, JSON-response mode so it works through Cloudflare tunnels), PyTorch on Apple MPS, Hugging Face transformers, mlx-whisper, the Anthropic SDK (Claude Opus 5.5 with structured JSON output), the Telegram Bot API, and Microsoft Edge neural TTS for the voice. Everything runs on one 8 GB M1 MacBook Air. We built our own test set by cloning our own (and a consenting friend's) voice with F5-TTS and Chatterbox, then played it through simulated codecs and through **real calls**.

## What we learned (the honest part)
We measured instead of assuming:

| Channel | EER |
|---|---|
| Clean audio | 0.0 % |
| G.711 / Opus codecs (simulated) | 1.2 % / 8.9 % |
| Real VoLTE call (clone played from a speaker) | ≈ 35-40 % |
| **Real WhatsApp call, live human vs clone** | **≈ 59 %** |

Voice-artifact detection **does not survive real calls**. On WhatsApp it even rated a live human as more synthetic than his clone: WhatsApp's own noise suppression and gain control make real voices look fake (we had measured the same effect from loudness normalisation). Codec simulation is not channel simulation. We found no published number for real Indian VoLTE or WhatsApp calls in Hindi; these are ours.

That result shaped the product: **audio alone can never raise an alert.** It only says "verify". Alerts come from scam language in the transcript (Claude scored an ordinary "Didi, put ₹5,000 in my account, I'll return it Sunday" at 0.10 and still flagged a garbled "police case… paise… jaldi" fragment at 0.55), from bot-like timing, or from the real family member saying No. On a live WhatsApp call our friend said "haan/hmm" 7 times while answering himself and 0 times when replying with his clone, and his reply gap grew.

## Challenges
Getting real call audio without root (only `playback` capture works for WhatsApp, and by default it mutes the call until you add `--audio-dup`); Telegram inline buttons that felt "dead" until we switched to a reply keyboard; Whisper failing on narrowband Hindi; and accepting that our first headline number (0 % on simulated WhatsApp-style audio) was wrong once we tested a real call. Details in `docs/friction_log.md`.

## Accomplishments we're proud of
Real SIM and WhatsApp call audio into an MCP server on a stock phone; an end-to-end flow where a clone is defeated by one tap from the real person; the first real-call measurements we know of for Hindi voice clones; and a submission that reports its failures.

## What's next
Ship as an Alexa+ add-on when partner access opens (we designed to its published MCP Toolkit checklist); move capture into an OEM dialer or carrier IMS layer; fine-tune the voice layer on real WhatsApp/VoLTE audio with live-speaker data; family safe-word and caller-ID mismatch signals.

## Built on
Our team's earlier MIT project **Digi Sanrakshak** (scam decision assistant) supplied the authority-sourced Hindi/English action steps and the scam-tactic taxonomy.

Code (MIT): https://github.com/shaunmortal/voice-shield
