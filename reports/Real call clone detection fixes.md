# Retest the right channel, then measure behaviour

The state of the art does not detect AI-cloned voices reliably on real phone calls, so Voice Shield's 35–40% EER is not a bug to be ashamed of. It is roughly what the published literature predicts for the stress test the team ran. That test was also the wrong headline benchmark. Indian voice-clone scams reach victims mostly as WhatsApp calls or as VoIP routed through SIM boxes onto ordinary mobile numbers. In both cases the clone is injected digitally. No source in this research describes scammers playing a clone from a loudspeaker into a second phone. The laptop-speaker → phone-mic → VoLTE path adds a room-acoustics replay stage that real attacks skip, and replay alone pushes the best open detector family from 10.6% to 24.8% EER ([ReplayDF](https://arxiv.org/html/2505.14862v2)). With about ten hours left, the team can make five fixes and report each one honestly:

- **Re-run the test** on a digital-injection path (BlackHole → WhatsApp Desktop, or a line-to-mic cable into the calling phone) and keep the loudspeaker result as a labelled worst-case row.
- **Train a logistic-regression probe** on frozen mid-layer DF_Arena features, using a small interleaved real-call set split by call, and report a task that cannot be won by spotting the loudspeaker.
- **Add a channel-proof behavioural layer.** Measure response gaps, backchannels and overlap from the separate uplink and downlink streams that scrcpy can capture, and add a spoken challenge.
- **Replace Whisper** with Sarvam Saaras in codemix/translit mode, with an int8 IndicConformer as the offline path, feeding fuzzy keyword matching rather than exact text.
- **Claim small-N numbers with call-level bootstrap intervals** in the README and video, not accuracy percentages.

What none of this does is catch a live human using real-time voice conversion over a codec. That gap belongs in the limitations section.

## The 35–40% collapse matches the field's own numbers

No open, documented detector has been trained for both replayed deepfakes and telephony, and every published replay benchmark shows large losses. In ReplayDF, published checkpoints that score 10–33% EER on their own test sets jump to 25–50% once speech is played through real speakers and re-recorded. The best family, wav2vec2-AASIST, still sits at **24.8% EER**. Retraining with room-impulse-response augmentation brought it down only to **11.1%**. Adding noise changed almost nothing, which means the damage comes from the speaker and room filtering the signal, not from noise ([arXiv 2505.14862](https://arxiv.org/html/2505.14862v2)). EchoFake used a setup very close to the team's: MacBook and iPad speakers into an iPhone 13 mini and a Galaxy A54 at 15 and 50 cm. Models trained on existing datasets averaged **59.6% accuracy** on its replayed audio ([arXiv 2510.19414](https://arxiv.org/html/2510.19414v1)). The strongest real-world system found, from Delgado et al. at ICASSP 2026, uses a frozen WavLM with presented-data training and a private benchmark of 80 participants and 16+ phones. It still caught only **88.2% of injected and 76.3% of loudspeaker-played deepfakes at 1% false-alarm rate**, and the authors recommend a separate playback detector ([arXiv 2509.26471](https://arxiv.org/html/2509.26471v2)).

The detector itself shows why. DF_Arena_500M's training list is ASVspoof 2019/2024, Codecfake, LibriSeVoc, DFADD, CTRSVDD, SpoofCeleb, MLAAD and EnvSDD. It includes neither replay nor telephony data, and even on its own benchmarks its pooled EER is 10.88% ([HF model card](https://huggingface.co/Speech-Arena-2025/DF_Arena_500M_V_1)). The earlier multilingual evidence still applies: all eleven detectors on the 2026 ML-ITW benchmark, which includes Hindi, scored **40–50% EER** ([arXiv 2603.05852](https://arxiv.org/html/2603.05852)). ASVspoof 5's telephony track found detection "degrades under … neural encoding/compression", with Speex 8 kHz severe and Opus 8 kHz moderate ([arXiv 2601.03944](https://arxiv.org/html/2601.03944v1); [arXiv 2408.10361](https://arxiv.org/pdf/2408.10361)).

Shipped products confirm the ceiling indirectly. LG U+ ixi-O runs an on-device Anti-DeepVoice module, and since October 2026 it feeds call risk to Woori Bank's fraud monitoring ([GSMA](https://www.gsma.com/solutions-and-impact/technologies/security/scams/gsma_study/real-time-on-device-vishing-detection-anti-deepvoice-protection/); [Herald](https://mbiz.heraldcorp.com/article/10893601)). Reality Defender RealCall runs an ensemble on each call stream ([Reality Defender](https://www.realitydefender.com/product/realcall)). Google's Pixel Scam Detection classifies what is being said, not how the voice sounds ([TechCrunch](https://techcrunch.com/2024/05/14/google-will-use-gemini-to-detect-scams-during-calls)). None publishes a false-positive rate on real calls. The state of the art in October 2026 is therefore an ensemble in which the acoustic score is one weak input. The open-model frontier on phone audio is "partially recovers with in-channel data", not "solved".

The Whisper failure fits the same pattern. On real 8 kHz Hindi customer-support calls, Whisper-large-v3 scores **49.2% WER** and Google's commercial telephony model 36.9%. Only models fine-tuned on in-domain telephone speech go below 25% ([arXiv 2606.18659](https://arxiv.org/html/2606.18659)). Two acoustic hops on top of that produce the garbage output the team saw.

## Scammers inject audio digitally, so test that way

The reported Indian cases point to digital paths. A Mumbai 69-year-old lost ₹50 lakh after a **WhatsApp call** from an unfamiliar number showing the impersonated person's photo; police suspect, but have not confirmed, an AI-cloned voice ([The420](https://the420.in/mumbai-senior-citizen-50-lakh-ai-voice-cloning-scam/)). Digital-arrest operations run from overseas compounds route internet calls through SIM boxes so that they arrive as local mobile calls. Tamil Nadu's Cyber Crime Wing seized 44 such boxes in two months of 2025 ([The420](https://the420.in/tamil-nadu-cybercrime-simbox-delhi-digital-arrest-scam/)), and a CBI case in Meerut seized 180 SIMs ([Daily Pioneer](https://www.dailypioneer.com/news/meerut-cbi-busts-voip-fraud-180-sim-cards-seized)). NCC Group's consented red-team vishing fed real-time voice-converter output directly into the calling software with about 0.5 s delay. It never played the output acoustically ([IEEE Spectrum](https://spectrum.ieee.org/real-time-audio-deepfake-vishing)). Vendors sell step-by-step guides for routing a voice changer into WhatsApp Desktop through a virtual audio device, which shows the technique is commodity knowledge ([VoxBooster](https://voxbooster.com/blog/voice-changer-whatsapp-video-desktop)).

The realistic channels split into three cases:

- **WhatsApp/Opus** (most "relative in trouble" clones): wideband, internet-coded. This is the easiest realistic case.
- **SIM-box termination**: VoIP codec, then transcoding onto possibly 2G/3G AMR-NB at 300–3400 Hz. This is the hardest realistic case.
- **Loudspeaker into the scammer's own phone**: the team's setup. It is plausible only for low-skill actors and should be treated as a stress test.

No source confirms which codec Jio or Airtel use by default for VoLTE (AMR-WB or EVS). The team can read it off a spectrogram: a ceiling near 3.4 kHz means narrowband, near 7 kHz means wideband.

Test in this order:

1. **WhatsApp injection (about 30 minutes).** Install BlackHole 2ch (`brew install blackhole-2ch`), a free virtual audio driver ([GitHub](https://github.com/lucyalynch/BlackHole)). Set it as the microphone in **WhatsApp Desktop**; Safari blocks virtual mics. Play WAVs into it and call the Oppo's WhatsApp ([VoxBooster](https://voxbooster.com/blog/voice-changer-whatsapp-video-desktop)).
2. **Carrier-call injection (about 1 hour, ₹200–500 of hardware).** Run the Mac headphone-out through a TRRS line-to-mic attenuator cable or a USB-C audio adapter into the calling Android phone, then place a normal SIM call to the Oppo. This gives the real AMR/EVS chain with no room acoustics, and is the closest legal stand-in for SIM-box delivery.
3. **Offline codec simulation for bulk data.** Use ffmpeg round-trips through AMR-NB 12.2k, Opus 8/12k and G.711 µ-law, and chain Opus → G.711 → AMR-NB to imitate SIP-to-GSM transcoding.

Keep the existing loudspeaker numbers as the bottom row of the table. Do not use caller-ID spoofing, third-party numbers or SIP trunks terminating on Indian mobiles; that is the regulated SIM-box path and is unnecessary.

Two practical risks need a five-minute check before relying on either path:

- **WhatsApp capture on the Oppo.** It is unverified whether scrcpy's `voice-call*` sources capture WhatsApp audio. Those sources target the telephony path, and WhatsApp may block playback capture. If capture fails, receive the WhatsApp call on a second computer and record it digitally.
- **WhatsApp Desktop and BlackHole.** Only a vendor blog reports that WhatsApp Desktop on Mac still accepts BlackHole as a microphone.

For the carrier path, the existing scrcpy capture on the Oppo already works. scrcpy documents `--audio-source=voice-call`, `voice-call-uplink` and `voice-call-downlink` on Android 11+ ([scrcpy audio docs](https://github.com/Genymobile/scrcpy/blob/master/doc/audio.md)). Confirm the exact option names with `scrcpy --help` on the installed version.

Expect zero-shot EER on the digital paths to land well below the loudspeaker number. Still, the probe below exists because "better than 35%" can mean anywhere from 5% to 30%. The earlier prior of **10–20% EER on real Indian cellular audio before adaptation** remains an estimate, not a measurement.

## A frozen-feature probe on interleaved calls buys partial recovery

Do not touch the backbone. Run DF_Arena's XLS-R once over every clip with all hidden states returned, mean+std pool each layer, and cache the result as `.npz`. Then fit `StandardScaler → LogisticRegression(class_weight="balanced")` per layer under grouped cross-validation. Frozen SSL features with a logistic-regression probe are an established low-overfitting baseline ([arXiv 2408.07414](https://arxiv.org/pdf/2408.07414)). On XLS-R, logistic-regression probes peak around **layers 6–14**: layer 9 on MLAAD and layers 6–8 on ASVspoof 2019 LA ([arXiv 2606.26384](https://arxiv.org/pdf/2606.26384)). Lower layers consistently carry the most deepfake signal ([arXiv 2502.03559](https://arxiv.org/abs/2502.03559)). After choosing a layer, try two extensions:

- concatenating the top 2–3 layers with PCA down to 64 dimensions, and
- fusing the probe with the raw DF_Arena logit.

Keep whichever wins under grouped CV. The whole loop takes minutes on an M1. One unverified detail needs checking first: whether the `trust_remote_code` model exposes `output_hidden_states` directly or needs a forward hook.

### Expected gains are modest at small N

| Evidence | Change | Conditions |
|---|---|---|
| Prompt-tuning paper, head-only ([arXiv 2410.09869](https://arxiv.org/html/2410.09869v1)) | 11.4% → 10.7–11.3% EER | 10–1000 target samples |
| Same paper, full fine-tuning | 11.4% → 3.49% / 0.876% EER | 100 / 1000 samples; overfits immediately at 10 |
| Few-shot prototypical net ([arXiv 2508.13320](https://arxiv.org/abs/2508.13320)) | 20–32% relative reduction | about 10 samples |
| ReplayDF retraining with RIR augmentation ([arXiv 2505.14862](https://arxiv.org/html/2505.14862v2)) | 18.2% → 11.1% EER | full retrain |
| Delgado et al., presented + augmented data ([arXiv 2509.26471](https://arxiv.org/html/2509.26471v2)) | 7.1% → 4.8% EER | frozen WavLM front-end |

Extrapolating, a probe on about 300 grouped segments per class should take in-channel EER from 35–40% to roughly **10–25%**. That is an inference, not a measured result. Going below 10% most likely means either the classes differ in something other than synthesis, or fine-tuning was used, which overfits at this N. Delgado et al. found that data realism mattered more than model size; a 3.55M-parameter ResNet stayed competitive. That supports spending the time on recording rather than modelling.

### Design the data so the probe cannot cheat

With tens of minutes of audio, a classifier happily learns the call session, the sentence, the speaker, leading silence or the loudspeaker instead of synthesis. A silence-only classifier exceeds 98% accuracy on FakeAVCeleb ([arXiv 2412.00175](https://arxiv.org/html/2412.00175v3)). EchoFake's replayed-bona-fide accuracy drops from about 99.5% on seen devices to **66–68% on unseen ones**, which shows that device and room conditions are being memorised ([arXiv 2510.19414](https://arxiv.org/html/2510.19414v1)).

Record three conditions through the same path, interleaved within every call:

- **H-live:** a teammate speaks the sentence into the calling phone.
- **H-inj:** the same teammate's clean recording of that sentence, injected through BlackHole or the cable (or replayed, on the loudspeaker path).
- **C-inj:** F5-TTS and Chatterbox clones of the same sentence, injected the same way.

Collection rules:

- Use 40–60 sentences of 4–8 s, mixing Hindi, Hinglish and scam scripts.
- Use both teammates as speakers, each cloned.
- Make four to six calls, varying volume and, on the loudspeaker path, distance.
- Apply identical preprocessing to every class: VAD trim, loudness normalisation, and resampling to 16 kHz.
- Keep `call_id`, `speaker`, `sentence_id`, `tool` and `condition` metadata on every 4 s window.

Splits and tasks:

- Split with `LeaveOneGroupOut(groups=call_id)`, then repeat by speaker and by sentence.
- Never let windows from one utterance appear in both train and test.
- Report **Task A** (H-live vs C-inj, the deployment case) and **Task B** (H-inj vs C-inj, the same channel with only synthesis differing) separately.
- Add leave-one-TTS-out runs: train on F5, test on Chatterbox, and the reverse.

If Task A is near zero while Task B stays near 35%, the team has built an injection or replay detector, not a clone detector. That is useful, but the README must call it that, because a replay detector also false-alarms on legitimate speakerphone users. EchoFake's MacBook→phone replay subsets could top up the probe's training data if the licence and download size allow; neither was confirmed.

### Report it so a judge can trust it

Report EER and TPR at 5% FPR, plus TPR at 1% FPR only alongside its bona-fide count. Give 95% intervals from 1,000 bootstrap resamples **over calls, not segments**. The `confidence_intervals` toolkit supports grouped bootstrap ([GitHub](https://github.com/luferrer/ConfidenceIntervals)). Two more rules:

- **Threshold:** set it on a calibration split, never at the test-set EER.
- **Rule of three:** with zero false alarms in 200 bona-fide windows, the honest 95% upper bound on FPR is about 1.5%, not 0%.

With four to six calls the interval will span ten or more EER points. The honest phrasing is "promising on N calls".

## Timing and challenge-response survive any codec

Behavioural signals measure when and how the remote party speaks, not its spectrum, so AMR or Opus compression barely touches them. In ten languages, humans start replying about **200 ms** after the other person stops ([Stivers et al. 2009](https://forms.mpi.nl/node/50939)). In Switchboard telephone calls, backchannels like "uh-huh" make up about **19% of dialogue acts** ([Benus et al.](https://www.cs.columbia.edu/nlp/papers/2007/benus_al_07b.pdf)), and 73% of sampled overlaps contain a backchannel or agreement token ([Frontiers](https://pmc.ncbi.nlm.nih.gov/articles/PMC4464110/table/T2)).

Production LLM voice agents measured on 270 live calls in 2026 had median turn times of **2.38–3.76 s** ([Retell, citing Cekura](https://www.retellai.com/learn/voice-ai-latency-benchmarks-comparing-real-time-response-performance)). Full-duplex research models almost never backchannel: 0.002–0.013 events per second ([Full-Duplex-Bench](https://arxiv.org/html/2503.04721v1)). Moshi replies in 0.11 s but takes over nearly every pause, so short-gap bots exist, and backchannel absence is the more universal tell. No peer-reviewed study has evaluated these features as an AI-caller detector on real calls, and no Hindi backchannel ("haan", "achha", "ji", "hmm") statistics exist. The thresholds have to be calibrated on the team's own calls.

The team has an advantage most papers lack: scrcpy's uplink/downlink sources give the Oppo owner's voice and the remote caller's voice as separate streams, so no diarization is needed. Run two capture sessions if the device allows concurrent capture. If it does not, record the mixed `voice-call` stream and separate the two sides by energy or against a 10 s enrollment of the owner's voice; on Android recordings the local side is usually much louder. Silero VAD runs at under 1 ms per 30 ms chunk ([Silero](https://raw.githubusercontent.com/snakers4/silero-vad/master/README.md)). Lower `min_speech_duration_ms` below its 250 ms default so that short "hmm"s survive.

Over a trailing 60 s window, recomputed every 2 s, compute:

- **Response gap:** downlink onset minus the preceding uplink offset, as a median over five or more turns, plus its coefficient of variation.
- **Backchannel rate:** downlink segments under 1 s that fall inside uplink speech, per minute.
- **Overlap ratio:** frames where both streams' VAD is active, divided by speech frames.

Every gap measured at the Oppo includes the network round trip, typically a few hundred ms over cellular. Subtract the median gap from human-to-human calls on the same path rather than a constant. A starting heuristic for "bot-like": corrected median gap above 1 s, backchannels near zero over at least 60 s of owner speech, and overlap under 2%.

Challenge-response turns that passive signal into an active test. NYU's PITCH study raised deepfake detectability from **56% AUROC on ordinary speech to 88.7%** using targeted challenges. Even a single 4.5 s challenge reached about 90% AUC. However, PITCH used 16 kHz recordings with no telephone codecs and older voice-conversion models ([arXiv 2402.18085](https://arxiv.org/html/2402.18085v4)). Its strongest acoustic challenges (cupped mouth, whisper, humming) are exactly what narrowband codecs blur, so the robust hackathon version is semantic. The assistant asks the caller to repeat an unpredictable phrase ("blue mango seventeen") or to answer the family safe word. Score it on response latency and fuzzy transcript match.

This catches typed-TTS operators and LLM agents. It does **not** catch a human driving real-time voice conversion, because a human answers naturally; Seed-VC's delay is about 400 ms ([Seed-VC](https://github.com/ChadCSong/seed-vc)), and StreamVC-class systems run under 80 ms ([ACL demo](https://preview.aclanthology.org/watermark/2025.acl-demo.37)). For that threat only the safe word and a callback to a known number work, which is exactly what the FBI and Tamil Nadu Police advise.

## Swap Whisper for telephony-tuned Indic ASR and match fuzzily

Sarvam's Saaras API is explicitly "optimized for 8KHz telephony audio". It has `codemix` and `translit` (romanised) modes for Hinglish, accepts AMR and Opus directly, and limits REST requests to 30 s ([Sarvam docs](https://docs.sarvam.ai/api/getting-started/models/saaras.md)). It costs ₹0.49 per minute, and signup credits cover a demo ([Sarvam pricing](https://www.sarvam.ai/api-pricing)). The offline path is AI4Bharat's IndicConformer-600M (MIT, trained on Indian speech). A community int8 ONNX build cuts peak RAM from about 2.6 GB to **about 1.1 GB** for 8 GB machines, at about half a WER point of cost on one test clip ([HF](https://huggingface.co/yashwork-byte/indic-conformer-600m-int8-onnx)). It outputs Devanagari, so the keyword list needs forms like ओटीपी and पुलिस alongside the romanised ones. No source publishes telephony WER for Sarvam or IndicConformer, so the team should not claim a WER, only before-and-after transcripts of the same call.

If Whisper must stay, three settings reduce the damage:

- force `language="hi"`;
- set `condition_on_previous_text=False` to stop hallucination loops;
- VAD-gate the input.

These come from general Whisper practice and are untested on telephony Hindi. Whatever the ASR, feed it **only the downlink stream** in 5–15 s VAD chunks, not the mixed call.

The scam layer should not depend on clean text. Match keywords with rapidfuzz `partial_ratio ≥ 80` against variant lists ("paise/paisa/pese", "bhej/bhejo/bhejdo", OTP, police, "kisi ko mat batana"), and score intent across the whole call (urgency + money + secrecy + authority) rather than single words. A 30–50% WER transcript usually still contains several of those cues. An LLM classifier over the noisy transcript tolerates ASR errors well.

## Ten hours, two people, one honest table

The current time is about 14:30 IST on 23 October and submission closes at 00:30 IST on 24 October. The plan front-loads data, because every later number depends on it, and finishes the video four hours before the deadline. Person A owns the channel and the detector. Person B owns ASR, behavioural signals and integration, and both record together.

| IST | Person A | Person B | Exit criterion |
|---|---|---|---|
| 14:30–15:15 | Install BlackHole; test WhatsApp Desktop injection; check the cable path; confirm scrcpy uplink/downlink capture and the codec band on a test sweep | Get a Sarvam key; run Saaras codemix/translit on yesterday's captures (downlink only if available) | One digitally injected clip captured cleanly on the Oppo |
| 15:15–17:15 | Record together: 2 speakers × ~40 sentences × H-live/H-inj/C-inj(F5, Chatterbox), interleaved within 4–6 calls on the best digital path, plus 2 loudspeaker calls. Then record 3–4 role-play conversations each of human↔human, human↔typed-TTS and human↔LLM-agent with both streams saved | (same) | ≥15 min per class after VAD; manifest CSV with call_id |
| 17:15–19:00 | Zero-shot DF_Arena EER per channel; cache all hidden states; per-layer probe under LeaveOneGroupOut(call); Task A, Task B, leave-one-TTS-out; call-level bootstrap CIs | Turn-taking module (VAD on both streams → gap, CV, backchannels, overlap); calibrate the network offset on the human↔human calls | Two tables exist, even if the numbers are bad |
| 19:00–20:30 | Plug the probe into the live pipeline, showing the raw and adapted scores side by side; threshold at 5% FPR on calibration calls | Challenge-response prompt (random phrase + safe word) scored by latency and fuzzy match; fuzzy keyword layer; fusion rule (content/behaviour gate, audio boosts, human decides) | End-to-end demo on one live call |
| 20:30–21:30 | Record the video | Write the README | Video under 3 minutes uploaded |
| 21:30–23:00 | README numbers table and limitations; push the repo | Product Feedback and Friction Log; final checks | Submitted by 23:00 |
| 23:00–00:30 | Buffer | Buffer | — |

The cut rules, in order:

- If the cable never arrives, use WhatsApp injection alone.
- If WhatsApp capture on the Oppo fails, drop it and use the loudspeaker path with Task B as the honest test.
- If the probe has not produced a grouped-CV number by 19:00, ship zero-shot per-channel numbers and spend the time on behavioural signals instead, because those carry the demo.
- Skip LoRA, EchoFake downloads, prosody and F0 features today.

### What to claim

| README row | Claim | Do not claim |
|---|---|---|
| DF_Arena zero-shot, loudspeaker → VoLTE | "~35–40% EER; replay worst case, matches ReplayDF/EchoFake findings" | That it represents real scams |
| DF_Arena zero-shot, digital injection (WhatsApp / carrier) | Measured EER, N calls, N windows, 95% call-bootstrap CI | Any number not measured |
| Adapted probe, Task A and Task B, leave-one-TTS-out | Both rows, side by side; say which one is the real "clone" test | One blended accuracy |
| Behavioural layer | Gap, backchannel and overlap distributions for human vs TTS vs LLM role-play calls, N conversations | That it detects live voice conversion |
| ASR | Side-by-side Whisper vs Saaras transcripts of the same downlink audio | A WER figure |
| Limitations | Only 2 speakers, 2 TTS tools, 1 handset, team-controlled calls; real-time VC untested over a carrier; DF_Arena and F5 weights are non-commercial | "Production-ready", "99%" |

The video should show the failure first: the loudspeaker test and the 38% EER. Then show the corrected test path, the adapted score next to the raw one, and a live response-gap meter turning red when a typed-TTS caller takes three seconds to answer "repeat blue mango seventeen". End on the safe-word prompt and callback button, the layer that still works when everything acoustic fails. Judges reward a team that found its own failure, explained it with the literature, and fixed what could be fixed in a day.

## Conclusion

The biggest correction from this round of research is to the test, not the model. The earlier plan recommended loudspeaker playback as the realistic route. The delivery evidence now says scammers inject audio digitally, so the team's 35–40% figure measures a replay attack the threat model barely contains. Measuring the right channel will probably improve the headline more than any adaptation can. The adaptation should then be judged on Task B, because Task A rewards detecting a loudspeaker or cable rather than a synthetic voice.

The deeper implication is that, for a two-person team, the useful contribution is the combination of signals. Acoustic detection fails exactly where conversational timing works (typed TTS and LLM agents), and timing fails exactly where only procedure works (a live human driving voice conversion). An ensemble layered in that order, with each failure stated in the README, is closer to how ixi-O and Pindrop actually ship than any single-model EER, and it is the version of Voice Shield that stays honest when the next clone tool appears.
