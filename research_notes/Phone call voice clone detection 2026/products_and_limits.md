# How shipped products detect AI voice-clone scam calls (as of Oct 2026) and the honest limits of audio-only detection

Scope note: "as of October 2026" unless labelled. Facts from 2023–2025 are labelled with their date. Vendor accuracy numbers are reported as vendor claims; independent numbers are labelled as such.

## KQ1. Which shipped products actually analyze live phone calls, what signals do they use, and where do they run?

### Takeaway
Almost every consumer phone feature that "detects scam calls" in real time (Google Pixel, Samsung Galaxy via Google, Apple/Samsung Call Screening, Airtel's network filter, DoT's spoofed-call system) is content-, metadata- or caller-ID-based, not voice-artifact-based. The only shipped systems that run synthetic-voice (artifact) detection on live telephony audio are: Hiya's AI Voice Detection (app + carrier/OEM SDK), Truecaller's AI Call Scanner (on-demand, US/Android/English, 2024), Pindrop Pulse and Reality Defender RealCall (enterprise contact-center cloud), and LG Uplus ixi-O in Korea, which is the only confirmed fully on-device, real-time anti-deepvoice feature on a cellular dialer (95% claimed, ~5,500 detections/month).

### Cited Findings

**Google Pixel Scam Detection (content-based, on-device, confirmed)**
- Google describes the feature as using "AI models processed on-device to analyze conversations in real-time"; the example trigger is a caller pressing for gift-card payment. The blog never mentions voice/synthetic-audio artifacts — it is conversational-pattern analysis — [Google Security Blog, Mar 2025](https://blog.google/security/new-ai-powered-scam-detection-features/)
- Gemini Nano is used on Pixel 9+; Pixel 6–8 used "other robust Google on-device machine learning models." Google says only that "Gemini Nano outperformed other models" — no detection or false-positive rate is published — [Google Security Blog](https://blog.google/security/new-ai-powered-scam-detection-features/); [9to5Google, Nov 2024](https://9to5google.com/2024/11/13/pixel-phone-scam-detection/)
- Alert UX: audio chime + haptic + on-screen "Suspicious activity detected for this call" with "End call" / "Not a scam" buttons; off by default; audio processed ephemerally, nothing stored or sent to Google — [Android Authority](https://www.androidauthority.com/pixel-scam-detection-rollout-3499163/)
- Originally US-English only (Nov 2024 beta → Mar 2025 rollout) — [Google Security Blog](https://blog.google/security/new-ai-powered-scam-detection-features/)

**Samsung Galaxy (Google's model, not Samsung's own)**
- The same Google-built on-device Gemini Scam Detection reached Galaxy S26 in Feb 2026 (US English only); with One UI 9 Samsung says it "will be available in Japan, Canada, and India"; no European country listed. Warning text: "Warning: Scam detected." — [Notebookcheck, 2026](https://www.notebookcheck.net/Samsung-One-UI-9-Security-features-you-must-turn-on-yourself.1415703.0.html); [SammyFans, Oct 6 2026](https://www.sammyfans.com/2026/10/06/heres-a-closer-look-at-samsungs-scam-detection-feature/amp/)
- One UI 9 beta code hints at S27/S25/Fold7/Flip7 support (leak, not announcement) — [SamMobile](https://www.sammobile.com/news/galaxy-s26-spam-calls-detection-leak/)
- Separate from this, Galaxy S26 Call Screening (One UI 8.5+) answers unknown callers with a digital assistant and transcribes the reply — no scam/voice classification — [PhoneArena](https://www.phonearena.com/news/your-galaxy-might-soon-warn-you-about-voice-phishing-and-samsungs-ai-is-already-testing-it_id173026)

**Apple iOS 26 Call Screening (not deepfake detection)**
- Answers unsaved numbers, asks name + reason, shows live transcript; must be enabled. Hiya's own analysis: "It doesn't block or evaluate spam or scam calls." Scam/spam labelling on iPhone comes from carrier-side classification ("Spam" toggle) — [BGR](https://bgr.com/1978901/ios-26-automatic-call-screening-how-to-activate/); [Hiya blog](https://blog.hiya.com/what-you-need-to-know-about-apples-ios-26-call-screening)
- Documented false-positive side-effect: legitimate callers (delivery drivers, technicians) hang up thinking the AI prompt is an answering machine — [Fox News](https://www.foxnews.com/tech/make-unknown-callers-explain-why-theyre-calling.amp)
- No Apple feature analyzes call audio for synthetic voice (nothing found; see Gaps).

**Hiya (audio-artifact detection; app + carrier/OEM)**
- Hiya AI Phone app (Jan 2025) analyzes call audio in real time for scam language AND flags whether caller is "a person, a recording, or an AI-generated voice"; free app, $9.99/mo premium — [Help Net Security, Jan 2025](https://www.helpnetsecurity.com/2025/01/28/hiya-ai-phone/); [MobileIDWorld](https://mobileidworld.com/hiya-launches-ai-powered-app-to-combat-deepfake-voice-scams/)
- AI Voice Detection is also offered to MNOs and OEMs at the network/device level; built on the acquisition of Loccus.ai — [Hiya AI Voice product page](https://www.hiya.com/products/ai-voice); [Mobile World Live](https://mobileworldlive.com/ai-cloud/hiya-targets-deepfake-calls-with-loccus-ai-buy)
- Vendor claims: "Over 99% accuracy vs. the most complex 'In-the-wild' datasets", "verifications in fractions of a second", "language and channel independent, including the most challenging low-quality audio". No metric definition, FP/FN rate, language list, or independent validation on the page — [Hiya AI Voice](https://www.hiya.com/products/ai-voice)
- Hiya's own 2024 survey (2,000 US consumers): 1 in 3 received at least one deepfake scam call in 2024; 34% of those targeted lost an average $7,200 — vendor research — [MobileIDWorld](https://mobileidworld.com/hiya-launches-ai-powered-app-to-combat-deepfake-voice-scams/)

**Truecaller AI Call Scanner (on-demand, 2024 — older fact)**
- Launched May 2024: user taps "Start AI Detection" during a call; app briefly holds the call, analyzes a few seconds, returns "Human Detected" / "AI Voice Detected". Premium, US-only, Android-only at launch; English only, Hindi "in progress" — [SpeechTech](https://www.speechtechmag.com/Articles/News/Speech-Technology-News/TrueCaller-Launches-AI-Call-Scanner-164270.aspx); [MediaNama interview, Jun 2024](https://www.medianama.com/2024/06/223-video-interview-truecaller-ai-voice-scanner/)
- MediaNama: press release gave no accuracy figures and "a lack of transparency specifying exactly how the scanner has been trained" — [MediaNama, May 2024](https://www.medianama.com/2024/05/223-truecaller-ai-voice-scanner-spam-call/)
- UC Berkeley researcher (Hany Farid lab context) quoted: models trained to detect deepfakes of a *specific person* work better than general detectors — [MediaNama](https://www.medianama.com/2024/05/223-truecaller-ai-voice-scanner-spam-call/)

**Pindrop Pulse (enterprise contact-center, cloud)**
- Vendor/reseller claims: 99% accuracy detecting audio deepfakes with <1% false positives; "previously unseen deepfakes with 90% accuracy"; up to 99.4% when combined with Pindrop's multifactor authentication (Apr 2026 data) — [SoftwareOne listing](https://platform.softwareone.com/product/pindrop-pulse/PCP-8653-3864); [Parse profile](https://www.parse.gl/brands/pindrop-com-2)
- Validation described as >20M audio files from >370 TTS systems; 20 model enhancements in 2024 for accent/gender bias and background noise — [Pindrop](https://www.pindrop.com/article/how-pindrop-product-teams-innovated-for-future/)
- Mar 2026: Pulse/Passport/Protect integrated into Zoom Contact Center — [Nasdaq PR](https://www.nasdaq.com/press-release/pindrop-zoom-integration-embeds-real-time-deepfake-detection-and-identity)
- Pindrop 2025 Voice Intelligence & Security Report (Jun 12 2025; 1.2B calls analyzed): deepfake fraud attempts in contact centers +1,300% in 2024 (≈1/month → 7/day); insurance +475%, banking +149%; retail 1 attempt per 127 calls; forecast +162% deepfake fraud in 2025 — [Webull/PR](https://www.webull.com/news/12977613328671744); [Pindrop](https://pindrop.com/article/deepfake-fraud-could-surge/)

**Reality Defender (enterprise, cloud/on-prem)**
- Contact-center product analyzes live calls via detection API; RealCall runs "an ensemble of deep-learning models on each call's audio stream"; deployment options API, private cloud, on-prem, SaaS — [Reality Defender contact centers](https://realitydefender.com/contact-centers); [RealCall](https://www.realitydefender.com/product/realcall)
- Reality Defender's ASVspoof5 submission (2024): EER 5.56%, minDCF 0.1499 on unseen attacks, but for some codecs minDCF was 3–5x higher (codec-7, codec-10) — [arXiv 2410.07379](https://arxiv.org/pdf/2410.07379)

**Resemble Detect / GetReal**
- Resemble's own blog (CEO-authored, Jul 2026) claims #1 on an "independent audio deepfake benchmark" at 98.05%; its comparison page claims real-time streaming detection is included vs. Reality Defender add-on — competitor-written claims — [Resemble top-10 (2026)](https://www.resemble.ai/resources/top-10-deepfake-detection-tools-for-enterprise-security-in-2026); [Resemble vs RD](https://resemble.ai/resemble-ai-vs-reality-defender)
- GetReal Security is listed (by Resemble) as "Partial" real-time, forensic-media focus; no GetReal live-phone-call product page found — [Resemble top-10](https://www.resemble.ai/resources/top-10-deepfake-detection-tools-for-enterprise-security-in-2026)

**McAfee Deepfake Detector / Norton Deepfake Protection (PC, not phone calls)**
- McAfee "Project Mockingbird" (Jan 2024): ">90% accurate at detecting and exposing maliciously altered audio in videos"; heise reported 96% for English only. Runs on NPU of Lenovo AI PCs (launched exclusively on Lenovo, 2024). It scans audio in videos/browser, not phone calls. No discontinuation notice found — [McAfee PR Jan 2024](https://www.mcafee.com/en-us/consumer-corporate/newsroom/press-releases/2024/20240108.html); [heise](https://heise.de/-10006266); [Inside.com.tw](https://www.inside.com.tw/article/35992-mcafee-deepfake-detector)
- Norton Deepfake Protection: runs on NPU (Qualcomm Snapdragon X first, then Intel Core Ultra Sept 2025, AMD "later this year"); checks whether audio is AI-generated AND whether the message appears aimed at scamming; "currently only detects scams in English language audio files"; manual scan outside YouTube; PC-only — [Norton blog](https://us.norton.com/blog/online-scams/npu-scam-detection); [Gen PR Sept 2025](https://newsroom.gendigital.com/2025-09-16-Norton-Unveils-Advanced-Deepfake-Protection-Powered-by-Intel-R-Core-TM-Ultra-Processors); [Norton community](https://community.norton.com/t/introducing-deepfake-protection-feature/405536)

**Honor / Huawei on-device (video only)**
- Honor's on-device deepfake detection (IFA 2024, shipped Magic7 Pro 2025) checks video frames; "for now, the feature only works on video calls" — [TechRadar](https://www.techradar.com/phones/honor-phones/worried-about-deepfakes-you-should-be-but-honor-has-an-ai-powered-solution); [News24, Jun 2025](https://www.news24.com/brandstory/partner-content/honor-tackles-deepfakes-with-on-device-detection-20250620-0659)

**Qualcomm / Microsoft on-device efforts**
- Scam.ai Halo (Computex, Jun 2026): on-device deepfake detection for live *video* calls on Snapdragon NPU, Windows first; one report says a Modulate partnership adds synthetic-voice detection (single-source, unverified) — [BusinessWire Jun 2026](https://secure.businesswire.com/news/home/20260623132017/en/Scam.ai-Announces-Qualcomm-Partnership-Launches-Halo-Deepfake-Detection-Model-at-Computex-2026); [Biometric Update Aug 2026](https://www.biometricupdate.com/202608/scam-ai-launches-on-device-deepfake-detection-for-video-calls)
- No Microsoft product doing voice-clone detection on phone calls was found.

**LG Uplus ixi-O (Korea) — the only confirmed on-device, real-time anti-deepvoice on a cellular dialer**
- GSMA case study (Aug 2025): hybrid on-device pipeline = VAD → STT → lightweight quantized LLM binary vishing classifier (trained on de-identified Korean National Police Agency / National Forensic Service case data) + "Anti-DeepVoice" synthetic-voice module; sound alert + pop-up during the call; audio never leaves device. "Reported detection accuracy of 95 per cent"; "approximately 5,500 detection instances per month." Vendor-submitted; metric undefined — [GSMA case study PDF](https://www.gsma.com/solutions-and-impact/technologies/security/scams/wp-content/uploads/2025/08/Case-Study_Real-time-On-device-Vishing-Detection-and-Anti-DeepVoice-Protection-v2.pdf); [GSMA page](https://www.gsma.com/solutions-and-impact/technologies/security/scams/gsma_study/real-time-on-device-vishing-detection-anti-deepvoice-protection/)
- Korean press: flags manipulated voices "in just five seconds" without sending data to servers; also matches against reported criminal voiceprints; voice-auth feature launched Jun 30 2025 — [Asiae](https://view.asiae.co.kr/en/article/2026021215253365891); [KED Global](https://m.kedglobal.com/newsView/ked202411070013)

**Carrier-network / metadata systems**
- Airtel AI spam filter (launched Sept 2024, Dec 2024 data): flagged 8 billion calls + 0.8 billion SMS in ~2 months, up to 6% of calls flagged; uses caller patterns, frequency, duration vs known spam behaviour; network-side, no app, free — [getcoai](https://getcoai.com/news/indian-telco-airtel-says-its-blocked-8-billion-spam-calls-using-ai-in-just-2-months); [BusinessWorld](https://businessworld.in/article/airtel-introduces-ai-powered-spam-detection-system-to-shield-customers-from-unwanted-calls-sms-535145). A 2026 headline mentions vernacular alerts + international call scanning (snippet only, unverified) — [APAC News Network](https://apacnewsnetwork.com/tag/telecom-security/)

### Inferences
- The on-device "scam detection" category (Pixel/Galaxy) is really an on-device LLM intent classifier over an STT transcript; it catches social-engineering scripts regardless of whether the voice is cloned, and would equally fire on a human scammer. It gives no protection against a cloned-voice relative who speaks a *plausible* script, and it is English-only in most markets.
- Live audio-artifact detection on cellular calls exists in production only (a) in enterprise contact centers via cloud, (b) in Hiya/Truecaller apps that tap the call audio on Android, and (c) in LG Uplus's Korean dialer. Nothing shipped on iPhone can do this because iOS does not expose call audio to third-party apps.
- The LG Uplus architecture (VAD + STT + small LLM + anti-deepvoice, all quantized on NPU) is the reference design for a true multi-signal on-device system.

### Gaps
- No published FP/FN rates for Pixel/Galaxy Scam Detection, Hiya, Truecaller or LG Uplus. "95%", "99%" and "90% on unseen" are vendor numbers with undefined metrics/datasets.
- Could not confirm whether Truecaller AI Call Scanner ever shipped on iOS or outside the US, or whether Hindi support launched.
- Pindrop's own Pulse product page returned 404; numbers above are from reseller/aggregator pages.
- No evidence of Apple, Huawei, Microsoft or Qualcomm shipping voice-clone detection on phone calls.

## KQ2. Published accuracy claims vs. independent tests; consensus on generalization to unseen cloners and telephony codecs

### Takeaway
Independent in-the-wild evaluation (Deepfake-Eval-2024) shows open-source audio detectors collapse to chance (AUC 0.43–0.58, EER 43–55%) and even the best anonymized commercial audio detector reaches only 0.89 accuracy / 0.93 AUC; ASVspoof 5 and a 2025 telephony benchmark show narrowband/neural codecs and packet loss are the dominant failure mode, partially fixable by codec augmentation. The field's consensus is that detectors trained on one generator family and one channel do not transfer.

### Cited Findings

**Deepfake-Eval-2024 (Chandra et al., arXiv Mar 2025; 56.5 h audio, 1,820 clips, 42 languages, 88 websites)**
- Open-source off-the-shelf on Deepfake-Eval-2024 vs original benchmark: AASIST AUC 0.43 (vs 1.00), RawNet2 0.53 (vs 0.99), P3 0.58 (vs 1.00); EER AASIST 55.22%, RawNet2 48.20%, P3 43.00%; average audio AUC drop 48% — [arXiv 2503.02857](https://arxiv.org/html/2503.02857)
- After fine-tuning on 60% of the dataset: AASIST acc 0.84 / AUC 0.91 / EER 16.99%; RawNet2 0.82 / 0.88 / 20.91%; P3 0.86 / 0.92 / 15.38% (avg AUC +80.6%) — [arXiv 2503.02857](https://arxiv.org/html/2503.02857)
- Eight anonymized commercial audio detectors: best = acc 0.89, AUC 0.93, precision 0.89, recall 0.84; #2 acc 0.88/AUC 0.93; #3 acc 0.86/AUC 0.90. Paper: no commercial model reached the ~90% it estimates is needed to match human forensic analysts; audio labels are partly correlated with commercial detectors (acknowledged bias) — [arXiv 2503.02857](https://arxiv.org/html/2503.02857)
- Documented failure modes: silent segments (accuracy 35.39% worse), background music (−17.94% accuracy, FNR +26.12%), non-English audio (−7.21% accuracy) — [arXiv 2503.02857](https://arxiv.org/html/2503.02857)
- Vendor spin on same paper: Reality Defender blog cites "approximately 78% accuracy" for leading commercial detectors (not matching paper text) — [Reality Defender](https://www.realitydefender.com/insights/lab-benchmarks-ineffective-in-deepfake-detection)

**VoiceWukong (arXiv Sept 2024 — older)**
- 12 SOTA detectors: best (AASIST2) EER 13.50%, all others >20%; "significant challenges in real-world applications" — [arXiv 2409.06348](https://arxiv.org/pdf/2409.06348)

**ASVspoof 5 (2024 challenge; overview paper arXiv Jan 2026)**
- 53 teams; top systems "consistently struggle with generalization, showing significant degradation under adversarial attacks, neural encoding/compression, and when tested on out-of-domain datasets" — [arXiv 2601.03944](https://arxiv.org/html/2601.03944v1)
- Vicomtech-UGR: clean EER 1.17% "severally degraded" under C07 (MP3+Encodec) and C10 (Speex 8 kHz); worst unseen attack A28 (YourTTS-based) 16.10% EER — [arXiv 2408.10361](https://arxiv.org/pdf/2408.10361)
- "Generalizable Detection of Audio Deepfakes" (arXiv Jul 2025): ASVspoof5 EER 7.68% → 3.57% with AWGN+RIR+RawBoost augmentation; degradation traced to codec-compressed *bona fide* audio being misclassified as fake — [arXiv 2507.01750](https://arxiv.org/pdf/2507.01750)

**Telephony/VoIP-specific benchmark (arXiv Apr 2025)**
- Simulated AMR-WB, EVS, IVAS, OPUS, Speex-WB, SILK plus packet loss 0/1/5/10/20%; baselines (GMM, LCNN, AASIST) lose avg 5.30% EER from clean to codec-only (0% PLR); codec+PLR augmentation (5x data) makes EER essentially flat (+0.003%). Authors: impact of real-world communication channels "largely overlooked" — [arXiv 2504.12423](https://arxiv.org/html/2504.12423v2)
- Odyssey 2026 paper studies telephony transmission impact on deepfake *source tracing* (MLAAD) — [ISCA Odyssey 2026](https://www.isca-archive.org/odyssey_2026/klein26_odyssey.pdf)

**Surveys**
- Yi et al. survey (2023): future work must address "lack of large scale datasets in the wild, poor generalization of existing detection methods to unknown fake attacks" — [arXiv 2308.14970](https://arxiv.org/pdf/2308.14970)
- Capacity-scaling paper: extending model capacity "while beneficial in the case of in-domain benchmarking, [is] insufficient for generalisable detection"; ASVspoof 2021 LA varies by "compression and telephony encoding algorithms" — [arXiv 2406.03512](https://arxiv.org/html/2406.03512v3)
- Humans: reviews find audio is the *worst* medium for people trying to spot fakes by ear — [SecurityScientist](https://www.securityscientist.net/blog/can-people-detect-deepfakes/)

**Consumer Reports (Apr 2025) tested cloning tools, not detectors**
- Of 6 voice-cloning products, only Descript and Resemble AI had meaningful anti-misuse safeguards; the rest used self-attestation — [eWeek](https://www.eweek.com/de/news/ai-voice-cloning-scammers-consumer-reports/)

### Inferences
- Vendor "99%" claims are lab/own-dataset numbers; the only independent cross-vendor evaluation puts the best commercial audio detector at ~89% accuracy on social-media audio, before telephony degradation. Expect a further hit on 8 kHz/AMR/Opus + packet loss unless the model was explicitly codec-augmented.
- The three documented failure modes most relevant to phone calls — silence, background noise/music, non-English — are all common on Indian cellular calls; a detector not trained on Indian languages and AMR-NB will under-perform its brochure.
- Operationally, a ~10% FP rate on a feature that fires on every call is unusable; this is likely why Google/Samsung chose content classification (which triggers only on scam scripts) over per-call voice-liveness.

### Gaps
- No independent test of Hiya, Truecaller, Pindrop, Reality Defender or LG Uplus on live cellular audio was found. Deepfake-Eval-2024 anonymizes commercial vendors.
- No NPR/Consumer Reports test of *detectors* found (CR tested cloners).
- ASVspoof 5 official baseline per-codec EERs not retrieved.

## KQ3. Real-time voice conversion (RVC/Seed-VC/StreamVC/live changers) vs. TTS clones against detectors

### Takeaway
Evidence is thin and mostly academic. RVC-style conversion is explicitly flagged as a real-time call threat; dedicated 1-second-window streaming detectors exist in the lab, and RVCBench (2026) finds modern VC models exhibit "detector-facing separability" vulnerabilities, but no shipped product publishes VC-vs-TTS detection rates, and no paper found gives a clean head-to-head.

### Cited Findings
- RVC "is also chosen due to its ability to quickly convert short speech samples, leading to the possibility of it being used in real-time," with a microphone-based during-call setup described (DEEP-VOICE dataset paper, 2023) — [arXiv 2308.12734](https://arxiv.org/pdf/2308.12734)
- "Defense Against Synthetic Speech: Real-Time Detection of RVC Voice Conversion Attacks" (arXiv Jan 2026): streaming detection on 1-second segments with time-frequency + cepstral features and supervised classifiers on DEEP-VOICE; background ambience re-mixed after conversion so detectors can't use noise absence as a shortcut; supports segment-level and call-level aggregation. Abstract gives no EER/latency numbers; no cross-model generalization test — [arXiv 2601.04227](https://arxiv.org/abs/2601.04227)
- RVCBench (arXiv Feb 2026): benchmarks 18 open-source modern VC models (codec-token LM and diffusion based); evaluates "detector-facing separability" with SSL-based, AASIST (graph), RawNet2 (CNN) detectors and an audio-LLM judge on 600 VCTK samples; authors caution separability ≠ robustness. No per-family numbers in abstract — [arXiv 2602.00443](https://arxiv.org/abs/2602.00443)
- ASVspoof 5: the hardest unseen attack for a strong system was A28, a YourTTS-based TTS (16.10% EER) — i.e., TTS, not VC, was the outlier there — [arXiv 2408.10361](https://arxiv.org/pdf/2408.10361)
- Hiya claims its detection distinguishes "a person, a recording, or an AI-generated voice" but does not separate VC from TTS — [Help Net Security](https://www.helpnetsecurity.com/2025/01/28/hiya-ai-phone/)
- Pindrop claims testing against ">370 text-to-speech systems" — TTS-centric; no VC count given — [Pindrop](https://www.pindrop.com/article/how-pindrop-product-teams-innovated-for-future/)

### Inferences
- Live VC preserves the scammer's real prosody, timing, breaths and the real room/telephone channel, removing several cues (unnatural pauses, flat prosody) that content- and artifact-detectors and humans rely on. Combined with codec degradation, VC over a cellular channel is plausibly the hardest shipped case; this is inference from the above, not a measured result.
- Vendor validation corpora skew to TTS engines; a buyer should ask for VC-specific (RVC, Seed-VC, StreamVC) and codec-specific test results.

### Gaps
- No source found giving detection EER for RVC/Seed-VC/StreamVC vs ElevenLabs/F5-TTS/Fish Speech/OpenAI voice under the same detector. RVCBench full text (not fetched) may contain this.
- No shipped product publishes VC-vs-TTS performance.

## KQ4. Signals besides audio that experts rate most robust; multi-signal fusion research; official human-in-the-loop countermeasures

### Takeaway
Every authority (FTC, FBI, Indian police/I4C materials) converges on process controls, not audio forensics: hang up, call back on a known number, verify the *event* via a second channel, use a pre-agreed family secret word, and treat urgency/secrecy plus wire/crypto/gift-card/OTP requests as the scam signature. Research backs text+audio fusion (transcript intent + synthetic-voice score) and finds transcripts beat raw audio for LLM-based scam classification.

### Cited Findings

**Official guidance**
- FBI IC3 PSA I-120324-PSA (Dec 3 2024): "Create a secret word or phrase with your family to verify their identity"; "Verify the identity of the person calling you by hanging up the phone" and "call the phone number directly" after looking it up yourself; "limit online content of your image or voice"; "Listen closely to the tone and word choice." No statistics in the PSA — [FBI IC3](https://www.ic3.gov/PSA/2024/PSA241203)
- FTC (Mar 2023, still current): "Don't trust the voice. Call the person who supposedly contacted you and verify the story. Use a phone number you know is theirs." If unreachable, go "through another family member or their friends." Red flags: requests to "wire money, send cryptocurrency, or buy gift cards" and give card numbers/PINs. Report at ReportFraud.ftc.gov — [FTC consumer alert](https://consumer.ftc.gov/consumer-alerts/2023/03/scammers-use-ai-enhance-their-family-emergency-schemes)
- Secondary FBI guidance: the secret word should not be texted, posted, or discoverable on social media; a successful callback to a known number is stronger evidence than questions inside the original call; caller ID can be spoofed so a familiar number isn't proof — [MoneyCrashers](https://www.moneycrashers.com/family-code-word-voice-clone/); [iTechGuides](https://www.itechguides.com/how-to-verify-a-familiar-voice-when-a-call-feels-urgent/)
- India: Tamil Nadu Police (Apr 2024): contact the supposed caller "through a known, verified number" before acting; ask probing questions — [DT Next via PressReader](https://www.pressreader.com/india/dt-next/20240428/281621015402986). Cyber-safety guides: agree a private codeword with relatives; report to 1930 / cybercrime.gov.in immediately so funds can be frozen — [CyberMithra](https://cybermithra.in/2023/12/13/voice-cloning-fraud/); [Moneylife](https://www.moneylife.in/article/fraud-alert-extortion-using-voice-cloning-and-csr-scams/73703.html)
- RBI: fraudsters pose as RBI officials threatening account freezes ("digital arrest") and press for OTP/PIN/card details (RBI PR998); RBI's standing advice: never share OTP/PIN/card details "even with bank officials, however genuine they might sound"; bank officials and RBI never ask for confidential info — [RBI PR998 PDF](https://website.rbi.org.in/documents/87730/39710918/PR998.pdf); [RBI press release](https://rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=53185)
- Gujarat Police awareness PDF: I4C, RBI and the PM have publicly warned about "digital arrest" video calls by impostors in uniform — [Gujarat Cybercrime PDF](https://gujaratcybercrime.org/Fake_Identity_Fraud_Awareness.pdf)
- Supreme Court of India (Aug 2026): directed RBI to issue within 4 weeks an SOP for temporary debit holds on mule accounts; States to operationalize e-Zero FIR and Cyber Crime Coordination Centres within 4 weeks (e-Zero FIR live in 19 states); CBI to consider lowering the ₹10-crore threshold for organised networks — [Drishti IAS, Aug 10 2026](https://www.drishtiias.com/daily-updates/daily-news-analysis/supreme-court-directs-measures-to-curb-digital-arrest-scams); [Verdictum](https://www.verdictum.in/supreme-court/digital-arrest-scams-interim-directions-rbi-1619172)

**Multi-signal research**
- MDPI Applied Sciences (Oct 18 2025): voice-phishing detector with text branch (KoBERT) + audio branch (MFCC → CNN-BiLSTM synthetic-speech classifier) and a fusion layer; motivation: text-only systems misclassify legitimate calls containing financial/institutional terms — [MDPI 15/20/11170](https://www.mdpi.com/2076-3417/15/20/11170/xml)
- Sim & Kim (arXiv Jun 2025): fine-tuned Llama3-8B SLM on transcripts matches a GPT-4 vishing detector; built an adversarial set of benign transcripts with scam vocabulary as a hard FP benchmark — [arXiv 2506.06180](https://arxiv.org/html/2506.06180v1)
- Turkish scam-call poster (arXiv, listed Jun 2026): first public aligned audio-transcript scam dataset (100 pairs); across 7 LLMs, transcript inputs consistently beat raw-audio inputs; ASR vs human-corrected transcripts perform comparably — [arXiv 2606.24523](https://arxiv.org/pdf/2606.24523)
- Norton's Deepfake Protection explicitly fuses "is the audio AI-generated" + "does the message appear aimed at scamming" — [Norton blog](https://us.norton.com/blog/online-scams/npu-scam-detection)
- LG Uplus fuses STT→LLM intent + Anti-DeepVoice + criminal voiceprint match — [GSMA case study](https://www.gsma.com/solutions-and-impact/technologies/security/scams/wp-content/uploads/2025/08/Case-Study_Real-time-On-device-Vishing-Detection-and-Anti-DeepVoice-Protection-v2.pdf)

### Inferences
- Rank order of robustness implied by the sources: (1) out-of-band callback/second-channel verification of the *event*; (2) pre-shared secret word; (3) transaction-type red flags (OTP, wire, crypto, gift card, "keep this secret", "don't hang up"); (4) caller-ID/number anomalies (international prefix, unknown number claiming to be family, spoofed-CLI flags); (5) transcript intent classifier; (6) voice-artifact score — the last being the least reliable in-the-wild and the only one adversaries can directly optimize against.
- Fusion papers and the two shipped fused systems (Norton, LG Uplus) both treat the voice-artifact score as a secondary feature gating or boosting a content score, not as a standalone verdict.

### Gaps
- No RBI or CERT-In advisory specifically about *voice cloning* was found (RBI material covers digital arrest/OTP; CERT-In nothing located). I4C guidance located only via police/secondary materials, not a primary I4C voice-cloning advisory.
- No paper found that fuses caller metadata (CLI, carrier, number age) with audio+text in one model.

## KQ5. India: scale of voice-clone / digital-arrest / family-emergency scams, and what telcos / DoT are doing

### Takeaway
India's official cyber-fraud losses are ~₹22,000+ crore/year (₹22,845 cr in 2024; ≥₹22,495 cr in 2025 on 2.81M complaints) with I4C projecting true 2025 losses near ₹1.2 lakh crore; digital-arrest complaints peaked at 123,672 (₹1,935.5 cr) in 2024 and fell to 58,249 in 2025 and 16,377 by June 2026. There is no official count of voice-clone-specific cases. DoT's countermeasures are all metadata/CLI-based (spoofed-call blocking, "International Call" labelling, Sanchar Saathi/Chakshu disconnections, CEIR); Airtel's network filter is behavioural; no Indian telco runs voice-deepfake detection on calls.

### Cited Findings

**Scale**
- Cyber-fraud losses: 2024 ₹22,845 crore on 2.26M complaints (66,370 FIRs); 2025 at least ₹22,495 crore on 2.81M complaints (55,484 FIRs; ~7,700 complaints/day; 32.4M calls to 1930; investment scams ~76% of losses); I4C projection: 2025 real losses could reach ₹1.2 lakh crore (~0.7% of GDP); national recovery rate 24% in 2025; CFCFRMS/1930 has saved >₹7,130 crore across 23 lakh complaints since 2021 (MHA parliamentary reply) — [Moneylife, May 29 2026](https://moneylife.in/article/housing-society-problems-and-solutions-occupancy-rights-leakage-disputes-and-agm-decisions/article/fraud-alert-india-is-losing-over-22000-crore-a-year-in-cyber-scams-and-the-worst-is-yet-to-come/80612.html)
- Digital arrest (I4C via Parliament reply Mar 2025 + SC proceedings Aug 2026): 2022 39,925 cases / ₹91.14 cr; 2024 123,672 / ₹1,935.51 cr; 2025 58,249 complaints; Jan–Jun 2026 16,377; cumulative 2022–May 2026 ≈297,727 complaints / ₹4,057.7 cr (News18-based); Money Restoration Mechanism restored ₹18.05 cr in 36,290 cases across 69 banks — [Drishti IAS Aug 2026](https://www.drishtiias.com/daily-updates/daily-news-analysis/supreme-court-directs-measures-to-curb-digital-arrest-scams); [Moneylife](https://moneylife.in/article/housing-society-problems-and-solutions-occupancy-rights-leakage-disputes-and-agm-decisions/article/fraud-alert-india-is-losing-over-22000-crore-a-year-in-cyber-scams-and-the-worst-is-yet-to-come/80612.html); [NewsBytes](https://www.newsbytesapp.com/news/science/india-s-digital-arrest-scam-causes-4-000cr-losses-in-3-years/story)
- Average digital-arrest loss per victim rose from ~₹22,826 (2022) to ~₹1,56,502 (2024) (Frank on Fraud estimate, not official) — [FrankonFraud PDF Jan 2026](https://frankonfraud.com/wp-content/uploads/2026/01/Digital-Arrest-Scams-Explained.pdf)
- Voice-clone prevalence (OLDER, Apr 2023): McAfee "Artificial Imposter" survey (1,010 Indian adults): 47% were a victim (20%) or knew one (27%) vs 25% global; 83% of Indian victims lost money, ~48% of them ≥₹50,000; 66% would respond to a voice note from a "loved one in need"; 86% share voice online weekly — [BusinessWorld](https://businessworld.in/article/ai-voice-scams-more-prevalent-in-india-affects-almost-50-indians-mcafee-report-475192); [FoneArena](https://www.fonearena.com/blog/392454/indians-victims-voice-scams.html/amp). Note: Moneylife (2026) attributes these same figures to a "2025 ORF survey"; they match McAfee 2023 exactly, so treat the ORF attribution as suspect.
- Over 50% of 2025 cyber fraud targeting Indians reportedly originated from scam compounds in Cambodia/Myanmar/Laos (uncited in source) — [Moneylife](https://moneylife.in/article/housing-society-problems-and-solutions-occupancy-rights-leakage-disputes-and-agm-decisions/article/fraud-alert-india-is-losing-over-22000-crore-a-year-in-cyber-scams-and-the-worst-is-yet-to-come/80612.html)

**DoT / telco measures (all CLI/metadata-based)**
- International Incoming Spoofed Calls Prevention System (live Oct 22 2024): blocks international calls presenting Indian CLI; two phases (per-operator, then central); ~1.35 crore calls blocked in first 24 h (~90%); by Dec 2024 ~6 lakh/month; ~4 lakh by Mar 2025 (Lok Sabha); scammers shifted to +8x/+65 numbers, so DoT mandated an "International Call" label on all foreign-origin calls and told Airtel/BSNL/Jio to block >20 blacklisted carriers — [Sanchar Saathi PIB PDF](https://sancharsaathi.gov.in/SancharSaathiDocuments/ImportantDocuments/Press%20Release_%20Press%20Information%20Bureau.pdf); [MediaNama Dec 2024](https://www.medianama.com/2024/12/223-dot-blocked-90-percent-spoofed-calls-two-months/); [Telecom Review Asia](https://telecomreviewasia.com/news/industry-news/4808-dot-blocks-90-of-international-spoofed-calls-in-cybercrime-crackdown/)
- False-positive concern: system "may mistakenly identify a legitimate call as spoofed if the caller's number matches the pattern" (e.g., Indians roaming abroad) — [MediaNama Oct 2024](https://www.medianama.com/2024/10/223-indian-spoofed-calls-prevention-system-blocks-1-35-crore-calls-amidst-false-positives-concerns/)
- Sanchar Saathi / Chakshu (Rajya Sabha reply Feb 5 2026): Chakshu reports 2,08,224 (2024), 5,19,662 (2025), 42,855 (2026 to early Feb); from 7.7 lakh citizen inputs: 39.43 lakh connections disconnected, 2.27 lakh handsets blacklisted, 1.31 lakh SMS templates blocked; earlier (Mar 2025): 3.40 crore disconnections total, 3.19 lakh IMEIs blocked. Financial-loss cases are routed to I4C, not Chakshu — [Angel One/RS reply](https://www.angelone.in/news/economy/chakshu-under-sanchar-saathi-reports-fraud-39-43-lakh-mobiles-disconnected-over-1-000-crore-loss-prevented); [Rajya Sabha PQ 267 Mar 2025](https://rsdebate.nic.in/bitstream/123456789/759305/1/PQ_267_20032025_U2257_p161_p162.pdf); [Morung Express](https://morungexpress.com/cyber-fraud-3943-lakh-mobile-connections-disconnected-227-lakh-handsets-blacklisted)
- DoT reversed its Dec 2025 mandate to pre-install Sanchar Saathi on all handsets after pushback — [Business Standard](https://www.business-standard.com/topic/spams)
- Telecommunications (Radio Equipment Possession Authorisation) Rules 2025 notified; (User Identification) Rules 2025 in final notification stage — [Drishti IAS](https://www.drishtiias.com/daily-updates/daily-news-analysis/supreme-court-directs-measures-to-curb-digital-arrest-scams)
- Airtel network AI filter: 8 bn calls / 0.8 bn SMS flagged in ~2 months, ≤6% of calls; 12% drop in customer response to spam — [getcoai](https://getcoai.com/news/indian-telco-airtel-says-its-blocked-8-billion-spam-calls-using-ai-in-just-2-months)
- Samsung says Google's on-device Scam Detection will be available in India with One UI 9 — [Notebookcheck](https://www.notebookcheck.net/Samsung-One-UI-9-Security-features-you-must-turn-on-yourself.1415703.0.html)

### Inferences
- "Digital arrest" is overwhelmingly a live-human + video-impersonation scam; voice cloning is a sub-technique within family-emergency and extortion scams. No Indian agency breaks out voice-clone cases, so the only prevalence data is a 2023 vendor survey.
- Indian defenses are at the network/CLI layer (spoofing, foreign-origin labelling, SIM/IMEI hygiene). A consumer-side detector in India would be the first layer that looks at the audio or content at all, and would need Hindi/regional-language support that Pixel/Galaxy Scam Detection (English) and Truecaller (English) lack.

### Gaps
- No official I4C/NCRB count of voice-clone or "family emergency" voice scams; no 2025–2026 Indian survey on voice-clone prevalence found (Moneylife's ORF 2025 attribution is unverified).
- No Jio or Vi AI call-fraud product details found (only Jio's compliance with DoT carrier blocks).
- No 2025 full-year digital-arrest loss total found.

## KQ6. Legal/consent constraints on analyzing the other party's call audio (India), with a US/EU one-liner

### Takeaway
India has no call-recording statute; a participant may record/analyze their own call (one-party in practice) but the other party's voice is personal data under the DPDP Act 2023, so an app vendor processing it is a data fiduciary needing notice/consent unless the processing stays entirely on the user's device for a "personal or domestic purpose." On-device, ephemeral, non-stored analysis (the Google/LG Uplus pattern) is the design that minimizes DPDP/IT-Act exposure. US: one-party federal rule but ~12 all-party states (CA, FL, IL, MD, MA, PA, WA, etc.); EU: GDPR applies to any processing of call audio, with several states requiring all-party or affirmative consent for company recording.

### Cited Findings
- "India does not have a specific law which addresses the recording of phone calls"; a participant may record but "may be liable to legal action" if it breaches privacy; recording a call you are not party to requires prior consent; tapping only by court order — [Wikipedia: Telephone call recording laws](https://en.wikipedia.org/wiki/Telephone_call_recording_laws)
- Voice data "does amount to personal data under the DPDPA," and recording the voice by any party amounts to processing personal data; the EU household exemption analogy fails once data leaves the personal sphere — [SCC Online, Oct 22 2025](https://www.scconline.com/blog/post/2025/10/22/covert-voice-recording-matrimonial-disputes-privacy-infringement-dpdpa/)
- DPDP Act personal/domestic-purpose exemption sits at Section 3(c)(i) (processing by an individual for personal or domestic purposes) — [dpdpa.com s.3](https://dpdpa.com/dpdpa2023/chapter-1/section3.html); [KPMG DPDP summary](https://assets.kpmg.com/content/dam/kpmg/in/pdf/2023/08/decoding-the-digital-personal-data-protection-act-2023.pdf)
- Smart-speaker analysis: third parties in the room/call "who do not want their voices processed... receive no notice at all" — the same problem for the remote caller — [RSRR](https://www.rsrr.in/post/from-living-rooms-to-courtrooms-smart-speakers-under-india-s-data-protection-and-evidence-law)
- Vendor compliance guides: DPDP consent must be "free, specific, informed" via clear affirmative action, not implied by staying on the line; IT Act s.43A (sensitive personal data handling) and s.72 (unauthorized disclosure) apply; recordings admissible under Evidence Act s.65B — [Exotel](https://exotel.com/glossary/call-recording-compliance-in-india/); [BnB Legal](https://bnblegal.com/article/call-recording-legal-in-india/)
- Google's design: audio "processed ephemerally," no audio/transcript stored or sent — [Google](https://blog.google/security/new-ai-powered-scam-detection-features/); LG Uplus: "audio data remained on the user's device at all times" — [GSMA](https://www.gsma.com/solutions-and-impact/technologies/security/scams/wp-content/uploads/2025/08/Case-Study_Real-time-On-device-Vishing-Detection-and-Anti-DeepVoice-Protection-v2.pdf)
- US: all-party consent in California, Connecticut (electronic), Florida, Hawaii (private place), Illinois, Maryland, Massachusetts, Montana (notification), New Hampshire, Oregon (in-person), Pennsylvania, Washington; ~30 one-party states; California's rule applies to calls with any California participant — [Wikipedia](https://en.wikipedia.org/wiki/Telephone_call_recording_laws)
- EU: GDPR "applies to any processing of private conversations" (NL entry, citation-needed flag); Denmark requires affirmative consent for company recording (2019 DPA); Finland requires informing participants; Germany requires all-party consent — [Wikipedia](https://en.wikipedia.org/wiki/Telephone_call_recording_laws)

### Inferences
- For an Indian consumer app: keep inference on-device, don't persist or upload the remote party's audio/transcript, and position the processing as the *user's* personal-purpose activity; any cloud scoring of the other party's voice makes the vendor a data fiduciary for a non-consenting data principal. Enterprise call-center deployment (Pindrop-style) needs an IVR consent notice.
- The DPDP Rules (2025) and the Telecommunications (User Identification) Rules 2025 are the moving pieces to watch.

### Gaps
- No Indian court ruling or DPDP Board guidance found that squarely addresses a consumer app analyzing the remote party's voice in real time; the s.3(c)(i) reading above is inference, not settled law.
- CERT-In position on call-audio AI analysis not found.
