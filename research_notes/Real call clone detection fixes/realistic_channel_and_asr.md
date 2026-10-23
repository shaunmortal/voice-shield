# Realistic delivery channel for voice-clone scam calls, and ASR for degraded Hindi/Hinglish call audio (as of Oct 2026)

## 1. How do voice-clone scammers actually deliver audio, and what does the channel do to it?

### Takeaway
The evidence points to digital paths. Indian voice-clone "family emergency" cases mostly arrive as **WhatsApp voice calls** from new accounts using the impersonated person's profile photo. That is internet audio, Opus-coded. Digital-arrest and organised vishing traffic is usually **VoIP terminated onto Indian mobile numbers through SIM boxes/GSM gateways**, so the victim hears a normal mobile call: VoIP codec first, then the carrier codec (AMR-NB/AMR-WB/EVS) on the last leg. I found no source describing scammers playing clones from a loudspeaker into a second phone. The team's laptop-speaker → phone-mic → call path adds a room/loudspeaker/mic replay stage that real attacks don't have, so it is **not representative** and is a pessimistic worst case.

### Cited Findings
- Mumbai, 69-year-old lost ₹50 lakh after a **WhatsApp call** from an unfamiliar number showing the impersonated person's profile photo. Police *suspect* an AI-cloned voice; this is not confirmed. — [The420.in](https://the420.in/mumbai-senior-citizen-50-lakh-ai-voice-cloning-scam/)
- Commentary on the same pattern says clone calls "increasingly arrive on WhatsApp from freshly created accounts wearing a stolen profile photo." This is a blog-level source. — [mayankdigitallabs](https://www.mayankdigitallabs.in/blog/ai-scam-calls-voice-cloning-2026)
- Thane police arrested a woman who used an AI-generated male voice on calls to dupe a neighbour of over ₹6 lakh. — [Tribune India](https://www.tribuneindia.com/news/india/woman-dupes-female-neighbour-of-over-rs-6-lakh-by-using-artificial-intelligence-to-create-male-voice-during-calls-635196)
- Tamil Nadu Police: scammers take voice samples from social media posts, or from a "wrong-number" call with the target, then call people in the target's contact list asking for urgent money. — [DT Next via PressReader](https://www.pressreader.com/india/dt-next/20240428/281621015402986)
- Digital-arrest offenders make audio or video calls posing as law enforcement, "frequently … using AI-generated voices or video technology." — [Outlook Money](https://www.outlookmoney.com/news/digital-arrest-scam-man-arrested-for-duping-ex-army-officer-of-rs-78-lakh)
- **SIM boxes**: Tamil Nadu Cyber Crime Wing seized 44 SIM boxes in two months (Sept–Oct 2025). Of these, 14 Quectel SIM boxes were seized in Chennai and 24 "modified SIM boxes" in Delhi. They were "designed to mask international calls as domestic ones" for digital-arrest scams run by international cybercrime compounds. — [The420.in](https://the420.in/tamil-nadu-cybercrime-simbox-delhi-digital-arrest-scam/)
- Police describe SIM boxes as converting internet calls into local mobile calls to bypass telecom tracking. One Dehradun device held up to 256 SIMs. A Chandigarh syndicate (10 arrested, Aug 2025) was run from Cambodia/Laos/Myanmar. A CBI case in Meerut seized 180 SIMs used for VoIP fraud. — [The Week](https://www.theweek.in/wire-updates/national/2025/08/01/des85-ch-scam-bust.html); [Daily Pioneer](https://www.dailypioneer.com/news/meerut-cbi-busts-voip-fraud-180-sim-cards-seized)
- Digital-arrest cases reported to Parliament (Mar 2025): 39,925 in 2022 and 123,672 in 2024, with ₹1,935.51 crore lost in 2024. This is a secondary report. — [Moneylife](https://moneylife.in/article/fraud-alert-india-is-losing-over-22000-crore-a-year-in-cyber-scams-and-the-worst-is-yet-to-come/80612.html)
- Academic taxonomy (PITCH): phone scams fall into robocalls, replayed voices, automated voice chatbots, and **real-time voice conversion**, the most targeted type. — [arXiv 2402.18085](https://arxiv.org/pdf/2402.18085)
- NCC Group red-team work: real-time voice conversion on a consumer laptop with about 0.5 s delay, combined with caller-ID spoofing, was used in consented vishing exercises. The voice-changer output is fed to the calling software, not played acoustically. — [IEEE Spectrum](https://spectrum.ieee.org/real-time-audio-deepfake-vishing); [NCC Group PDF](https://www.nccgroup.com/media/zw5iy13i/voice-impersonation-and-deepfake-vishing-in-realtime.pdf)
- Vendors publish guides for routing a voice changer into **WhatsApp Desktop** calls through a virtual audio device (BlackHole on Mac). This shows the digital-injection workflow is commodity knowledge. — [VoxBooster (vendor blog)](https://voxbooster.com/blog/voice-changer-whatsapp-video-desktop)
- Pindrop's telephony data, from contact centres over 1.2B calls, shows deepfake attempts rising from about 1/month to 7/day in 2024. Pindrop flags Zoom/Teams-style real-time platforms as the next frontier. The headline growth figure is inconsistent: +1,300% in the press release vs +680% on its web summary. — [Pindrop report PDF](https://www.pindrop.com/wp-content/uploads/2025/07/Voice-Intelligence-and-Security-Report-Report-June-2025.pdf); [CIO Influence](https://cioinfluence.com/security/pindrops-2025-voice-intelligence-security-report-reveals-1300-surge-in-deepfake-fraud/)
- McAfee (2023, 7 countries): 47% of Indian adults had experienced, or knew someone who experienced, an AI voice scam (global 25%). 83% of Indian victims lost money. — [McAfee report](https://www.mcafee.com/content/dam/consumer/en-us/resources/cybersecurity/artificial-intelligence/rp-beware-the-artificial-impostor-report.pdf); [BOOM](https://www.boomlive.in/explainers/ai-voice-scam-voice-cloning-mcafee-report-21851)
- **Channel effects on detectors:** ASVspoof 5, which has a Track 2 telephony/VoIP scenario, found that detection "degrades under … neural encoding/compression." One system went from about 1.17% EER clean to severe degradation under Speex 8 kHz and MP3+Encodec, with moderate degradation under Opus 8 kHz. — [ASVspoof 5 overview](https://arxiv.org/html/2601.03944v1); [Vicomtech-UGR arXiv 2408.10361](https://arxiv.org/pdf/2408.10361)
- In another ASVspoof 5 study, noise, RIR and RawBoost augmentation helped more than codec augmentation. Adding 8 kHz resampling as augmentation made EER worse in that table. — [arXiv 2507.01750](https://arxiv.org/pdf/2507.01750)
- EVS is the 3GPP successor to AMR-WB for VoLTE/VoNR and has an AMR-WB interoperable mode. — [Fraunhofer IIS](https://www.iis.fraunhofer.de/en/ff/amm/communication/evs.html)

### Inferences
- **Path A, WhatsApp/OTT call** (the most common reported vector for India "relative in trouble" clones). The chain is clone TTS/VC → virtual audio device or phone → Opus at a variable bitrate. Opus usually stays wideband (16 kHz) when bandwidth allows, with packet-loss concealment and jitter artefacts. There is no carrier codec. The detector sees relatively good-quality audio, so this is the **easiest realistic case**.
- **Path B, SIM-box/VoIP termination onto a mobile number** (digital-arrest style). The chain is softphone/dialer → SIP (G.711/G.729/Opus) → GSM gateway → carrier. If the gateway places 2G/3G calls, the last leg is **AMR-NB, 8 kHz, about 300–3400 Hz**, possibly with transcoding twice. This is the **hardest realistic case**. VoLTE-to-VoLTE between Indian subscribers would usually be AMR-WB (16 kHz) or EVS. I found no confirmation of which codec Jio or Airtel use by default.
- **Path C, call from the scammer's own phone** with a clone played from a laptop speaker into the handset. This is the only path matching the team's setup. I found no evidence it is a common technique, and it is plausibly used only by low-skill actors. Treat it as a stress test, not the main benchmark.
- The 35–40% EER collapse is likely dominated by the **acoustic replay plus double-mic plus room stage** in the team's setup. Replay is a separate attack class (ASVspoof "physical access") from codec degradation. The garbage Whisper output is also consistent with two acoustic hops plus a narrowband call leg.
- On top of channel realism, the detector needs codec, noise and RIR augmentation in training. Do not just add 8 kHz resampling (see the 2507.01750 finding).

### Gaps
- I found no I4C or CERT-In primary advisory that specifies the technical delivery mechanism, such as virtual audio cable or real-time voice changer, for voice-clone calls. The "I4C 2025 advisory on voice cloning" appears only in blogs, so it is unverified.
- I found no Hiya 2025 India-specific report.
- I found no source on Indian carriers' default VoLTE codec (AMR-WB vs EVS) or SIM-box last-leg codec.
- I found no study measuring the share of clone calls that are live voice conversion vs pre-generated TTS clips.

## 2. Most realistic test setup a student team can reproduce in a few hours

### Takeaway
Remove the acoustic hop. Inject the clone audio **digitally** into a real call and record the receiving phone's output digitally. In priority order:
1. Mac → **BlackHole → WhatsApp Desktop** call to the test phone. This matches the dominant India clone vector (Opus). It is free and takes about 30 min.
2. Mac line-out → **TRRS cable / USB audio adapter into an Android phone's mic input** on an ordinary carrier call to the test phone. This gives the real carrier codec (AMR-NB/WB/EVS) with no room acoustics.
3. **Offline codec simulation** with ffmpeg (AMR-NB 8 kHz, Opus 8/16 kHz, G.711 µ-law) for bulk evaluation and training augmentation.

Keep the current loudspeaker path as a labelled "replay worst case" row, not the headline number.

### Cited Findings
- BlackHole is a free, open-source macOS virtual audio driver that passes audio between apps with zero added latency. macOS has no built-in virtual audio device. — [BlackHole GitHub](https://github.com/lucyalynch/BlackHole)
- The WhatsApp Desktop routing recipe is: install BlackHole 2ch, create a Multi-Output Device in Audio MIDI Setup (headphones + BlackHole) to monitor, send the player's output to BlackHole 2ch, then in WhatsApp Desktop → Settings choose BlackHole 2ch as the microphone. Use the Desktop app; Safari blocks virtual mics by default. — [VoxBooster guide (vendor)](https://voxbooster.com/blog/voice-changer-whatsapp-video-desktop)
- Loopback by Rogue Amoeba is the paid alternative (about $100+). — [Daily Dev Tips](https://daily-dev-tips.com/posts/streaming-desktop-sound-and-microphone-on-mac-with-streamlabs)
- ASVspoof 5's codec conditions (Opus 8 kHz, Speex 8 kHz, MP3, Encodec) are the published reference set for channel-degraded evaluation. — [ASVspoof 5 overview](https://arxiv.org/html/2601.03944v1)

### Inferences (recommended protocol; not from a single source)
- **Setup 1, WhatsApp/Opus (about 30 min):**
  - Install BlackHole 2ch (`brew install blackhole-2ch`).
  - Play clone and bona fide WAVs with `afplay` or ffmpeg, output to BlackHole.
  - Set WhatsApp Desktop's mic to BlackHole and call the test phone's WhatsApp.
  - On the receiving side, the cleanest capture is a second Mac or PC running WhatsApp Desktop, recording its output with BlackHole + QuickTime/ffmpeg. That keeps capture digital as well.
  - If capture must be on the phone, use Android's built-in call recorder or screen recorder with internal audio where available. Note that many Android builds block call-audio capture, and iOS does not allow it at all.
- **Setup 2, carrier call (about 1 h, needs a ₹200–500 cable):**
  - Connect the Mac headphone-out through a TRRS "line-to-mic" attenuator cable, or a USB-C audio adapter with a mic input, into an Android phone. Set the level low to avoid clipping.
  - Place a normal SIM call to the test phone. The audio then crosses the real AMR/EVS chain with no room acoustics.
  - Record on the receiving phone with its built-in call recorder (common on Indian Android OEMs, e.g. Google Dialer in India), or by wiring the receiver's headphone-out into the Mac's input.
  - This is the closest legal stand-in for SIM-box/VoIP termination.
- **Setup 3, simulated channel (minutes, scalable):**
  - `ffmpeg -i in.wav -ar 8000 -ac 1 -c:a libopencore_amrnb -b:a 12.2k out.amr`, then decode back to WAV. This requires an ffmpeg built with opencore-amr; Homebrew's ffmpeg may need a tap that includes it.
  - Also produce `-c:a libopus -b:a 12k -ar 16000`, `-c:a libopus -b:a 8k -ar 8000`, and `-ar 8000 -c:a pcm_mulaw`.
  - Chain two codecs (e.g. Opus 16k → G.711 → AMR-NB) to mimic SIP-to-GSM transcoding.
  - Use these both to report EER per channel and as training augmentation.
- **Report EER per channel:** clean / Opus-WhatsApp / carrier-call / simulated AMR-NB / loudspeaker-replay. Run bona fide speech from the same speakers through the same channel, or the detector will learn "channel = fake."
- **Ethics and legality:** only call phones owned by the team, with consent from the voice donors. Use no caller-ID spoofing and no third-party numbers. Do not use call forwarding to VoIP numbers or SIP trunks terminating on Indian mobiles; that is effectively the regulated SIM-box/ILD path and is unnecessary.

### Gaps
- I did not verify that the current WhatsApp Desktop for Mac accepts BlackHole as a mic after recent updates; it is reported only by a vendor blog.
- I found no source on Android's "play audio into call" API limits. The common understanding is that third-party apps cannot inject audio into the cellular uplink without root or system privileges, but I have no citation for this.
- I found no citable number for the codec WhatsApp uses on Indian mobile networks.

## 3. Best on-device or low-cost ASR for noisy narrowband Hindi/Hinglish phone audio on an Apple M1 8 GB

### Takeaway
Off-the-shelf Whisper is genuinely poor on 8 kHz Hindi telephony: large-v3 has about 49% WER on real customer-support calls. The team's garbage output is expected, not a bug, though the acoustic hop made it worse. The best low-effort options are:
- **(a) Sarvam Saaras v3/v4 API.** It is Indian, explicitly "optimized for 8 kHz telephony," has a `codemix` mode for Hinglish, costs about ₹0.49/min, gives free signup credits, and limits REST requests to 30 s.
- **(b) On-device AI4Bharat IndicConformer-600M** (hi, CTC), using the community int8 ONNX build (0.62 GB, about 1.1 GB RAM) or a CoreML build. This fits an 8 GB M1 and was trained on Indian speech.

For the scam-language layer, run keyword and phrase matching on a romanised transcript (fuzzy match), rather than relying on a clean full transcript.

### Cited Findings
- **Narrowband Hindi telephony benchmark** (real customer-support calls, 8 kHz), overall WER:

  | Model | Overall WER |
  |---|---|
  | Whisper-large-v3 | **49.2%** (agent 47.2, customer 53.2) |
  | Data2Vec_AQC | 43.7% |
  | NeMo zero-shot | 44.4% |
  | **Google Telephony (commercial)** | **36.9%** |
  | Conformer trained from scratch on 50 h | 28.9% |
  | NeMo fine-tuned on 50 h | 23.3% |
  | NeMo fine-tuned + pseudo-labels | 19.7% |
  | In-house encoder + pseudo-labels | 16.6% |

  The authors call zero-shot foundation models "suboptimal across the board." — [arXiv 2606.18659 (Jun 2026)](https://arxiv.org/html/2606.18659)
- **Sarvam Saaras** (v4 default, v3 available):
  - Modes are transcribe, translate (to English), verbatim, translit (romanised) and codemix (English words in Latin script, Indic in native script).
  - "Optimized for 8KHz telephony audio."
  - Accepts WAV/MP3/AAC/OGG/OPUS/FLAC/AMR and more, auto-detected.
  - Limits are 30 s per REST request and up to 2 h per batch file. Streaming over WebSocket is available.
  - — [Sarvam Saaras docs](https://docs.sarvam.ai/api/getting-started/models/saaras.md)
- Sarvam's streaming STT added 8 kHz sample-rate support in Sept 2025. A product page still says streaming takes 16 kHz PCM, so the two sources conflict. — [Sarvam changelog](https://docs.sarvam.ai/changelog/2025/9/1); [Sarvam Nepali page](https://www.sarvam.ai/apis/speech-to-text/nepali)
- Legacy Saarika reported 11.81% Hindi WER on Vistaar. This is a wideband mix, not telephony. — [Sarvam Saarika docs](https://docs.sarvam.ai/api/models/saarika)
- Sarvam STT pricing:
  - Real-time/batch: ₹0.49/min pay-as-you-go (₹0.45 Pro, ₹0.41 Growth).
  - With diarization: ₹0.59/min.
  - Free credits on signup (amount not stated), non-expiring.
  - Product pages elsewhere list ₹1.25/min, which conflicts; the pricing page is likely the newer figure.
  - — [Sarvam API pricing](https://www.sarvam.ai/api-pricing); [Sarvam Odia page](https://www.sarvam.ai/apis/speech-to-text/odia)
- **IndicConformer-600M multilingual** (AI4Bharat):
  - Covers 22 Indian languages under an MIT license. The official loading path uses AI4Bharat's NeMo fork. — [AI4Bharat GitHub](https://github.com/AI4Bharat/IndicConformerASR); [HF collection](https://huggingface.co/collections/ai4bharat/indicconformer)
  - A Hindi-only model also exists: `ai4bharat/indicconformer_stt_hi_hybrid_ctc_rnnt_large`. — [HF collection](https://huggingface.co/collections/ai4bharat/indicconformer)
  - Community int8 ONNX build: the encoder shrinks from 2.4 GB to 0.62 GB and peak RAM from about 2.6 GB to about 1.1 GB. The author motivates it explicitly with "an 8 GB device." Usage is `AutoModel.from_pretrained(..., trust_remote_code=True)`, then `model(wav16k, "hi", "ctc")`. The WER cost is about +0.5 points on 1 of 6 conversational clips. — [HF yashwork-byte/indic-conformer-600m-int8-onnx](https://huggingface.co/yashwork-byte/indic-conformer-600m-int8-onnx)
  - CoreML (macOS) RNNT build with per-language heads including Hindi. There is no language ID, so the caller must specify the language. — [HF phequals CoreML](https://huggingface.co/phequals/indic-conformer-600m-multilingual-coreml-rnnt)
- Whisper Hindi fine-tunes, e.g. vasista22/whisper-hindi-large-v2 at 6.8–10.98% WER, are benchmarked on read or broadcast speech, not telephony. — [HF vasista22](https://huggingface.co/vasista22/whisper-hindi-large-v2/blob/main/README.md); [Collabora](https://collabora.com/news-and-blog/news-and-events/breaking-language-barriers-fine-tuning-whisper-for-hindi.html)
- **Deepgram Nova-3:**
  - Supports Hindi.
  - Nova-3 Multilingual (`model=nova-3&language=multi`) code-switches across 10 languages, including Hindi and English.
  - The vendor claims up to 27% WER reduction for Hindi vs Nova-2.
  - No telephony or Hinglish WER is published.
  - — [Deepgram blog](https://deepgram.com/learn/deepgram-expands-nova-3-with-11-new-languages-across-europe-and-asia); [Deepgram changelog](https://developers.deepgram.com/changelog/2025/2/12)
- **Keyword spotting:**
  - sherpa-onnx supports KWS and hotwords, but hotword biasing works only for transducer models, not Whisper. — [react-native-sherpa-onnx docs](https://www.mintlify.com/XDcobra/react-native-sherpa-onnx/advanced/hotwords)
  - The published sherpa-onnx KWS models (about 3.3M params) cover English and Chinese only; there is no Hindi KWS model. — [sherpa-onnx pkg](https://pkg.go.dev/github.com/csukuangfj/sherpa-onnx@v1.12.33)
  - Hindi KWS research exists, a fixed-vocabulary CNN on MFCCs, but it is not a ready-to-use model. — [arXiv 2605.02928](https://www.alphaxiv.org/abs/2605.02928)
  - Open-vocabulary KWS built on intermediate ASR representations is a known approach. — [IIIT-H thesis](https://cvit.iiit.ac.in/research/thesis/thesis-students/open-vocabulary-audio-keyword-spotting-with-low-resource-language-adaptation)

### Inferences (practical recipe for today)
- **Fastest path to working:** send call-audio chunks (≤30 s; VAD-split) to Sarvam Saaras with `mode="translit"` or `"codemix"`. Romanised output makes matching phrases like "paise bhej", "OTP", "kisi ko mat batana", "accident" and "police" trivial. A few minutes of demo audio fits easily within the free credits.
- **Local path:** IndicConformer int8 ONNX, Hindi, CTC, on 16 kHz input (upsample 8 kHz call audio with `ffmpeg -ar 16000`; upsampling adds no information but matches the model's expected rate).
  - Output is Devanagari. Transliterate to Latin (e.g. the `indic-transliteration` package) or match on Devanagari variants of the phrases.
  - English loanwords like "OTP" and "police" will appear in Devanagari (ओटीपी, पुलिस), so include those forms in the phrase list.
- **If staying on Whisper (mlx-whisper):**
  - Force `language="hi"` (auto language ID often flips to Urdu or English on narrowband audio).
  - Use `condition_on_previous_text=False` to stop hallucination loops, and raise `no_speech_threshold` / VAD-gate silence.
  - Set an `initial_prompt` containing Hinglish scam vocabulary in the script you want out.
  - Large-v3-turbo will still be roughly at the ~49% WER level of large-v3 on real 8 kHz calls. Use it only for keyword evidence, not exact text. These parameter recommendations come from general Whisper practice; I found no telephony-Hindi source quantifying them.
- **Preprocessing:**
  - Resample to 16 kHz mono.
  - Use a gentle band-pass (about 100–3800 Hz for narrowband) and loudness normalisation.
  - Use VAD chunking (Silero VAD) at 5–15 s, which also respects Sarvam's 30 s limit.
  - Be careful with heavy denoisers (e.g. RNNoise/DeepFilterNet); they can hurt ASR on already-codec'd speech. This is an inference with no citation found.
- **Scam-language layer robustness:**
  - Match **fuzzily** on romanised n-best output, e.g. rapidfuzz partial_ratio ≥ 80 over normalised tokens such as "paise/paisa/pese", "bhej/bhejo/bhejdo".
  - Score intent across the whole call (urgency + money + secrecy + authority), not single words. A 30–50% WER transcript still usually preserves several of these cue words.
  - Optionally pass the noisy transcript to an LLM for intent classification; LLMs tolerate ASR noise well.
- **ASR on Path 1/2 audio vs the loudspeaker path:** expect ASR on the realistic digital test paths to be noticeably better than on the loudspeaker path. Re-evaluate there before concluding the ASR approach fails.

### Gaps
- I found no published WER for IndicConformer, Sarvam Saaras, Deepgram Nova-3, AWS Transcribe hi-IN (8 kHz) or Google Chirp on **8 kHz Hindi/Hinglish telephony**. Only arXiv 2606.18659 gives telephony numbers, and it does not cover those systems except "Google Telephony" and a generic NeMo model.
- I did not retrieve AWS Transcribe hi-IN 8 kHz support or pricing, or Google Chirp 2/3 Hindi telephony details.
- No Hindi open-vocabulary KWS model is ready for sherpa-onnx; building one is out of scope for a few hours.
- I did not verify the exact mlx-community availability of IndicConformer or of Hindi-fine-tuned Whisper (MLX format). Converting a HF Whisper fine-tune to MLX is possible with mlx-examples' convert script, but untested here.
