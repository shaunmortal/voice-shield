# Building a Telephone-Channel Cloned-Voice Test Set and Fast-Adapting an Anti-Spoof Detector (M1/8GB, 48h, Oct 2026)

Scope note: this is a defensive security-research setup — one consenting team member clones only their own voice to build a test/eval set and to measure/improve a spoof detector. Findings below reflect that framing. Several figures come from vendor pages, project READMEs, and secondhand review sites; those are flagged.

## Q1: Local voice-cloning tools on M1/8GB, Hindi/Hinglish support, commercial free tiers

### Takeaway
F5-TTS (with a Hindi/Hinglish fine-tune), Chatterbox Multilingual (Hindi included), and GPT-SoVITS are the best-documented local options for Apple Silicon with Hindi; XTTS-v2 and CosyVoice2 are plausible on CPU/MPS but unverified for 8GB. 8GB RAM is the binding constraint — expect to run one model at a time, lean on MLX/quantized ports, and tolerate slow CPU/MPS inference. Commercial free tiers (ElevenLabs, Fish Audio, Cartesia) all offer instant cloning but review sites disagree on commercial-rights/credit details, so confirm on vendor pages.

### Cited Findings
- **F5-TTS** — MIT code; pretrained weights are CC-BY-NC-4.0 (non-commercial, due to Emilia training data). An MLX port (`f5-tts-mlx`, lucasnewman) targets Apple Silicon specifically. ComfyUI's F5 node auto-selects MPS on Apple Silicon. — [HF F5TTS MLX card](https://huggingface.co/aufklarer/F5TTS-v1-Base-MLX-fp16); [ComfyUI F5 node](https://comfy.icu/node/F5TTSEngineNode)
- **F5-TTS Hindi/Hinglish** — A Hinglish (code-switched) fine-tune exists, built on `SPRINGLab/F5-Hindi-24KHz` (151M params, F5-TTS Small); zero-shot cloning from a 3–10s reference + transcript. — [HF F5-TTS-Hinglish](https://huggingface.co/SwarajSolanke-turtle/F5-TTS-Hinglish)
- **Chatterbox (Resemble AI)** — Multilingual V3 is ~500M params, 23+ languages including Hindi; a separate Hindi single-language finetune (`ResembleAI/Chatterbox-Multilingual-hi`) exists for tighter Hindi quality. MPS/Apple-Silicon support claimed only by a third-party mirror (unverified); sample code defaults to `device="cuda"`, so you'd set `mps`/`cpu` and test. — [HF ResembleAI/chatterbox README](https://huggingface.co/ResembleAI/chatterbox/blob/main/README.md); [third-party mirror (MPS claim, unverified)](https://www.mintlify.com/yocxy2/chatterboxyocxy/models/chatterbox-multilingual)
- **GPT-SoVITS** — Best-documented on Apple Silicon: a 2026 guide says M1/M2/M3 is supported (lower perf than NVIDIA, sufficient for inference), recommends 15–20GB free disk. A research paper fine-tuned a voice on 37 min of speech on a 24GB M4 Pro MacBook and had to fix 7 platform incompatibilities incl. pervasive float16 precision errors — expect Mac-specific setup pain. Clones from ~1 min of audio. — [GPT-SoVITS 2026 guide](https://pasqualepillitteri.it/news/7050/gpt-sovits-voice-cloning-guida)
- **XTTS-v2 (Coqui)** — ~2GB model; ~2–3GB VRAM + ~5GB RAM on GPU with DeepSpeed; runs on CPU but slower. No Apple-Silicon figure found. (Note: Coqui shut down; XTTS-v2 weights carry the Coqui Public Model License, non-commercial.) — [XTTS hosting page](https://www.databasemart.com/ai/xtts); [Skyrim mod RAM note](https://www.nexusmods.com/skyrimspecialedition/mods/113445)
- **CosyVoice2** — A review site claims the 0.5B model runs "comfortably on an 8GB-RAM laptop" (unverified; check FunAudioLLM/CosyVoice repo). — [CosyVoice2 review](https://www.madebyagents.com/models/cosyvoice-2-0)
- **Qwen3-TTS** — Apache 2.0 family; 10 languages (zh, en, ja, ko, de, fr, ru, pt, es, it) — **Hindi NOT listed**. Clones from ~3s (one source) to 10–15s (another). Cross-lingual cloning supported. — [Qwen3-TTS guide](https://medium.com/@zh.milo/qwen3-tts-the-complete-2026-guide-to-open-source-voice-cloning-and-ai-speech-generation-1a2efca05cd6); [NYU Shanghai writeup](https://rits.shanghai.nyu.edu/ai/%F0%9F%93%A2-qwen3%E2%80%91tts-open%E2%80%91source-text%E2%80%91to%E2%80%91speech-tts-family/)
- **Commercial free tiers** (all secondhand review sites — verify on vendor pages):
  - ElevenLabs: free plan ~10,000 credits/mo; instant clone ~1 min from a short sample; one review says free tier lacks commercial rights. — [dupple voice-cloning roundup](https://dupple.com/learn/best-ai-voice-cloning-tools)
  - Cartesia: reviews disagree whether instant cloning is on the free tier or needs cheapest paid plan; free credits listed as 10K–20K. — [Cartesia vs ElevenLabs](https://cartesia.ai/vs/cartesia-vs-elevenlabs)
  - Fish Audio: free plan ~8,000 credits/mo; one review says enhanced cloning + commercial rights included, another says free tier is non-commercial; clones from ~10–15s. — [dupple ElevenLabs alternatives](https://dupple.com/learn/elevenlabs-alternatives)

### Inferences
- On 8GB RAM you should plan to run exactly one cloning model at a time, prefer MLX/quantized checkpoints (F5-TTS-MLX), and generate clips offline (no real-time needed for a test set). F5-TTS-MLX + the Hinglish fine-tune is the lowest-risk local Hindi path; Chatterbox-Multilingual-hi is the second bet (budget time to switch its device flag to MPS/CPU). GPT-SoVITS is viable but Mac setup will eat hours.
- For maximum tool diversity with least local pain, pair 1–2 local tools (F5-TTS, Chatterbox) with 2–3 commercial free-tier clones (ElevenLabs, Fish Audio, Cartesia/MiniMax). This also gives you "unseen tool" families for honest eval (train detector on some, test on others).

### Gaps
- No primary-source confirmation that any of these produce *good* Hindi/Hinglish quality on M1/8GB specifically — needs a hands-on test.
- MiniMax and PlayHT free-tier cloning terms: not found.
- Fish Speech / OpenAudio S1-mini, Dia, Orpheus, Zonos, Spark-TTS, IndexTTS 2, MaskGCT, VoiceCraft, Kokoro (not a cloner), CosyVoice3, Qwen-TTS: not individually verified this pass for M1/RAM/Hindi.

## Q2: Real-time voice conversion on Mac (can a live attack be reproduced for testing)

### Takeaway
Seed-VC is the strongest zero-shot RT-VC option and lists Apple Silicon support; RVC/Applio on Apple Silicon is historically troubled (MPS shader errors reported). Real-time, GPU is strongly recommended — on an M1/8GB expect to reproduce live conversion only marginally; for a test set, offline conversion is more reliable.

### Cited Findings
- **Seed-VC (Plachtaa/seed-vc)** — Zero-shot VC, real-time VC, and singing VC from a 1–30s reference, no training. README quotes ~300ms algorithm delay + ~100ms device delay (~400ms end-to-end), "suitable for online meetings/gaming/streaming." Install needs Python 3.10 on Windows/Linux/Apple Silicon Macs; GPU recommended for real-time. Optional fine-tune from ~1 utterance, ~2 min on a T4. A 2025 arXiv paper uses Seed-VC as a data generator and calls it SOTA on speaker similarity + WER among zero-shot VC. — [Seed-VC README (gittrend mirror)](https://gittrend.io/repo/Plachtaa/seed-vc); [arXiv 2510.09245](https://arxiv.org/html/2510.09245v1)
- **StreamVC** — cited as a mobile codec-based RT system at 70.8 ms latency (useful latency benchmark). — [arXiv 2510.09245](https://arxiv.org/html/2510.09245v1)
- **RVC / Applio on Apple Silicon** — Old AppleVis threads (2023–24): an Apple Silicon user reported RVC "kept trying to use the MPS shaders, which didn't work and gave errors," and gave up. `RVC-Voicechanger` (GitHub) is a real-time RVC desktop app built on IAHispano/Applio; macOS/Apple-Silicon support not stated. — [AppleVis RVC thread](https://www.applevis.com/comment/161372); [RVC-Voicechanger](https://github.com/satiricalguru/RVC-Voicechanger)

### Inferences
- A live scammer attack (RT voice conversion into a call) is reproducible in principle with Seed-VC, but on M1/8GB real-time quality/latency will likely be marginal. For a *test set*, run Seed-VC/RVC offline (file-to-file conversion) — you get the same acoustic artifacts without the real-time constraint.
- w-okada voice changer wraps RVC/Seed-VC/etc. and is the usual "live" front-end, but inherits the same Apple-Silicon GPU limitations — not separately verified this pass.

### Gaps
- No independent (non-README) latency measurement for Seed-VC on M1. w-okada and Retrieval-based VC Mac status not directly sourced this pass.

## Q3: Public codec/telephony-degraded deepfake datasets for augmentation/eval

### Takeaway
ASVspoof 5 (codec + neural-codec conditions, telephony Track 2), ASVspoof 2021 DF (compressed/in-the-wild), CodecFake/CodecFake+ (neural-codec deepfakes), MLAAD (multilingual), and In-the-Wild are the core resources. For Hindi specifically, IndicSynth (12 Indian languages incl. Hindi, 4,000+ hrs, ACL 2025 Outstanding Paper) is the single best fit; SEA-Spoof and HAV-DF also include Hindi. For channel/replay realism, EchoFake and ReplayDF are purpose-built.

### Cited Findings
- **ASVspoof 5** — Crowdsourced from MLS English (not VCTK); applies codecs including a neural-network-based codec to bona fide + spoof data. Track 1 includes conventional + neural codecs; Track 2 is the telephony-style scenario. — [ASVspoof 5 paper (arXiv 2408.08739)](https://arxiv.org/pdf/2408.08739); [SZU-AFS system paper](https://arxiv.org/html/2408.09933v1)
- **ASVspoof 2021 DF** — Hosted on Zenodo record 4835108 (LA/PA/DF subsets), Open Data Commons Attribution Licence. Keys/metadata released separately (e.g. `asvspoof.org/resources/DF-keys-stage-1.tar.gz`). DF targets manipulated, *compressed* speech posted online; source beyond VCTK includes undisclosed corpora. — [ASVspoof 2021 paper (arXiv 2210.02437)](https://arxiv.org/html/2210.02437v3)
- **In-the-Wild** — Distributed via Fraunhofer AISEC (`deepfake-demo.aisec.fraunhofer.de/in_the_wild`); real-world celebrity/politician audio; direct-download/Zenodo status not confirmed this pass. — [AISEC In-the-Wild](https://deepfake-demo.aisec.fraunhofer.de/in_the_wild)
- **CodecFake (original)** — Zenodo-hosted (records 11169871 / 11125029); 1,058,216 samples from 7 neural codecs; aimed at codec/ALM-based deepfake detection. — [Zenodo 11169871](https://zenodo.org/record/11169871); [CodecFake paper (arXiv 2405.04880)](https://arxiv.org/pdf/2405.04880)
- **CodecFake+ (newer, separate)** — `huggingface.co/datasets/CodecFake/CodecFake_Plus_Dataset`, MIT license, English; CoRS subset uploaded as multi-part archives (merge with `cat`, extract `tar`), CoSG expected ~2025.11; HF Datasets loader status "TBD." Paper arXiv:2501.08238. — [CodecFake+ HF README](https://huggingface.co/datasets/CodecFake/CodecFake_Plus_Dataset/blob/b24dda894efff390bab8a09e8b0caf762d388d5c/README.md)
- **MLAAD** — Synthetic-only (pair with M-AILABS for real audio); on HF. v6 (26 Apr 2025): 420.7 hrs, 91 TTS models, 38 languages. v9 (Jan 2026): 687.4 hrs, 140 models, 51 languages. Hindi inclusion NOT confirmed (language tables not in results). — [MLAAD paper (arXiv 2401.09512 v9)](https://arxiv.org/html/2401.09512v9); [MLAAD AISEC page](https://deepfake-demo.aisec.fraunhofer.de/mlaad)
- **IndicSynth** (best Hindi fit) — 12 Indian languages incl. Hindi, 4,000+ hrs synthetic, for anti-spoofing; SBILab IIIT-Delhi; ACL 2025 Outstanding Paper. Source speech from IndicSUPERB. Access: `github.com/vdivyas/IndicSynth` + HF mirror `vdivyasharma/IndicSynth` (has a Hindi loader example). License not stated in results. Caveat: transcripts are generation prompts, not guaranteed aligned. — [IndicSynth ACL 2025](https://aclanthology.org/2025.acl-long.1070); [AIKOSH listing](https://aikosh.indiaai.gov.in/home/datasets/details/indicsynth.html); [HF mirror](https://huggingface.co/datasets/vdivyasharma/IndicSynth)
- **SEA-Spoof** (Sept 2025) — 300+ hrs paired real/spoof across Tamil, Hindi, Thai, Indonesian, Malay, Vietnamese. — [arXiv 2509.19865](https://arxiv.org/html/2509.19865v2)
- **HAV-DF** (Nov 2024) — Hindi audio-video deepfake dataset (face-swap, lip-sync, voice-clone); detection accuracy lower than on English datasets. — [arXiv 2411.15457](https://arxiv.org/pdf/2411.15457)
- **SpoofCeleb** — Built on VoxCeleb1, 23 contemporary TTS systems trained in real-world *noisy* conditions. — [ASVspoof 5 paper context](https://arxiv.org/pdf/2408.08739)
- **EchoFake** (replay/channel) — Pairs TTS speech with *replayed* speech under varied recording configs; open-set split uses unseen speakers/systems/replay conditions. — [arXiv 2510.19414](https://www.arxiv.org/pdf/2510.19414)
- **ADD-C benchmark** — Tests detectors under codec compression + packet loss; finds significant robustness decline. — [arXiv 2504.12423](https://arxiv.org/html/2504.12423v2)

### Inferences
- For *augmentation* on a tiny M1 budget, don't download the giant corpora whole — pull a sampled subset of ASVspoof 2021 DF + CodecFake, plus IndicSynth-Hindi, and rely mostly on your own codec-augmented clips (Q4/Q5).
- For *honest unseen-tool eval*, IndicSynth/MLAAD give you deepfakes from TTS systems not in your own clone set — good held-out families.

### Gaps
- Confirmed Hindi presence in MLAAD, and licenses for IndicSynth / In-the-Wild / LibriSeVoc / DECRO / HABLA / Fake-or-Real: not verified this pass.

## Q4: Fast adaptation recipes (fine-tune + calibrate on a few hundred clips)

### Takeaway
The standard strong baseline is wav2vec2/XLS-R front-end + AASIST back-end, fine-tuned with RawBoost (telephony/codec augmentation, needs no external data). For few-shot/low-compute adaptation, LoRA on the wav2vec encoder beats full fine-tuning for out-of-domain generalization. Per-channel score calibration (temperature/Platt) is a known, separately-studied deployment concern — EER alone hides threshold-transfer failure.

### Cited Findings
- **RawBoost** (TakHemlata/RawBoost-antispoofing, ICASSP 2022, EURECOM) — Raw-waveform augmentation needing no external noise/IR data; combines noise + distortion types to simulate telephony; improved a strong raw end-to-end baseline by **27% relative** on ASVspoof 2021 LA. Repo built on RawNet2 (ASVspoof 2021 baseline); provides train/eval commands + pretrained model (`RawBoost.py`, `data_utils_rawboost.py`). Train cmd example: `python main.py --track=LA --loss=WCE --lr=0.0001 --batch_size=128`. — [RawBoost repo](https://github.com/TakHemlata/RawBoost-antispoofing); [arXiv 2111.04433](https://arxiv.org/abs/2111.04433)
- **wav2vec2 + AASIST baseline** — Tak et al. 2022: fine-tuned wav2vec 2.0 + augmentation reached 0.82% EER (ASVspoof 2021 LA) and 2.85% EER (DF). This is the well-known baseline for this family. — [Fraunhofer summary of arXiv 2202.12233](https://deepfake-demo.aisec.fraunhofer.de/related_work/2202.12233)
- **SZU-AFS (ASVspoof 5)** — Wav2Vec2 front-end + AASIST back-end; compares single/random/cascade augmentation policies during fine-tuning, plus a gradient-norm co-enhancement step. Good template for an augmentation-policy sweep. — [arXiv 2408.09933](https://arxiv.org/html/2408.09933v1)
- **LoRA for generalization** (arXiv 2509.13878, Sept 2025) — Full fine-tuning struggles out-of-domain (EER >19% on ASVspoof 5). A single rank-8 LoRA in Wav2Vec2 reached avg EER 8.22%; a dense mixture of three rank-8 experts reached 6.08%. Directly supports LoRA/adapter approach for few-shot, low-compute adaptation. — [arXiv 2509.13878](https://arxiv.org/html/2509.13878v1)
- **Scalable AASIST** (arXiv 2507.11777, Jul 2025) — Freezes wav2vec 2.0 encoder, swaps AASIST graph attention for multi-head attention; 7.6% EER on ASVspoof 5. Freezing the encoder = much lower memory, relevant for 8GB. — [arXiv 2507.11777](https://arxiv.org/html/2507.11777v1)
- **Calibration** (arXiv 2606.21584, "When EER Hides Deployment Failure") — Audits threshold transfer + unlabeled score calibration for speech deepfake detectors; uses SSL-AASIST (wav2vec2 XLS-R + AASIST), treats output logits as scores. Establishes that per-deployment calibration matters beyond EER. — [arXiv 2606.21584](https://arxiv.org/pdf/2606.21584)

### Inferences
- Recommended 48h recipe: take a pretrained SSL-AASIST (or RawBoost's pretrained RawNet2), **freeze the SSL encoder**, add a small LoRA/adapter + classifier head, fine-tune on a few hundred bona-fide + codec-augmented clone clips with RawBoost + ffmpeg codec augmentation (Q5). Freezing + LoRA keeps it feasible on M1/8GB (CPU/MPS). Then fit a per-channel temperature/Platt scaler on a held-out calibration split and report EER + TPR@1%FPR per channel.
- Train on a subset of your clone tools, hold out others for "unseen tool" EER to report generalization honestly.

### Gaps
- No single paper found combining per-channel temperature calibration + LoRA on wav2vec for telephony specifically — the recipe above is assembled from separate sources.
- No sourced EER-improvement number for codec augmentation on *Hindi/telephone* data specifically.

## Q5: Simulate the telephony channel offline, and play a clip INTO a real call

### Takeaway
ffmpeg/sox can reproduce the telephone channel: resample to 8kHz mono, band-limit ~300–3400 Hz, and round-trip through a telephony codec (AMR-NB, G.711 µ-law, Opus-NB, optionally AMR-WB). To get a clip into a real call for detector testing, the robust/legal approach is acoustic playback: play the clip through a loudspeaker next to the sending phone (this is exactly the "presentation phase" that research shows matters). For digital routing, BlackHole on Mac feeds a VoIP/softphone leg. Covert injection into another party's cellular call is out of scope (it is wiretapping/fraud in many jurisdictions, and stock Android blocks it by design).

### Cited Findings
- **ffmpeg codec constraints** — `libopencore_amrnb` encoder refuses sample rates other than 8kHz under strict compliance and accepts only 1 channel (fixed 160-sample frames). So inputs must be resampled to 8kHz mono before AMR-NB encoding. — [FFmpeg libopencore-amr source](https://ffmpeg.org/doxygen/8.0/libopencore-amr_8c_source.html)
- **convan** (reference wrapper) — Converts audio to common VoIP telephony standards: g711a, g711u, g722, g729, opus-nb, opus-wb; wraps ffmpeg + ffmpeg-normalize. Good source for exact per-codec flags. — [convan repo](https://github.com/MrM0bi/convan)
- **BlackHole** (digital routing on Mac) — Free virtual audio loopback driver for macOS; works on Intel + Apple Silicon with no kernel extensions; appears in Audio MIDI Setup. A softphone selects BlackHole as input/output; combine with hardware via an Aggregate/Multi-Output device. Multi-channel builds (2/16/64/128/256ch) exist. — [BlackHole on SourceForge](https://sourceforge.net/app/blackhole-2ch/mac/); [ask.audio Soundflower-replacement writeup](https://ask.audio/articles/this-replacement-for-soundflower-brings-virtual-audio-routing-back-to-newer-macs)
- **Presentation-phase matters** (arXiv 2509.26471, "It's All in the Presentation") — Detectors fail when training ignores how audio arrives through a channel; framework routes raw deepfakes through telephony via direct injection OR loudspeaker playback; reports 39% accuracy gain in realistic lab setups, 57% on a real-world benchmark. Validates loudspeaker playback as a legitimate test method. — [arXiv 2509.26471](https://arxiv.org/pdf/2509.26471)
- **Replay/acoustic coupling** (ReplayDF, Resemble AI) — Re-recorded audio across 109 speaker+microphone setups; the physical speaker→mic path strips artifacts detectors rely on; room impulse responses help evade detection. Confirms acoustic playback meaningfully degrades/realistically transforms clips. — [Resemble ReplayDF](https://www.resemble.ai/resources/replay-attacks-against-audio-deepfake-detection)
- **Android inject constraint** — Stock Android: an app can only access its own mic stream, never another app's audio; silent mic-path splicing is blocked by design. (Reproducing a live injection attack is not achievable on unrooted stock Android.) — [voxbooster Android voice-changer](https://voxbooster.com/blog/voice-changer-for-android)

### Inferences
- Practical offline channel-sim chain (standard ffmpeg usage, codec names confirmed above; verify flags against your ffmpeg build): (1) band-limit + resample: `ffmpeg -i in.wav -af "highpass=f=300,lowpass=f=3400" -ar 8000 -ac 1 band.wav`; (2) AMR-NB round-trip: `ffmpeg -i band.wav -ar 8000 -ac 1 -c:a libopencore_amrnb -b:a 7.4k out.amr && ffmpeg -i out.amr amr_out.wav`; G.711 µ-law: `-c:a pcm_mulaw`; Opus-NB: `-c:a libopus -b:a 12k -application voip`. Apply several codecs to produce multiple channel conditions matching your real-call recording.
- Cheapest realistic "into a call" method for the hackathon: play each codec-augmented clip from a laptop speaker (or small BT speaker) held next to the *consenting team's own* sending phone during a call between two team phones, and capture via scrcpy `voice-call` on the receiving side. This reproduces the presentation phase (speaker→mic + cellular codec) that the research says dominates. Digital alternative: BlackHole → a VoIP/softphone app on a team-controlled line.
- Align your offline sim to the *measured* channel: record a known clip through the real call first, inspect its band/codec, then pick the ffmpeg codec/bitrate that matches (Indian cellular commonly AMR-NB/AMR-WB).

### Gaps
- Exact per-codec ffmpeg flags from convan not fetched (read its source for G.729/G.722 which need extra libs). AMR-WB (`libvo_amrwbenc`) availability depends on your ffmpeg build.
- No source giving the exact codec used by a specific Indian carrier's VoLTE path — determine empirically from a test recording.

## Q6: Test methodology (clip count, metrics, honest unseen-tool reporting)

### Takeaway
Report EER and TPR@1%FPR (not accuracy — fraud is rare so accuracy misleads), stratified by channel condition and by clone tool, with a clear seen/unseen-tool split. Use an existing benchmark toolkit (AUDDT) to sanity-check against pretrained detectors across many datasets.

### Cited Findings
- **Metrics** — For rare-fraud detection, accuracy is misleading; use ROC AUC, EER, precision/recall, and FPR at fixed TPR. (practitioner blog, not peer-reviewed.) — [kunalganglani AI voice detector test](https://www.kunalganglani.com/blog/ai-voice-detector-accuracy-test.md)
- **AUDDT** (arXiv 2509.21597) — Unified benchmark toolkit; automated benchmarking of pretrained detectors across 31 datasets with category-by-category analysis. Use to establish baselines before/after your fine-tune. — [arXiv 2509.21597](https://arxiv.org/pdf/2509.21597)
- **Unseen-condition weakness is the known story** — ASVspoof 2021 found key generalization weaknesses for unseen data sources and real-world physical access; EchoFake's open-set split explicitly uses unseen speakers/systems/replay conditions — the standard way to report generalization. — [ASVspoof 2021 (arXiv 2210.02437)](https://arxiv.org/html/2210.02437v3); [EchoFake (arXiv 2510.19414)](https://www.arxiv.org/pdf/2510.19414)

### Inferences
- Minimal honest design: N clone tools (say 5–6: mix local + commercial). For each, generate ~30–50 utterances of the consenting speaker's own voice; add matched bona-fide real recordings of that speaker; pass all through each channel condition (clean, AMR-NB, G.711, Opus, real-call-recorded). That's a few hundred to ~1–2k clips — feasible in 48h.
- Split: train/calibrate detector on, e.g., 3 tools; hold out the other 2–3 as "unseen tools." Report per-channel and per-tool EER + TPR@1%FPR, plus a single "unseen-tool" number, and state plainly that seen-tool numbers are optimistic. Report the real-call-recorded condition separately as the headline deployment number.
- EER needs enough positives/negatives to be stable; a few hundred clips per condition is a reasonable floor for a hackathon but note confidence is limited.

### Gaps
- No source prescribing an exact minimum clip count for stable EER in this setting — the figures above are reasoned estimates, not sourced.
