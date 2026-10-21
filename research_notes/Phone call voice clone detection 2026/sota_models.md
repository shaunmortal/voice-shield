# SOTA open-source audio deepfake / anti-spoofing models for local telephony-grade detection (state as of 2026-10-21)

Scope: pretrained, open-weight speech deepfake detectors that a 2-person team could run offline on an Apple M1 (8 GB) in ~48 h, with evidence on unseen-attack and codec/telephony generalization. Everything below is sourced; numbers from different papers are NOT controlled comparisons unless noted (Speech DF Arena and the SUPERB-style benchmark are the only unified evaluations). Items older than 2025 are marked "(pre-2025)".

---

## KQ0. Ranked practical shortlist (what to integrate in 48 h)

### Takeaway
Nothing open is "telephony-ready" out of the box; the best open systems are all wav2vec2-XLS-R-300M-class front-ends (~320 M params, ~1.2 GB fp32, fits 8 GB) with a tiny back-end, and they all show 5–11% EER on In-the-Wild, 13–22% on ASVspoof 5 codec-heavy data, and 40–50% (random) on 2026 multilingual in-the-wild sets. The practical ranking below trades generalization evidence against license and integration friction (fairseq-pinned repos vs. plain `transformers` loaders).

### Cited Findings (ranked)

**Tier A — integrate first**

1. **NII Yamagishi-lab "AntiDeepfake" post-trained SSL family (MMS-300M / Wav2Vec2-Large / Wav2Vec2-Small)** — best zero-shot generalization of any open model, but **CC BY-NC-SA 4.0 (research/educational only)**.
   - Variants: XLS-R-2B, XLS-R-1B, MMS-1B, MMS-300M, Wav2Vec2-Large, Wav2Vec2-Small, HuBERT-XL; each in Default (RawBoost aug) and NDA (no aug). Trained on ~56,370 h genuine + ~18,280 h fake, "over 100 languages", including ASVspoof5 (413 h real / 1,808 h fake), MLAAD (378 h, 38 languages), Codecfake/CodecFake, VoxCeleb2-vocoded, FLEURS-R, CVoiceFake. Input 16 kHz, arbitrary length. Inference needs fairseq 0.12.2 + safetensors; code at github.com/nii-yamagishilab/AntiDeepfake — [HF model card (W2V-Large-NDA)](https://huggingface.co/nii-yamagishilab/wav2vec-large-anti-deepfake-nda)
   - Zero-shot EER (RawBoost / no-RawBoost): W2V-Small 95 M: ITW 4.23/4.65, ADD2023 13.02/19.41, DF-Eval-2024 33.33/31.97. W2V-Large 317 M: ITW 1.91/2.25, ADD2023 13.25/12.67, FoR 0.67/0.80, DF-Eval-2024 33.36/30.06. MMS-300M 317 M: ITW 2.90/2.00, ADD2023 7.93/11.22, DF-Eval-2024 32.84/31.39. XLS-R-1B 965 M: ITW 1.35, ADD2023 5.39. XLS-R-2B 2.2 B: ITW 1.23, ADD2023 4.67, DF-Eval-2024 25.76 — [Post-training for Deepfake Speech Detection, arXiv 2506.21090](https://arxiv.org/html/2506.21090)
   - Wav2Vec2-Small card: base facebook/wav2vec2-base, 95 M params, ITW EER 4.24% @thr 0.8128, DF-Eval-2024 33.33%, ADD2023 13.02%, FoR 22.03%, DeepVoice 9.78%; CC BY-NC-SA 4.0 — [HF card](https://huggingface.co/nii-yamagishilab/wav2vec-small-anti-deepfake)
   - Independent leaderboard submissions on the HF SpeechAntiSpoofingBenchmarks ITW arena: Wav2Vec2-Large-AntiDeepfake 2.89%, -NDA 2.94%, XLS-R-2B-NDA 2.99% — [discussion #18](https://huggingface.co/datasets/SpeechAntiSpoofingBenchmarks/InTheWild/discussions/18), [#19](https://huggingface.co/datasets/SpeechAntiSpoofingBenchmarks/InTheWild/discussions/19), [#29](https://huggingface.co/datasets/SpeechAntiSpoofingBenchmarks/InTheWild/discussions/29)
   - No codec-specific or telephony results reported despite codec data in training; Hindi not named in training languages (FLEURS covers 102 languages, so likely present but unconfirmed) — [arXiv 2506.21090](https://arxiv.org/html/2506.21090)

2. **Nes2Net-X (XLS-R-300M front-end + 511 k-param nested back-end)** — Apache 2.0, strongest permissively-licensed ITW number, has an ASVspoof 5 branch.
   - Checkpoints (Google Drive) for ASVspoof21-DF 1.65%/1.49% and ITW 5.52%/5.15% (w/ val aug); LA 2021 best 1.73%; back-end params Nes2Net-X 511 k vs AASIST 447 k vs SLS 23,399 k; needs fairseq commit a54021305d + XLS-R 300M `xlsr2_300m.pt`; `easy_inference_demo.py` for single-file scoring; ASVspoof5 models/scripts released 2025-04-20 in `asvspoof5` branch — [GitHub Nes2Net_ASVspoof_ITW](https://github.com/Liu-Tianchi/Nes2Net_ASVspoof_ITW)
   - Paper (arXiv 2504.05657, 2025) states scripts and pretrained models are public — [search result](https://arxiv.org/html/2504.05657v2)
   - Unified benchmark (Speech DF Arena, trained on ASVspoof19 only): Nes2NetX 317.9 M params, avg EER 16.11%, ITW 7.75, ASV21DF 1.49, ASV24(=ASVspoof5) 22.05, FoR 6.31, CodecFake 39.34, ADD23-R1 21.13 — [Speech DF Arena, arXiv 2509.02859](https://arxiv.org/html/2509.02859)
   - DeepFense re-implementation: Wav2Vec2 + Nes2Net trained on ASVspoof5 gives 5.53% EER on ASVspoof5 eval (codec-heavy) — [DeepFense, arXiv 2604.08450](https://arxiv.org/html/2604.08450)

3. **XLSR + SLS (Sensitive Layer Selection)** — best open-source *average* in the unified Speech DF Arena; license NOT stated in repo.
   - Pretrained ckpt via Google Drive/Baidu; base wav2vec2 XLS-R 300M; ASV21 DF 1.92%, LA 2.87%, ITW 7.46%; Python 3.7, torch 1.12.1, bundled fairseq zip — [GitHub QiShanZhang/SLSforASVspoof-2021-DF](https://github.com/QiShanZhang/SLSforASVspoof-2021-DF)
   - Speech DF Arena: XLSR+SLS 340 M params, avg EER 13.84% (best open), pooled 15.68%, ITW 7.45, ASV24 18.76, FoR 5.07, CodecFake 33.43, ADD22-T1 33.95, ADD23-R1 19.37, DFADD 7.54, SONAR 24.72; "most effective open-source system … lowest EER except the ASVspoof series" — [arXiv 2509.02859](https://arxiv.org/html/2509.02859)

4. **Speech-Arena-2025 DF_Arena models (100M / 500M / 1B)** — easiest load (`transformers` pipeline, `trust_remote_code=True`), trained on MLAAD + ASVspoof5 + Codecfake etc.; **1B is non-commercial**; 100M/500M licenses not shown on org page.
   - DF_Arena_1B_V_1: training = ASVspoof 2019+2024, Codecfake, LibriSeVoc, DFADD, CtrSVDD, SpoofCeleb, MLAAD, EnvSDD; EER ITW 0.91, ASV21DF 1.75, ASV21LA 4.66, FoR 2.92, codecfake 8.37, ADD23-R1 5.08, ASVspoof 2024 17.25, ADD22-T1 22.21; avg 5.92, pooled 9.52; 16 kHz; non-commercial LICENSE.txt — [HF card](https://huggingface.co/Speech-Arena-2025/DF_Arena_1B_V_1)
   - Org lists DF_Arena_1B_V_1, DF_Arena_500M_V_1, DF_Arena_100M_V_1 (updated 2025-12-04), DF_Arena_100M_V_0 — [HF org](https://huggingface.co/Speech-Arena-2025/models)
   - RAPTOR controlled study (2026): DF-Arena 500M ITW 1.76 / ASVspoof-2024 12.39 / avg 5.78 / pooled 10.88; DF-Arena 100M-V1 ITW 2.21 / ASVspoof-2024 21.39 / avg 8.39 / pooled 13.92 — [arXiv 2603.06164](https://arxiv.org/html/2603.06164)

**Tier B — consider**

5. **pellav2 (Pella Research)** — MIT, single-script `transformers` inference, but English/studio-only and weak on noisy real speech.
   - XLS-R-300M backbone, learned layer weighting + linear head, ~300 M params; private training corpus; DFADD 1.9% EER, ITW (random 1/10) 10.9% EER; 57 ms per 4-s crop on T4; threshold 0.5; "noisy real-world channels … raise false positives on genuine speech"; not evaluated on non-English or VC — [HF card](https://huggingface.co/Sadanie/pellav2-audio-deepfake-detector)
   - Podonos studio benchmark (4,524 English clips, ~25 modern TTS/cloning systems): 95.82% acc, F1 0.959, FPR 5.5%, FNR 2.8%; best open model by 32.9 points; .m4a accuracy 93.6% vs 97.1% wav — [Podonos blog](https://www.podonos.com/blog/audio-deepfake-detection-benchmark)

6. **SSL_Anti-spoofing (Tak et al., XLS-R-300M + AASIST, RawBoost) (pre-2025)** — MIT; the only classic open model whose headline number is on telephony-transmitted data (ASVspoof 2021 LA).
   - Pretrained LA/DF ckpts on Google Drive; ASV21 LA 0.82% EER / min t-DCF 0.2066; DF 2.85%; torch 1.8.1, Python 3.7, bundled fairseq — [GitHub TakHemlata/SSL_Anti-spoofing](https://github.com/TakHemlata/SSL_Anti-spoofing)
   - ASVspoof 2021 LA eval data "was sent over a variety of telephony systems including VoIP and PSTN" — [ASVspoof 2021 summary (pre-2025)](https://ar5iv.labs.arxiv.org/html/2109.00537)
   - Speech DF Arena: Wav2Vec2-AASIST 317.84 M, avg 18.02%, ITW 11.19, ASV21LA 0.82, ASV24 16.24, CodecFake 43.36 — [arXiv 2509.02859](https://arxiv.org/html/2509.02859)

7. **XLSR-Mamba** — MIT, HF weights, ITW 6.71%; risk: Mamba SSM kernels on Apple Silicon unverified.
   - HF ckpts AustinXiao/XLSR-Mamba-LA and -DF (319 M); LA 0.93% / t-DCF 0.208, DF 1.88%, ITW 6.71%; Python 3.10, fairseq commit a54021305d; no inference script, no CPU notes — [GitHub swagshaw/XLSR-Mamba](https://github.com/swagshaw/XLSR-Mamba)
   - Speech DF Arena: XLSR Mamba avg 14.21%, pooled 20.12%, ITW 6.70, ASV24 14.40 (best open on ASVspoof5), FoR 6.71 — [arXiv 2509.02859](https://arxiv.org/html/2509.02859)

8. **ISSF-lab WavLM-Large + AASIST (SAFE 2025 runner-up)** — multilingual training incl. MLAAD (Hindi); code public, weights/license unconfirmed.
   - WavLM-Large → 128-d FC → AASIST, RawBoost; trained on ASVspoof19 LA + M-AILABS + MLAAD + CodecFake A2 + Famous Figures + SpoofCeleb (200 k train); SAFE BAC Task1 0.810, Task2 0.819, Task3 0.496; ITW EER 8.42% (vs 35.61% ASVspoof19-only baseline); code github.com/issflab/ssl-antispoofing — [arXiv 2508.20983](https://arxiv.org/html/2508.20983v1)

9. **DeepFense toolkit (Apache 2.0, 2026)** — 456 checkpoints promised but HF link was "anonymous" at fetch time.
   - Front-ends Wav2Vec2/WavLM/HuBERT/EAT/MERT/Whisper/BEATs/Wav2Vec2-BERT; back-ends AASIST/ECAPA/RawNet2/Nes2Net/TCM/MLP/Pool/BiCrossMamba-ST; best ITW 6.98% (W2V2+TCM, ASV19-trained); CodecFake-trained models give best cross-set macro-avg 17.16%; site deepfense.github.io — [arXiv 2604.08450](https://arxiv.org/html/2604.08450)

10. **Fake-Mamba** (Aug 2025, ASRU) — ITW 5.85%, DF 1.74%, LA 0.97%; code github.com/xuanxixi/Fake-Mamba; speed claims are GPU RTF — [arXiv 2508.09294](https://arxiv.org/pdf/2508.09294)

**Tier C — do not rely on (the four HF models the user asked about, see KQ6)**: Gustking/wav2vec2-large-xlsr-deepfake-audio-classification, MelodyMachine/Deepfake-audio-detection-V2, mo-thecreator/Deepfake-audio-detection, Om-Parab/distilhubert-finetuned-audio-deepfake-in-the-wild.

### Inferences
- For a hackathon/research deliverable, AntiDeepfake MMS-300M (or W2V-Small if memory-bound) is the best single pick: it is the only open model post-trained on ASVspoof5 codec data + MLAAD + Codecfake and it leads every ITW leaderboard. If the deliverable must be commercially usable, swap to Nes2Net-X (Apache) or DF_Arena_500M (verify license) and accept ~2–3x higher ITW EER.
- All Tier A/B models share the same 300 M XLS-R front-end; integration cost is dominated by fairseq pinning (Python 3.7–3.10, old torch). The `transformers`-native ones (DF_Arena, pellav2) are the 48 h-safe path; fairseq-based ones need an extra half-day to port the front-end to `torchaudio.models.wav2vec2_xlsr_300m` or HF `facebook/wav2vec2-xls-r-300m`.
- Ensembling two front-ends (e.g., XLS-R-based + WavLM-based) is what every challenge winner did; a 2-model score average is cheap on M1 if both are ≤320 M.

### Gaps
- No independent, unified benchmark includes AntiDeepfake, DF_Arena and pellav2 together on telephony audio; cross-paper numbers above are not controlled.
- DF_Arena_100M/500M license text not retrieved (org page omits it).
- DeepFense checkpoint URLs unverified (anonymous placeholder in paper).
- XLSR-Mamba / Fake-Mamba CPU/MPS runnability (mamba-ssm CUDA kernels) unverified.

---

## KQ1. Which models top ASVspoof 5, In-the-Wild, ADD 2023, SAFE 2025, Deepfake-Eval-2024, and 2026 benchmarks? Which have open weights?

### Takeaway
Challenge winners are ensembles that are almost never released; the open-weight leaders are XLS-R-based single systems (AntiDeepfake, DF_Arena, XLSR-SLS, Nes2Net-X, XLSR-Mamba). On the hardest sets (Deepfake-Eval-2024, ML-ITW 2026) every open model is at 25–50% EER.

### Cited Findings
- **ASVspoof 5 (2024/25)**: 53 teams; closed-condition top-5 reached minDCF < 0.5 and EER < 15%; open condition better, "most strong entries use … SSL models, e.g. wav2vec 2.0"; performance "degrades under adversarial attacks and … neural encoding/compression" — [ASVspoof 5 overview, arXiv 2408.08739](https://arxiv.org/pdf/2408.08739)
- ASVspoof 5 evaluation summary (Jan 2026): Track 1 open top systems used wav2vec 2.0 Large (T45, T43, T23) and WavLM-Base (T36, T27); Track 2 open best min a-DCF 0.07 (T45, wav2vec 2.0 Large CM); Track 2 closed best min a-DCF 0.28; top-3 open systems minDCF < 0.2 on Encodec; narrowband 8 kHz DSP codecs harder than 16 kHz codecs in closed condition — [arXiv 2601.03944](https://arxiv.org/html/2601.03944v1)
- XMUspeech ASVspoof 5 system: closed fusion minDCF 0.478 / EER 20.45%; open fusion minDCF 0.225 / EER 9.36% — [arXiv 2509.18102](https://arxiv.org/pdf/2509.18102)
- Official challenge repo: github.com/asvspoof-challenge/asvspoof5 (no team weights identified) — [search result](https://arxiv.org/pdf/2408.08739)
- **In-the-Wild** (unified Speech DF Arena, all ASV19-trained): XLSR-Mamba 6.70, XLSR+SLS 7.45, Nes2NetX 7.75, TCM 7.79, Wav2Vec2-AASIST 11.19, Whisper-MesoNet 26.72, AASIST 43.00, RawNet2 49.00; proprietary Whispeak 1.26, Resemble 3.94, Syntra 3.97 — [arXiv 2509.02859](https://arxiv.org/html/2509.02859)
- In-the-Wild with large-scale training: AntiDeepfake W2V-Large 1.91%, XLS-R-2B 1.23% — [arXiv 2506.21090](https://arxiv.org/html/2506.21090); DF_Arena_1B 0.91% — [HF](https://huggingface.co/Speech-Arena-2025/DF_Arena_1B_V_1); RAPTOR/DF-Arena 500M 1.76%, mHuBERT-Iter2 (95 M) 1.56% — [arXiv 2603.06164](https://arxiv.org/html/2603.06164)
- **SAFE 2025** (IH&MMSec): Round-1 balanced accuracy — ISP/ISPL (PoliMi) T1 0.87 / T2 0.80 / T3 0.66; ANO 0.74/0.78/0.57; VIP 0.77/0.67/0.55; JAI 0.68/0.72/0.65; DMF 0.67/0.58/0.51. ISPL = attention-gated mixture of LCNN+MelSpec, ResNet+MelSpec, ResNet+LogSpec; ANO = AASIST + sample-weight learning; ISSF = SSL front-end + AASIST; "every team's first submission scored below 0.65 BAC"; paper does not say any winner is open source — [SAFE overview, arXiv 2510.03387](https://arxiv.org/html/2510.03387v2)
- ISPL winning system paper (IEEE WIFS 2025) — [arXiv 2509.17585](https://arxiv.org/abs/2509.17585v1); runner-up (WavLM-Large+AASIST, multilingual) — [arXiv 2508.20983](https://arxiv.org/html/2508.20983v1)
- **Deepfake-Eval-2024**: 56.5 h audio from 88 websites in 52 languages; open-source audio models (AASIST, RawNet2, SSL model P3) lost 48% AUC vs. prior benchmarks; commercial and fine-tuned models better but below forensic analysts — [arXiv 2503.02857](https://arxiv.org/pdf/2503.02857). AntiDeepfake zero-shot 25.8–33.4% EER; fine-tuned XLS-R-1B 8.28% at 50 s — [arXiv 2506.21090](https://arxiv.org/html/2506.21090)
- **ADD 2023**: organizers' review says top systems relied on noise+reverb augmentation; Track 1.2 USTC system = wav2vec2 + AASIST + multi-level augmentation; no public winning code found — [arXiv 2408.04967](https://arxiv.org/html/2408.04967v2), [CEUR Vol-3597 paper 20](https://ceur-ws.org/Vol-3597/paper20.pdf). Open models on ADD23-R1: Nes2NetX 21.13, XLSR+SLS 19.37, AntiDeepfake MMS-300M 7.93, DF_Arena_1B 5.08 — [arXiv 2509.02859](https://arxiv.org/html/2509.02859), [arXiv 2506.21090](https://arxiv.org/html/2506.21090), [HF](https://huggingface.co/Speech-Arena-2025/DF_Arena_1B_V_1)
- **2026 benchmarks**: ML-ITW (Mar 2026; 14 languages incl. Hindi, 24,529 segments, 7 platforms) — all 11 evaluated detectors at 40–50% EER (AASIST 41.85, XLSR+AASIST 49.40, XLSR+SLS 48.83, ML_SSLFG 40.49, ALLM4ADD 43.70); training XLSR+AASIST on SpoofCeleb gave 27.65% — [arXiv 2603.05852](https://arxiv.org/html/2603.05852). SUPERB-style SSL benchmark (Mar 2026) — [arXiv 2603.01482](https://arxiv.org/html/2603.01482). DeepFense (Apr 2026) — [arXiv 2604.08450](https://arxiv.org/html/2604.08450). RAPTOR compact-backbone study (Mar 2026) — [arXiv 2603.06164](https://arxiv.org/html/2603.06164)
- Leaderboards: Speech DF Arena — [HF Space](https://huggingface.co/spaces/Speech-Arena-2025/Speech-DF-Arena), toolkit github.com/Speech-Arena/speech_df_arena; SpeechAntiSpoofingArena (ITW) — [HF Space](https://huggingface.co/spaces/SpeechAntiSpoofingBenchmarks/SpeechAntiSpoofingArena) (dynamic page; could not scrape)

### Inferences
- ITW EER ≈ 1–2% from AntiDeepfake/DF_Arena is partly due to training on much larger, newer fake data; it does not translate to Deepfake-Eval-2024 (still 25–33%) or ML-ITW. Expect similar collapse on Indian-network phone audio unless fine-tuned.
- The "open vs proprietary" gap on ITW (6.7% vs 1.3%) in the ASV19-trained setting is mostly a data gap, closed by AntiDeepfake's post-training.

### Gaps
- Full ASVspoof 5 per-team EER table and Table VI codec-condition mapping were not in the fetched HTML text.
- SAFE Round-2 full leaderboard (stresearch.github.io/SAFE) not fetched.
- Live SpeechAntiSpoofingArena ranking not retrieved (JS-rendered).

---

## KQ2. Which SSL front-ends + back-ends generalize best to unseen attacks? (cross-domain EER)

### Takeaway
Across three independent 2025–26 evaluations, wav2vec2-XLS-R-300M is the best front-end for unseen attacks and codec conditions; among back-ends, SLS, Mamba, TCM and Nes2Net-X are within ~1 pt of each other on ITW (6.7–7.8%) and far ahead of AASIST-on-raw-waveform (43%). Compact 95 M backbones (mHuBERT-147, WavLM-Base+) are within ~1–2 pts of 320 M models on ITW.

### Cited Findings
- SUPERB-style benchmark (20 SSL models, frozen, weighted-sum + MLP head, trained on ASV19): XLS-R lowest mean EER 17.4% (ASV21DF 4.31, ASV5 14.39, ITW 20.07, DF-Eval-2024 45.39, FamousFigures 29.60); UniSpeech-SAT best on ITW 16.79%; WavLM Large mean 20.56%; HuBERT Large 22.71%; wav2vec2 Large (English) 28.65%; w2v-BERT, XLSR-53, XLS-R 1B/2B not tested — [arXiv 2603.01482](https://arxiv.org/html/2603.01482)
- Same paper, ASVspoof 5 codec conditions C01–C11 average EER: XLS-R 13.5%, UniSpeech-SAT 14.0%, WavLM Large 18.1%, SSAST 28.8%, APC 33.3%, FBANK 49.8% — [arXiv 2603.01482](https://arxiv.org/html/2603.01482)
- Speech DF Arena (ASV19-trained): avg EER XLSR+SLS 13.84 < XLSR-Mamba 14.21 < TCM 15.77 < Nes2NetX 16.11 < Wav2Vec2-AASIST 18.02 << WavLM-ECAPA 28.74, Whisper-MesoNet 28.69, HuBERT-ECAPA 33.19, AASIST 34.49, RawGAT-ST 34.92, RawNet2 35.75; "no single model wins on every dataset" — [arXiv 2509.02859](https://arxiv.org/html/2509.02859)
- XLSR-Mamba paper: ITW 6.71 vs XLSR+Conformer+TCM 7.79, XLSR+SLS 7.46, XLSR+Conformer 8.42 — [arXiv 2411.10027](https://arxiv.org/pdf/2411.10027); Fake-Mamba (L) ITW 5.85 ± 0.27 — [arXiv 2508.09294](https://arxiv.org/pdf/2508.09294)
- RAPTOR (2026): 95 M mHuBERT-Iter2 ITW 1.56 / pooled 11.72 vs W2V2-AASIST 317 M ITW 2.12 / pooled 12.46 vs W2V2-TCM 319 M 1.65 / 12.88; MoLEX (376 M MoE) ITW 0.03 but ASVspoof-2024 15.87; WavLM-Base+ 94 M ITW 2.24 / ASVspoof-2024 18.45 — [arXiv 2603.06164](https://arxiv.org/html/2603.06164)
- DeepFense: Wav2Vec2 front-end variants have the widest per-language spread on MLAAD (9.7–12.0%); EAT narrowest; training on CodecFake generalizes best to ITW (12.8%) among training sets — [arXiv 2604.08450](https://arxiv.org/html/2604.08450)
- MoE in SAFE: ISPL attention-gated mixture of spectrogram CNNs won all three tasks — [arXiv 2510.03387](https://arxiv.org/html/2510.03387v2)
- (pre-2025) wav2vec2 fine-tuning caveat: anti-spoofing gains from pretrained SSL "almost disappear if the attacker also makes use of the pretrained models" — [arXiv 2305.15518](https://arxiv.org/abs/2305.15518)
- WavLM fine-tuned multi-layer: 0.65 / 3.50 / 3.19% on ASV19LA / 21LA / 21DF — [search summary](https://arxiv.org/abs/2204.01387v2)

### Inferences
- Front-end choice (XLS-R-300M, multilingual pretraining) matters more than back-end; back-end differences are ≤1 pt on ITW. Pick the back-end with the cleanest license/loader.
- For M1/8 GB, a 95 M backbone (WavLM-Base+ or mHuBERT-147 with a DF-Arena-style head) loses ~0.5–2 pts on ITW but 3–9 pts on ASVspoof5; acceptable only if latency forces it.

### Gaps
- No unified comparison includes w2v-BERT 2.0 or XLSR-53 as front-ends for anti-spoofing.
- Layer-wise results (which XLS-R layers carry spoof cues) not in the 2026 benchmark; SLS paper addresses it but was not fetched.

---

## KQ3. Telephony / codec-augmented training and EER degradation at 8 kHz / AMR-NB / EVS / Opus

### Takeaway
Published evidence is consistent that narrowband/CELP codecs and phone channels degrade detectors (ASVspoof 5: 8 kHz codecs harder than 16 kHz; SAFE: phone codec/Opus hurt; 2025 benchmark: +5.3 pts EER for baselines) and that codec augmentation in training nearly eliminates the gap — but no open model publishes AMR-NB/EVS-specific EER, and the only 8 kHz telephony leaderboards (Podonos) are still empty.

### Cited Findings
- ASVspoof 5 eval set codecs: MP3, Opus, AMR, Speex, M4a, Encodec, MP3+Encodec, plus "a simulated mobile-to-PSTN telephony transmission path"; Track 2 (telephony/SASV) drops non-telephony codecs; closed condition: Encodec hardest, then narrowband 8 kHz DSP codecs, then 16 kHz DSP codecs; top closed system minDCF 0.35 on Encodec vs 0.55 second-best; open-condition top-50% median minDCF 0.26 on Encodec, < 0.2 on other codecs — [arXiv 2601.03944](https://arxiv.org/html/2601.03944v1)
- ASVspoof 5 data: "crowdsourced … adversarial attacks … neural encoding/compression schemes" degrade performance — [arXiv 2408.08739](https://arxiv.org/pdf/2408.08739)
- Benchmark of robustness in real-world communication (2025): codecs AMR-WB, EVS (8–48 kHz), IVAS, Opus, Speex-WB, SILK at packet loss 0/1/5/10/20%, all at 16 kHz; baselines (GMM, LCNN, AASIST) trained on clean lose avg 5.30 pts EER clean→codec; proposed models lose 2.33; with codec+PLR augmented training the gap is 0.003; augmented set 1.83 M utterances; AMR-NB and 8 kHz not tested — [arXiv 2504.12423](https://arxiv.org/html/2504.12423v2)
- Multi-granularity TF-attention paper (2025): same six codecs + packet loss; AASIST trained on degraded data: EER 0.33 (clean) → 0.26/0.27/0.31/0.38/0.77 at PL 0→20%; RawNet2 0.63 → 1.35; LCNN 0.63 → 1.43; CELP codecs "over-quantize or eliminate components that deviate from expected speech norms", suppressing spoof artifacts — [arXiv 2508.01467](https://arxiv.org/html/2508.01467v1)
- SAFE Task 2 (processing incl. Opus, "phone-audio codec", MP3/AAC chains, resampling, neural codecs): Gaussian noise hurt most (ISP 0.87→0.70); speech codecs/filtering (Opus, phone audio, speech filter) and chained MP3/AAC "degraded performance significantly"; neural codecs had little effect (ISP 0.92 Encodec, 0.95 Focalcodec); over-the-air re-recording most damaging in Task 3 (ISP → 0.62) — [arXiv 2510.03387](https://arxiv.org/html/2510.03387v2)
- (pre-2025) Vicomtech ADD 2022 system, XLS-R(128) with FIR band-limit augmentation: ASV21 DF EER no-aug 5.68, FIR-narrowband 6.18, FIR-wideband 4.98; narrowband filters "emulate traditional telephonic systems" and helped LA — [arXiv 2203.01573](https://arxiv.org/pdf/2203.01573)
- (pre-2025) ASVspoof 2021 LA eval = ASV19 data "sent over … VoIP and PSTN"; DF = compressed audio — [arXiv 2109.00537](https://ar5iv.labs.arxiv.org/html/2109.00537); XLS-R+AASIST+RawBoost on 21-LA 0.82% EER — [GitHub](https://github.com/TakHemlata/SSL_Anti-spoofing)
- Speech DF Arena augmentation study: reverberation causes the largest EER increase; XLSR+SLS on LibriSeVoc 1.96% → 21.39% with reverb — [arXiv 2509.02859](https://arxiv.org/html/2509.02859)
- Podonos telephony tracks (8 kHz narrowband 300–3400 Hz: G.711 μ/A-law 64 kbps, AMR-NB 12.2 kbps, G.729 8 kbps, GSM-FR 13 kbps; 16 kHz wideband: EVS-WB 24.4/13.2 kbps, AMR-WB 23.85/12.65 kbps), "both tracks have empty leaderboards" — [Podonos](https://www.podonos.com/blog/audio-deepfake-detection-benchmark)
- Human-perception study: AMR-NB constrains bandwidth to ~300–3400 Hz, removing high-frequency components — [MDPI](https://www.mdpi.com/3939840)
- Resemble AI (vendor claim): retrained model raised VoIP+packet-loss accuracy 88% → 94% — [Resemble changelog](https://www.resemble.ai/changelogs/audio-dfd-model-update-4-eer); a "telephony optimized" model is announced but the page gave no specs/EER — [Resemble blog](https://www.resemble.ai/introducing-telephony-optimized-deepfake-detection-model)
- SafeEar (CCS 2024, pre-2025): codec-augmented training, detector sees only acoustic codec tokens, avg EER 2.02% on four benchmarks; repo github.com/LetterLiGo/SafeEar — [arXiv 2409.09272](https://arxiv.org/html/2409.09272v1)
- Open models with codec data in training: AntiDeepfake (ASVspoof5 + Codecfake + CodecFake) — [HF](https://huggingface.co/nii-yamagishilab/wav2vec-large-anti-deepfake-nda); DF_Arena (ASVspoof 2024 + Codecfake) — [HF](https://huggingface.co/Speech-Arena-2025/DF_Arena_1B_V_1); Nes2Net asvspoof5 branch — [GitHub](https://github.com/Liu-Tianchi/Nes2Net_ASVspoof_ITW)

### Inferences
- Expected degradation for a clean-trained XLS-R detector on AMR-NB/EVS phone audio: at least the +5 pt baseline shift measured at 16 kHz codecs, likely worse at 8 kHz given ASVspoof 5's ordering (8 kHz DSP > 16 kHz DSP in difficulty) and SAFE's phone-codec drop. Treat 10–20% EER on real Indian cellular audio as the realistic starting point for Tier-A models before fine-tuning.
- The cheapest, best-supported mitigation is codec augmentation (ffmpeg `libopencore_amrnb` at 12.2 kbps, `libopus` 8 kHz, band-limit 300–3400 Hz, 1–10% packet loss) on a small local real/fake set, then fine-tune only the back-end/head of a Tier-A model (the papers above show augmentation closes the gap almost entirely).
- Because detectors upsample 8 kHz → 16 kHz anyway, the upper 4 kHz band is empty; models that rely on high-frequency vocoder artifacts (spectrogram CNNs) will suffer more than SSL models.

### Gaps
- No paper reports per-codec EER for AMR-NB or EVS for any open SSL detector; the Indian-cellular (AMR-NB 12.2 / EVS-NB) condition has zero published numbers.
- ASVspoof 5 Table VI (per-codec EER by system) and Track 2 appendix not retrieved.
- Whether AntiDeepfake/DF_Arena include narrowband-simulated data is not documented.

---

## KQ4. Hindi / Indian-language and multilingual evaluation

### Takeaway
Hindi appears in MLAAD, SpeechFake, ML-ITW and the dedicated Indic corpora (IndicSynth, HAV-DF, Indic-CodecFake), and the consistent finding is that English-trained detectors degrade sharply on Hindi/Indic fakes (AASIST 26–40% EER cross-lingual), while XLS-R-based or multilingually-trained models degrade less. No open SSL detector publishes a Hindi-specific EER.

### Cited Findings
- IndicSynth (ACL 2025, outstanding paper): >4,000 h synthetic speech in Hindi + 11 Indian languages, speaker IDs/gender/transcripts; IIIT-Delhi; on HF and AIKosh — [AIKosh](https://aikosh.indiaai.gov.in/home/datasets/details/indicsynth.html), [HF](https://huggingface.co/datasets/vdivyasharma/IndicSynth/commit/5bc5ad7d2132c8421470abe463e2af0ca5e87bdc)
- HAV-DF (Nov 2024, pre-2025): Hindi audio-video deepfake set (face-swap, lip-sync, voice cloning); existing detectors performed worse than on FF++/DFDC — [arXiv 2411.15457](https://arxiv.org/abs/2411.15457v1)
- Indic-CodecFake (Apr 2026): 12 Indic languages from IndicSUPERB re-synthesized through DAC, Encodec, SoundStream, SpeechTokenizer, FunCodec, AudioDec, SNAC, MIMI; AASIST in-domain 12.47% EER; AASIST trained on CodecFake → ICF 40.32%; AASIST cross-lingual 26.74–31.11%, Dravidian↔Indo-European 33.45/38.73%; SATYAM (Whisper+TRILLsson+frozen Qwen2-7B, 3.75 M trainable) 3.27% in-domain, Hindi 2.34%, cross-lingual 6.3–7.1%; dataset/code at helixometry.github.io/IndicFake — [arXiv 2604.19949](https://arxiv.org/html/2604.19949)
- ML-ITW (Mar 2026) includes Hindi among 14 languages; all 11 detectors 40–50% EER overall; per-language macro-avg AASIST 35.24%, ML_SSLFG 44.06%, ALLM4ADD 44.80%; dataset HF chlo1/ML-ITW — [arXiv 2603.05852](https://arxiv.org/html/2603.05852)
- MLAAD: 140 TTS models, 51 languages (v9); DeepFense evaluated 23 MLAAD languages incl. Indo-Aryan, Wav2Vec2 variants most variable per language (9.7–12.0% spread) — [MLAAD arXiv 2401.09512](https://arxiv.org/html/2401.09512v9), [DeepFense](https://arxiv.org/html/2604.08450)
- SpeechFake (2025): models trained on English+Chinese only show a "noticeable performance drop … particularly for French and Hindi"; W2V+AASIST generalizes better "attributed to multilingual pretraining of wav2vec2 XLSR" — [arXiv 2507.21463](https://arxiv.org/pdf/2507.21463)
- Models trained with Hindi-containing MLAAD: AntiDeepfake (MLAAD 378 h, 38 langs) — [HF](https://huggingface.co/nii-yamagishilab/wav2vec-large-anti-deepfake-nda); DF_Arena — [HF](https://huggingface.co/Speech-Arena-2025/DF_Arena_1B_V_1); ISSF WavLM+AASIST — [arXiv 2508.20983](https://arxiv.org/html/2508.20983v1)
- IJERT 2025 LSTM/log-mel detector for Hindi/Marathi/Punjabi/Bengali (Flask app; low-rigor venue, no cross-dataset numbers) — [IJERT](https://www.ijert.org/deepfake-audio-detection-for-indian-language)

### Inferences
- Use IndicSynth (real+fake, 12 Indic languages) as the local fine-tuning/validation set; it is the only large, licensed-for-download Indic corpus with synthetic pairs. Pass it through AMR-NB/EVS simulation to build the telephony dev set.
- SATYAM's numbers are not actionable on 8 GB (frozen Qwen2-7B), but its AASIST baselines quantify the cross-lingual penalty (~+15–25 pts) you should expect from English-trained spectral models.

### Gaps
- No published Hindi EER for XLSR-SLS, Nes2Net, AntiDeepfake or DF_Arena.
- IndicSynth license terms and HAV-DF audio-only detector results not retrieved.
- Indic-CodecFake license not stated in the paper.

---

## KQ5. Inference cost on M1 / CPU, memory, ONNX/CoreML

### Takeaway
All competitive models are ~320 M params (~1.2 GB fp32 weights; comfortably inside 8 GB); the one CPU measurement found says a full XLS-R-300M forward on a 5 s clip takes ~9 s on a single CPU core (RTF ≈ 1.8), so multi-core/MPS and/or layer truncation is needed for real-time 2–4 s windows. No official ONNX or CoreML exports exist for any ranked model.

### Cited Findings
- Edge/browser-plugin study (Jun 2026): Wav2Vec2-300m detector, 5 s clips at 16 kHz on one CPU core; inference time rises ~linearly with transformer layers, ~2 s (early layers) to ~9 s (full model); authors conclude the full model "cannot be used for real-time processing on the single CPU core" and propose layer truncation — [arXiv 2606.30780](https://arxiv.org/pdf/2606.30780) (numbers from search snippet; PDF body not parseable)
- pellav2: 57 ms per 4 s crop on T4 GPU, batch 1 — [HF](https://huggingface.co/Sadanie/pellav2-audio-deepfake-detector)
- Podonos latency (vendor APIs incl. network): pellav2 57 ms RTF 0.021, Pindrop 282 ms RTF 0.076, Resemble DETECT-World 399 ms RTF 0.12 — [Podonos](https://www.podonos.com/blog/audio-deepfake-detection-benchmark)
- Parameter counts: XLSR+SLS 340 M, TCM 319 M, Nes2NetX 317.9 M, Wav2Vec2-AASIST 317.84 M, XLSR-Mamba 319 M, WavLM-ECAPA 102 M, RawNet2 17.6 M, Whisper-MesoNet 7.6 M, AASIST 0.3 M, RawGAT-ST 0.44 M — [arXiv 2509.02859](https://arxiv.org/html/2509.02859); back-end only: Nes2Net-X 511 k, AASIST 447 k, Mamba 1.94 M, SLS 23.4 M — [GitHub](https://github.com/Liu-Tianchi/Nes2Net_ASVspoof_ITW)
- Compact alternatives: AntiDeepfake W2V-Small 95 M (ITW 4.24) — [HF](https://huggingface.co/nii-yamagishilab/wav2vec-small-anti-deepfake); DF_Arena_100M (ITW 2.21) — [arXiv 2603.06164](https://arxiv.org/html/2603.06164); Om-Parab DistilHuBERT 23.7 M (no metrics) — [HF](https://huggingface.co/Om-Parab/distilhubert-finetuned-audio-deepfake-in-the-wild)
- Input length: open-source detectors "accept only about four seconds of input"; Deepfake-Eval-2024 evaluated on 4 s segments — [arXiv 2503.02857](https://arxiv.org/pdf/2503.02857); AntiDeepfake accepts arbitrary length, DF-Eval-2024 EER improves 4 s → 30 s (20.15 → 10.73 after fine-tune) — [HF](https://huggingface.co/nii-yamagishilab/wav2vec-large-anti-deepfake-nda); ISSF found 12 s windows beat 4 s on processed audio — [arXiv 2508.20983](https://arxiv.org/html/2508.20983v1)
- Fake-Mamba speed comparison is RTF on GPU ("GPU Inference" index term) — [arXiv 2508.09294](https://arxiv.org/pdf/2508.09294)
- Runtime dependencies: AntiDeepfake needs fairseq 0.12.2 + Python 3.9 — [HF](https://huggingface.co/nii-yamagishilab/wav2vec-small-anti-deepfake); SLS needs Python 3.7 / torch 1.12.1 / bundled fairseq — [GitHub](https://github.com/QiShanZhang/SLSforASVspoof-2021-DF); Nes2Net needs fairseq commit a54021305d — [GitHub](https://github.com/Liu-Tianchi/Nes2Net_ASVspoof_ITW); DF_Arena loads via `transformers.pipeline("antispoofing", trust_remote_code=True)` — [HF](https://huggingface.co/Speech-Arena-2025/DF_Arena_1B_V_1); torchaudio ships `wav2vec2_xlsr_300m` natively — [torchaudio docs](https://docs.pytorch.org/audio/2.7.0/generated/torchaudio.models.wav2vec2_xlsr_300m.html)
- Gustking XLS-R model has "1 quantized version" on HF (unverified quality) — [HF](https://huggingface.co/Gustking/wav2vec2-large-xlsr-deepfake-audio-classification)

### Inferences
- Memory budget on 8 GB M1: 320 M fp32 ≈ 1.3 GB + activations for 4 s ≈ fine; two 320 M models in parallel ≈ 3 GB, fine; DF_Arena_1B fp32 ≈ 4 GB + macOS overhead = risky; 2 B models are out. fp16 on MPS halves this.
- Expect RTF ≈ 0.3–0.6 for a 320 M model on M1 using all performance cores or MPS (extrapolating from ~1.8 on one core); a 4 s hop with 2 s overlap is realistic. If not, truncate XLS-R to the first ~8–12 layers (SLS/weighted-sum heads already show mid layers carry most spoof signal) or use the 95 M variants.
- ONNX export of the HF `Wav2Vec2ForSequenceClassification`-style models (DF_Arena, pellav2) via `optimum` is standard; fairseq-based repos need the front-end re-mapped to HF weights first.

### Gaps
- No published M1/MPS or multi-core CPU latency for any ranked model; must be measured locally.
- No official ONNX/CoreML exports found for any model in this list.
- Browser-plugin paper hardware details and truncation-vs-EER table not extracted (PDF unreadable via fetch).

---

## KQ6. Reliability of the four named HF models + Resemble / Pindrop / Reality Defender / AASIST-SSL / SLS / XLSR-Mamba / Nes2Net / SafeEar / RawBMamba / SpeechBrain-WeSpeaker / NVIDIA-Microsoft / 2026 releases

### Takeaway
The four community HF models are undocumented fine-tunes with no cross-dataset evidence; the one that was independently tested (MelodyMachine V2) missed 90.9% of modern fakes. Resemble, Pindrop and Reality Defender are API-only. AASIST-SSL, SLS, XLSR-Mamba and Nes2Net are the credible open options (covered in KQ0); SafeEar/RawBMamba have papers but no verified usable checkpoints; no SpeechBrain/WeSpeaker anti-spoof recipe or NVIDIA/Microsoft open detector was found.

### Cited Findings
- **Gustking/wav2vec2-large-xlsr-deepfake-audio-classification**: base facebook/wav2vec2-xls-r-300m via an intermediate gender-recognition fine-tune; ~0.3 B params; Apache-2.0; training data and hyperparameters not specified; self-reported F1 0.95 (unknown set) and ASVspoof2019 eval acc 0.9286 / precision 0.9999 / recall 0.9205 / EER 0.0401; ~10.6 k downloads/month — [HF](https://huggingface.co/Gustking/wav2vec2-large-xlsr-deepfake-audio-classification)
- **MelodyMachine/Deepfake-audio-detection-V2**: wav2vec2-base lineage (facebook/wav2vec2-base → mo-thecreator/wav2vec2-base-finetuned → mo-thecreator/Deepfake-audio-detection), 94.6 M, Apache-2.0; dataset only "audiofolder"; acc 0.9973 on undocumented eval; train loss 0.0003 vs val loss 0.0174 (overfit signal); ~6.2 k downloads/month — [HF](https://huggingface.co/MelodyMachine/Deepfake-audio-detection-V2). Independent Podonos test: 53.03% acc, F1 0.162, "misses 90.9% of fakes" — [Podonos](https://www.podonos.com/blog/audio-deepfake-detection-benchmark)
- **mo-thecreator/Deepfake-audio-detection**: same lineage, 94.6 M, Apache-2.0; dataset "None"; acc 0.9882, val loss rising after epoch 2; ~17.3 k downloads/month — [HF](https://huggingface.co/mo-thecreator/Deepfake-audio-detection)
- **Om-Parab/distilhubert-finetuned-audio-deepfake-in-the-wild**: HuBERT-arch, 23.7 M params; auto-generated card; no base model, dataset, metrics, sample rate or license listed; 407 downloads/month — [HF](https://huggingface.co/Om-Parab/distilhubert-finetuned-audio-deepfake-in-the-wild)
- Other Podonos open baselines on modern-TTS test: Wav2Vec2 (2019 LA) 62.89% acc (best), AST (ASVspoof5) 56.83%, RawNet2 50.66%, AASIST 48.17%, AASIST3 (CC BY-NC-4.0) 47.63% "misses 98.4% of fakes" — [Podonos](https://www.podonos.com/blog/audio-deepfake-detection-benchmark)
- **Resemble AI**: proprietary (DETECT-World, DETECT-3B Omni, Detect-2B); Speech DF Arena lists "Resemble AI" 2,112 M params, avg EER 10.69%, ITW 3.94, CodecFake 33.04, ADD23-R1 21.07 — [arXiv 2509.02859](https://arxiv.org/html/2509.02859); Podonos DETECT-World 99.47% acc, 399 ms — [Podonos](https://www.podonos.com/blog/audio-deepfake-detection-benchmark); only open repo is Resemblyzer (a speaker encoder, not a detector) — [Resemble page](https://www.resemble.ai/introducing-telephony-optimized-deepfake-detection-model)
- **Pindrop**: no open model found; Podonos 95.05% acc, 282 ms — [Podonos](https://www.podonos.com/blog/audio-deepfake-detection-benchmark); [search](https://voxbooster.com/de/blog/voice-cloning-deepfake-detection/)
- **Reality Defender**: proprietary spectrogram CNN; open-source client SDKs only; free tier 50 scans/month; Podonos 71.27% acc, FPR 53.7%, 5.7 s latency — [RD blog](https://www.realitydefender.com/blog/enhanced-detection-of-deepfakes), [Podonos](https://www.podonos.com/blog/audio-deepfake-detection-benchmark)
- **AASIST-SSL (SSL_Anti-spoofing)**, **SLS**, **XLSR-Mamba**, **Nes2Net**: see KQ0 items 2, 3, 6, 7 — [GitHub](https://github.com/TakHemlata/SSL_Anti-spoofing), [GitHub](https://github.com/QiShanZhang/SLSforASVspoof-2021-DF), [GitHub](https://github.com/swagshaw/XLSR-Mamba), [GitHub](https://github.com/Liu-Tianchi/Nes2Net_ASVspoof_ITW)
- Nes2Net variant with checkpoint: XLSR-Nes2Net-LA in MultiAPI-Spoof repo — [GitHub](https://github.com/XuepingZhang/MultiAPI-Spoof); Nes2Net CtrSVDD repo mentions HF `nielsr/nes2net-checkpoints` (Mar 2026, unverified) — [GitHub](https://github.com/Liu-Tianchi/Nes2Net)
- **SafeEar**: CCS 2024, repo github.com/LetterLiGo/SafeEar, avg EER 2.02% on four benchmarks, codec augmentation — [arXiv 2409.09272](https://arxiv.org/html/2409.09272v1) (weights/license not verified)
- **RawBMamba**: paper only, no repo or weights located — [arXiv 2406.06086](https://arxiv.org/pdf/2406.06086)
- **SpeechBrain / WeSpeaker**: no anti-spoofing recipe or pretrained CM surfaced in search — [search](https://arxiv.org/abs/2204.01387v2)
- **NVIDIA / Microsoft**: only mention is "NVIDIA Audio Watermarker" (watermarking, not detection) in a tool list — [voxbooster](https://voxbooster.com/de/blog/voice-cloning-deepfake-detection/); no open detector release found
- **2026 releases**: DeepFense (Apache 2.0, Apr 2026) — [arXiv 2604.08450](https://arxiv.org/html/2604.08450); DF_Arena_500M/1B (Mar–Apr 2026) — [HF org](https://huggingface.co/Speech-Arena-2025/models); XLSR-MamBo (Jan 2026) — [arXiv 2601.02944](https://arxiv.org/html/2601.02944v1) (not fetched); RAPTOR (Mar 2026) — [arXiv 2603.06164](https://arxiv.org/html/2603.06164); "Neural Encoding Detection is Not All You Need" (Apr 2026) — [arXiv 2604.16700](https://arxiv.org/pdf/2604.16700) (not fetched); community XLS-R cards eliya/forensics_0.3B_base_deepfake_classifier, RuiRuihigh/hyperion-* (no license/metrics verified) — [search](https://huggingface.co/eliya/forensics_0.3B_base_deepfake_classifier)

### Inferences
- The Gustking model's ASVspoof2019 EER 4.0% is in-domain-only and ~20x worse than SOTA on the same set (XLSR+SLS 0.23%); treat it as a demo, not a detector. The wav2vec2-base family (MelodyMachine, mo-thecreator) is demonstrably broken on 2025-era TTS.
- Commercial APIs are not an option under the offline constraint, but the Resemble/Whispeak numbers set the ceiling to aim for (ITW ~1–4%).

### Gaps
- XLSR-MamBo and the Apr-2026 "neural encoding detection" paper not read; may contain newer open checkpoints.
- SafeEar and MultiAPI-Spoof checkpoint availability/licensing not verified.
- The Speech DF Arena / SpeechAntiSpoofingArena live tables (which may list newer 2026 entries) could not be scraped.
