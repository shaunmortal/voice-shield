# Adapting a pretrained anti-spoofing detector (DF_Arena_500M) to a real Indian VoLTE call channel with a few hours of in-domain data

Scope: a few-shot / low-resource adaptation recipe for a frozen XLS-R-based detector on an 8 GB M1. The research date is October 2026. Sources dated 2024 to early 2025 are marked "(older)". Anything under "Inferences" is my reasoning and is not a published result.

## Q1. Few-shot / domain adaptation: frozen SSL embeddings plus a small back-end. Which layers, which classifier, and what published gains with tens to thousands of target samples?

### Takeaway
A frozen XLS-R/WavLM backbone with mean-pooled hidden states and a logistic-regression probe is a well-established, cheap baseline. Mid or lower transformer layers (around layers 6–14 of 24) usually carry the most spoof signal. Published few-shot adaptation results give only modest gains with 10–100 target samples. Large gains (for example 11% EER down to about 1–3.5%) appear only with roughly 100–1000 labelled target samples and some fine-tuning. Plan for a partial recovery, not a return to the clean-audio 0–9% EER.

### Cited Findings
- DF_Arena_500M_V_1 was trained on ASVspoof 2019 and 2024, Codecfake, LibriSeVoc, DFADD, CTRSVDD, SpoofCeleb, MLAAD and EnvSDD. The card does not list replay or telephony data. It reports 5.78% average EER and 10.88% pooled EER, with the worst result on ADD-2022 track 1 (23.98%). It loads through `pipeline("antispoofing", trust_remote_code=True)` at 16 kHz and returns logits. The licence is non-commercial. — [HF model card](https://huggingface.co/Speech-Arena-2025/DF_Arena_500M_V_1)
- (older, 2024) Frozen SSL models with linear probing: a logistic regression on average-pooled representations, predicting bona fide vs spoof, reached 0.96% EER with an MLS-pretrained backbone (WavLM ensemble paper). — [arXiv 2408.07414](https://arxiv.org/pdf/2408.07414)
- A 2026 ensemble paper argues that with a small training set, freezing the backbone and fitting only a logistic-regression head reduces overfitting risk. — [arXiv 2608.01796](https://arxiv.org/pdf/2608.01796) (search-snippet level)
- Layer choice, from an audit of frozen XLS-R with logistic regression:
  - On MLAAD-English, logistic regression peaks at layer 9 (86.83% mean per-generator accuracy) and is most competitive around layers 9–14. Ridge regression peaks at layer 18.
  - On ASVspoof2019 LA, the best frozen logistic-regression probes were at layers 6–8.
  - Source: [arXiv 2606.26384](https://arxiv.org/pdf/2606.26384) (search-snippet level; the same paper argues that linear probes on general SSL features "closely approach the performance of bespoke detectors", so benchmarks may reward general audio understanding over forensic cues — [abstract](https://arxiv.org/abs/2606.26384))
- A layer-wise analysis of SSL models (2025) found that lower transformer layers consistently give the most discriminative deepfake features, and that competitive EER is reachable with only a few lower layers. — [arXiv 2502.03559](https://arxiv.org/abs/2502.03559)
- In XLS-R-128 (24 layers), the top two-thirds of the transformer contributes negligibly after standard fine-tuning, and layer 7 alone is competitive (101M vs 315M parameters). — [NeurIPS 2026 poster](https://neurips.cc/virtual/2026/poster/150091) (search-snippet level)
- An alternative to picking one layer: XLS-R + SLS (ACM MM 2024, older) learns attention weights over all 24 layers and feeds them to a small fully-connected head. — [HF card](https://huggingface.co/sukhdeveyash/XLS-R-SLS-Deepfake-Detection/blob/main/README.md)
- (older, Interspeech 2024) Prompt tuning for test-time domain adaptation (Oiso et al.), using a wav2vec2-300M + AASIST target with In-the-Wild as the target domain:

  | Method | 10 samples | 100 samples | 1000 samples |
  |---|---|---|---|
  | Linear head only | 11.4% | 11.3% | 10.7% |
  | Linear head + prompt tuning | 10.9% | 10.5% | 8.61% |
  | Full fine-tuning | 11.4% | 3.49% | 0.876% |

  - The baseline (no adaptation) EER is 11.4%.
  - The authors report that "fully fine-tuned models immediately overfit" at tiny N.
  - With 50 samples on other targets, head and prompt tuning sometimes gave large drops (16.8 → 7.19, 13.1 → 3.85, 4.34 → 0.79) but sometimes hurt (0.84 → 2.53).
  - Source: [arXiv 2410.09869](https://arxiv.org/html/2410.09869v1)
- (2025) A self-attentive prototypical network for few-shot adaptation reports relative EER reductions of up to 32% (Japanese deepfakes) and 20% (ASVspoof 2021 DF) with as few as 10 in-distribution samples. — [arXiv 2508.13320](https://arxiv.org/abs/2508.13320)
- Some 2025 results summaries state that with N=100, pretrained SSL features adapt quickly without significant overfitting, but that this "breaks down" at N=10. — [arXiv 2508.13320](https://arxiv.org/pdf/2508.13320) (search-snippet level, not verified in full text)
- (2026) An unsupervised DA method needs no target labels: Wav2Vec2 embeddings, statistical transforms, CORAL covariance alignment, then logistic regression. It reaches only 62.7–63.6% accuracy cross-dataset (ASVspoof19 LA ↔ Fake-or-Real), with CORAL and feature selection contributing most. — [arXiv 2603.07935](https://arxiv.org/html/2603.07935v1)
- Training on "presented" data (TTS played or injected through real smartphones into a call centre) is effective. For WavLM-LLGF with a frozen WavLM front-end, average EER over base sets was:
  - Base: 7.1%
  - Base + Presented: 5.8%
  - Base + Augmented: 4.9%
  - Base + Presented + Augmented: 4.8%
  - The authors report a 39% improvement in lab tests and 57% on a real-world benchmark, and conclude that data collection matters more than model size (a 3.55M logmel-ResNet stayed competitive). — [Delgado et al., arXiv 2509.26471 / ICASSP 2026](https://arxiv.org/html/2509.26471v2)

### Inferences
- **Recommended back-end (cheapest first).**
  1. Feature extraction:
     - Run DF_Arena's XLS-R encoder once with `output_hidden_states=True` on every clip.
     - For each layer, mean+std pool over frames, giving 2×1024 dims per layer.
     - Cache the results to disk as `.npy`. For about 1000 clips of 4 s, this should take minutes on MPS.
  2. Per-layer probe:
     - For each layer L in 0..24, fit `StandardScaler → LogisticRegression(C in {0.01, 0.1, 1}, class_weight="balanced")` under grouped CV (see Q2).
     - Pick the layer or layers by grouped-CV EER, not by train fit. Expect the best layer around 6–14.
  3. Combine:
     - Try (a) the concatenation of the best 2–3 layers after PCA to about 64–128 dims, and (b) the original DF_Arena logit as an extra feature (score-level fusion).
     - Keep whichever wins under grouped CV.
  4. Only if time remains, fine-tune the last few conformer/head layers with a low LR. Given the prompt-tuning evidence, this is the step most likely to give big gains at about 1000 samples, but also the most likely to overfit at about 100.
- A small MLP is unlikely to beat logistic regression at N of a few hundred, and it adds overfitting risk. If tried, use one hidden layer of 64 units with dropout and weight decay.
- A one-class model (for example a Gaussian or OC-SVM on bona fide embeddings only) is worth one cheap try. It does not learn the clone-tool identity, so it may generalise better to unseen TTS. However, with telephone-channel bona fide from only 1–3 speakers it will mostly model those speakers. Treat it as a sanity check, not the main system.
- Per-utterance CMVN on frame features before pooling removes stationary channel colouration (loudspeaker or phone frequency response). This helps channel invariance, but it can also erase some spoof cues. Test it with and without; it is a single flag.
- **Segment length.** Use 3–6 s VAD-trimmed speech segments. The Delgado et al. real-world benchmark averaged checkpoints of 2–15 s of net speech ([2509.26471](https://arxiv.org/html/2509.26471v2)), and DF_Arena was trained on utterance-length clips. At test time, average segment scores per call.
- **Data per class.** Tens of minutes per class gives roughly 300–600 four-second segments per class. That matches the 100–1000 regime where the published adaptation gains appear. Real independence is much smaller, though: count calls × sentences × speakers, not segments.
- **Expected gains (inference).**
  - A logistic regression on frozen mid-layer features with about 300+ grouped segments per class should plausibly lower the in-channel EER from 35–40% to somewhere around 10–25%.
  - Reaching under 10% would most likely need the clone and bona-fide conditions to differ in something real (for example loudspeaker vs mouth; see Q2) or need fine-tuning.
  - These numbers are extrapolated from ReplayDF (RIR augmentation took the EER from 18.2% to 11.1%), from prompt tuning (head-only gains of about 1–3 points at N=100–1000), and from Delgado et al. (relative 20–40% gains). They are not measured on this channel.

### Gaps
- I found no published paper that adapts specifically to a real Indian VoLTE (AMR-WB/EVS) channel or to a scrcpy capture path.
- I found no direct head-to-head of weighted-sum vs single-layer vs last-layer for a frozen XLS-R under telephone or replay conditions. The layer findings above come from clean LA/MLAAD-style data.
- The full text of 2508.13320 (N sweep, absolute EERs) and the per-layer tables of 2502.03559 were not retrieved.

## Q2. Avoiding shortcuts (speaker, text, session, loudspeaker vs mouth) with a small target set: splits and data-collection design

### Takeaway
With tens of minutes of data, the classifier can easily learn the call session, the sentence text, the speaker, or "loudspeaker vs mouth" instead of "synthetic". Collect in a paired, interleaved design, split by group, and report several bona-fide definitions separately.

### Cited Findings
- Leading-silence shortcut: in FakeAVCeleb and AV-Deepfake1M, a silence-only classifier exceeds 98% accuracy, and detectors degrade when the silence is removed. ASVspoof19 also leaks labels through silence duration and bitrate. — [Smeu et al., CVPR 2025, arXiv 2412.00175](https://arxiv.org/html/2412.00175v3)
- In replay settings, the replayed bona fide (RB) class is the hardest because it "lacks synthetic artifacts". In EchoFake's open-set (unseen device) test:
  - RB accuracy for the baselines was only 66–68%.
  - Replayed-fake accuracy was 76–97%.
  - Closed-set (seen devices) RB accuracy was about 99.4–99.8%.
  - This shows that device and room conditions are memorised. — [EchoFake, arXiv 2510.19414](https://arxiv.org/html/2510.19414v1)
- EchoFake notes that ASVspoof PA contains replayed bona fide speech but no replayed deepfakes, and that it relies on simulated playback. — [arXiv 2510.19414](https://arxiv.org/html/2510.19414v1)
- ReplayDF replays both bona fide and spoof. Bona-fide accuracy stayed high (97.7%) while spoof detection collapsed. — [arXiv 2505.14862](https://arxiv.org/html/2505.14862v2)
- Delgado et al. treat injected-into-phone bona fide (MLS-Synth/inj, 5,965 samples) as a way to give bona fide the telephone processing too. They recommend a separate playback-detection model because playback attacks remained the weakest point (76.3% detection at 1% FAR vs 88.2% for injection). — [arXiv 2509.26471](https://arxiv.org/html/2509.26471v2)

### Inferences
- **Threat model.**
  - The realistic attack is a clone played through a loudspeaker into a phone, or injected directly.
  - Real bona fide is a live human speaking into the phone.
  - A loudspeaker replay of a real human recording is, by definition, a replay attack (ASVspoof PA). Calling it "bona fide" teaches the model to ignore the loudspeaker.
- **Recording conditions.** Record three conditions over the same channel, ideally in the same calls:
  - **H-live:** a human speaks the sentence live into the calling phone.
  - **H-replay:** the same human's clean recording of the same sentence, played from the same laptop speaker at the same position.
  - **C-replay:** F5-TTS and Chatterbox clones of the same sentences, played from the same speaker.
- **Report two tasks separately.**
  - **Task A (deployment):** H-live vs C-replay. Easy to win, but the model may simply detect "loudspeaker". That is arguably acceptable for this threat model, since Delgado et al. propose a playback detector, but it will false-alarm on legitimate speakerphone or Bluetooth-speaker users.
  - **Task B (true synthetic-cue test):** H-replay vs C-replay. Same loudspeaker and same path, so only the TTS-ness differs. If Task B stays near 35–40% while Task A is near 0%, the detector is a replay detector, not a clone detector. Say so honestly.
- **Interleaving.** Interleave classes within each call, for example alternating H-live, C-replay and H-replay every few sentences. Per-call network state (AMR-WB vs EVS mode, jitter, packet loss) then cannot become a class shortcut. Never record "all bona fide in call 1, all clones in call 2".
- **Paired text.** Use the same sentence list for every class, so content and lexical cues cannot separate classes. Split by sentence ID.
- **Speakers.** Use at least 2–3 team members as bona-fide speakers and clone each of them. Use leave-one-speaker-out CV.
- **Splits.** Use `GroupKFold` or `LeaveOneGroupOut` from sklearn with groups set to the call/session, then repeat with groups set to the speaker and to the sentence. Never let segments of the same utterance land in both train and test (segmenting one clip into 4 s windows leaks).
- **Leave-one-tool-out.** Train with F5-TTS clones and test on Chatterbox, and the reverse, to check that the model is not just fingerprinting one TTS.
- **Preprocessing.** Apply the same VAD trim, the same loudness normalisation (for example −23 LUFS or peak normalisation) and the same resampling to 16 kHz to all classes. This removes silence, level and sample-rate shortcuts (the scrcpy capture may vary between 8 and 16 kHz; resample everything identically).
- **Variety.** Vary the playback volume, laptop-to-phone distance, room and phone where possible, at least two of each. Hold one condition out for test.

### Gaps
- I found no published study of shortcut learning specifically in few-shot channel adaptation of anti-spoofing models. The split rules above follow general ML practice and the confounds documented in the datasets cited.

## Q3. Which detector families are most robust to over-the-air replay plus telephony, and is there an open pretrained replay-aware model?

### Takeaway
SSL-front-end detectors (wav2vec2/XLS-R + AASIST and similar) degrade least under replay, but all published open detectors degrade substantially. Training or adapting on real presented/replayed data, plus RIR augmentation, is the only consistently supported fix. I found no well-documented open pretrained model that is trained for both replayed deepfakes and telephony. EchoFake and ReplayDF are the open data resources.

### Cited Findings
- ReplayDF (Interspeech 2025) EERs, out-of-the-box checkpoint → ReplayDF:

  | Model | Baseline | ReplayDF |
  |---|---|---|
  | Whisper | 44.7% | 49.5% |
  | Raw PC Darts | 32.1% | 43.9% |
  | RawNet2 | 25.9% | 43.1% |
  | TCM ADD | 13.3% | 37.3% |
  | RawGAT-ST | 19.8% | 40.2% |
  | W2V2-AASIST | 10.6% | 24.8% |

  - Retrained W2V2-AASIST went from 4.7% to 18.2% EER under replay; RIR-augmented retraining brought ReplayDF EER to 11.09%.
  - Accuracy correlates with replay quality (Pearson 0.423 with MOS, 0.509 with PESQ).
  - Adding synthetic noise barely changes results, so the cause is the convolutional channel, not noise.
  - The dataset has 109 speaker–mic setups, 132.5 h, and is non-commercial. — [arXiv 2505.14862](https://arxiv.org/html/2505.14862v2); [ISCA](https://www.isca-archive.org/interspeech_2025/muller25_interspeech.html); [HF dataset](https://huggingface.co/datasets/mueller91/ReplayDF)
- EchoFake (Oct 2025):
  - 126.4 h, 13,005 speakers, 11 TTS systems.
  - Contains bona fide, replayed bona fide, fake and replayed fake.
  - Replay used MacBook/iPad loudspeakers into an iPhone 13 mini and a Galaxy A54 at 15 and 50 cm, which closely resembles this team's setup.
  - Models trained on existing datasets average 59.6% accuracy on replayed audio.
  - Training on EchoFake gave the lowest weighted-average cross-dataset EER: Wav2Vec2 16.79%, AASIST 30.15%, RawNet2 32.49%.
  - Code, data and the recording tool are at github.com/EchoFake/EchoFake. — [arXiv 2510.19414](https://arxiv.org/html/2510.19414v1)
- Delgado et al. (ICASSP 2026), real-world "Fraud Academy" benchmark:
  - 80 participants, 16+ phones, 5 loudspeakers, 10 TTS engines.
  - Frozen-WavLM LLGF detected 88.2% of injected and 76.3% of playback deepfakes at 1% FAR.
  - The benchmark is private. — [arXiv 2509.26471](https://arxiv.org/html/2509.26471v2)
- SAFE challenge (2025): a blind benchmark with three tiers (raw, compressed/resampled, laundered), 90 h, about 21k samples, 21 real sources, 17 TTS. I did not retrieve its numeric laundered-task results. — [arXiv 2510.03387](https://arxiv.org/abs/2510.03387v2)
- Searching for an HF checkpoint trained on ASVspoof 2019 PA found only a sparsely documented wav2vec2-base model (`WWWxp/wav2vec2_spoof_dection1`, "asvspoof2019" with no partition stated). — [HF](https://huggingface.co/WWWxp/wav2vec2_spoof_dection1/blob/main/README.md?code=true)

### Inferences
- Within today's budget, the most practical replay-aware option is to keep DF_Arena's XLS-R as the frozen feature extractor and train the probe on the team's own real-call data.
- A small optional extension (about 1 h): add EchoFake's MacBook→phone replayed bona fide and replayed fake subsets to the probe's training set. These are closest to this setup. Check the download size and licence first; I did not confirm a dataset licence.
- Cheap augmentation for the training data: convolve the team's clean bona fide and clone audio with RIRs, then apply G.711/AMR-NB band-limiting. This follows the ReplayDF RIR-augmentation result and the Delgado "augmented + presented" result. It is a supplement, not a replacement, for real-call data.
- PA-trained (ASVspoof 2019 PA) models detect replay of anything, including human recordings. They would help Task A (live vs played) but not Task B (human-replay vs clone-replay).

### Gaps
- I found no open, well-documented pretrained checkpoint trained on ReplayDF or EchoFake for direct download. EchoFake baseline weights might be in its GitHub repo, but this was not verified.
- I found no telephony-specific (VoLTE/AMR-WB/EVS) replay benchmark numbers.

## Q4. Expected magnitude of improvement and how to report it honestly with small N

### Takeaway
Report EER plus TPR at a fixed FPR with confidence intervals, bootstrapped by call or session group rather than by segment. With a few hundred bona-fide segments, TPR@1%FPR rests on about 3 false alarms and is unstable. Report TPR@5%FPR alongside it and state N.

### Cited Findings
- Published magnitudes, for calibrating expectations:

  | Source | Change | Notes |
  |---|---|---|
  | ReplayDF RIR augmentation | 18.2% → 11.1% EER | |
  | Prompt-tuning paper | 11.4% → 10.5–10.7% EER | Head-only adaptation, N=100–1000 |
  | Prompt-tuning paper | 11.4% → 3.49% / 0.876% EER | Full fine-tuning, N=100 / 1000 |
  | Few-shot prototypical net | 20–32% relative EER reduction | N≈10 |
  | Delgado et al. | 7.1% → 4.8% EER | Presented + augmented data |

  Sources: [2505.14862](https://arxiv.org/html/2505.14862v2), [2410.09869](https://arxiv.org/html/2410.09869v1), [2508.13320](https://arxiv.org/abs/2508.13320), [2509.26471](https://arxiv.org/html/2509.26471v2)
- For per-attack EERs with few trials, the SASV/UDA anti-spoofing work reports parametric 95% CIs computed from the EER and the target and non-target trial counts with Z=1.96. — [arXiv 2203.10992](https://arxiv.org/pdf/2203.10992)
- The `confidence_intervals` toolkit (Ferrer) implements bootstrap CIs for metrics including EER and supports bootstrapping by condition or group. — [GitHub luferrer/ConfidenceIntervals](https://github.com/luferrer/ConfidenceIntervals); [PyPI](https://pypi.org/project/confidence-intervals)
- NIST speaker-recognition evaluations use nonparametric two-sample bootstrap for uncertainty of detection costs. — [NIST IR 7722](https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7722.pdf)

### Inferences
- **Honest reporting template.**
  1. Before adaptation: DF_Arena raw-logit EER on the held-out calls.
  2. After adaptation: probe EER on held-out calls or speakers, with no data from those calls in training.
  3. A 95% CI from 1000× bootstrap that resamples calls (or speaker×session groups) with replacement, not segments.
  4. TPR at 1% and 5% FPR, with the bona-fide count stated (for example "FPR resolution = 1/n_bona").
  5. Separate rows for Task A (H-live vs clone) and Task B (H-replay vs clone), and for leave-one-TTS-out.
  6. Call-level results from mean-of-segment scores, labelled separately from segment-level results.
- **Rule of three.** If zero false alarms are seen in n bona-fide trials, the 95% upper bound on FPR is about 3/n. With n=200, claiming "<1% FPR" is not supported; the bound is about 1.5%.
- **Calibration.** Set the operating threshold on a calibration split separate from the test split. Picking the threshold at EER on test data is optimistic.
- **Interpreting the results.** If there are only 2–4 independent calls, the CI will be very wide (likely ±10+ EER points). Present the result as "promising on N calls", not as a solved problem.

### Gaps
- I found no paper comparing bootstrap and parametric EER CIs at very small N in anti-spoofing specifically.

## Q5. Practical code-level guidance (M1 8 GB, under 3 h compute)

### Takeaway
One feature-extraction pass with all hidden states cached, then sklearn probes under grouped CV: the whole loop takes minutes on an M1. Spend the remaining hours on data collection (the strongest lever per Delgado et al.) and on honest splits.

### Cited Findings
- DF_Arena exposes logits through an HF pipeline with `trust_remote_code`, at a 16 kHz input rate. — [HF model card](https://huggingface.co/Speech-Arena-2025/DF_Arena_500M_V_1)
- Frozen-feature + logistic-regression probes are a standard, low-overfitting approach for small data. — [2408.07414](https://arxiv.org/pdf/2408.07414); [2608.01796](https://arxiv.org/pdf/2608.01796)
- Mid layers (around 6–14) peak for logistic-regression probes on XLS-R. — [2606.26384](https://arxiv.org/pdf/2606.26384); [2502.03559](https://arxiv.org/abs/2502.03559)
- Data realism (presented data) beats model size. — [2509.26471](https://arxiv.org/html/2509.26471v2)

### Inferences (concrete recipe; not from a single published source)
1. **Data (2–3 h wall clock).**
   - Use 40–60 phonetically varied sentences of 4–8 s each.
   - Per speaker (2–3 people), record H-live, H-replay, C-replay(F5) and C-replay(Chatterbox) within the same calls, interleaved. Make 4–6 calls with different volume, distance and room.
   - Target at least 15 min per class after VAD, which gives about 200–300 four-second segments per class per task.
2. **Preprocessing.**
   - Resample to 16 kHz mono and trim with VAD (silero-vad or webrtcvad).
   - Apply the same RMS/LUFS normalisation to every class.
   - Cut 4 s windows with a 2 s hop, and keep `utt_id`, `call_id`, `speaker`, `sentence_id`, `tool` and `condition` metadata for every window.
3. **Feature extraction (about 10–20 min on MPS).**
   - Load the DF_Arena model and get the XLS-R submodule.
   - Run `model(..., output_hidden_states=True)` under `torch.no_grad()`, using fp32 (fp16 on MPS can be flaky). Use batch size 1–4 to stay within 8 GB.
   - For each of the 25 hidden states, store mean and std over time (optionally after per-utterance CMVN), plus DF_Arena's own logit.
   - Save everything as one `.npz` file.
4. **Probe (minutes).**
   - Use `make_pipeline(StandardScaler(), LogisticRegression(C=c, class_weight="balanced", max_iter=2000))`.
   - Score each layer under `LeaveOneGroupOut(groups=call_id)` and pick the best layer by mean held-out EER.
   - Then try top-3 layer concatenation with `PCA(n_components=64)`, and fusion with the DF_Arena logit.
   - Report Task A and Task B, plus leave-one-TTS-out.
5. **Optional (about 1 h).** A LoRA or last-2-layers fine-tune of the DF_Arena head on cached frame features, or adding EchoFake replay subsets. Do this only if the grouped-CV probe plateaus and at least 500 segments per class are available.
6. **Deployment.**
   - At call time, score each 4 s window with the probe, average over the call, and threshold at a value set on held-out calls at 5% FPR.
   - Show the raw DF_Arena score next to the adapted score.

### Gaps
- I did not verify the internals of DF_Arena's `trust_remote_code` model, such as whether the XLS-R submodule exposes `output_hidden_states` directly or needs a forward hook. Check this first.
- Actual MPS throughput for a 300M XLS-R on an 8 GB M1 was not measured in any source found. The 10–20 min estimate is an inference.
