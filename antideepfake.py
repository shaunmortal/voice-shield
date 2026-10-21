"""nii-yamagishilab/wav2vec-small-anti-deepfake without fairseq.

fairseq Wav2Vec2 base encoder -> transformers.Wav2Vec2Model (facebook/wav2vec2-base
architecture) + the original `proj_fc` head. Reproduces the README inference exactly:
    wav (mono, 16 kHz) -> layer_norm(wav, wav.shape) -> encoder last hidden state [T, 768]
    -> mean over T -> Linear(768, 2) -> softmax -> (p_fake, p_real)
"""
import os
import re

import numpy as np
import torch
from safetensors.torch import load_file, save_file
from transformers import Wav2Vec2Config, Wav2Vec2Model

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "antideepfake-small")
HF_CACHE = os.path.join(MODEL_DIR, "hf_model.safetensors")

# fairseq -> transformers key mapping (same as transformers'
# convert_wav2vec2_original_pytorch_checkpoint_to_pytorch.py MAPPING, base/group-norm variant).
_MAP = [
    (r"^feature_extractor\.conv_layers\.(\d+)\.0\.weight$", r"feature_extractor.conv_layers.\1.conv.weight"),
    (r"^feature_extractor\.conv_layers\.0\.2\.(weight|bias)$", r"feature_extractor.conv_layers.0.layer_norm.\1"),
    (r"^layer_norm\.(weight|bias)$", r"feature_projection.layer_norm.\1"),
    (r"^post_extract_proj\.(weight|bias)$", r"feature_projection.projection.\1"),
    (r"^encoder\.pos_conv\.0\.bias$", r"encoder.pos_conv_embed.conv.bias"),
    (r"^encoder\.pos_conv\.0\.weight_g$", r"encoder.pos_conv_embed.conv.parametrizations.weight.original0"),
    (r"^encoder\.pos_conv\.0\.weight_v$", r"encoder.pos_conv_embed.conv.parametrizations.weight.original1"),
    (r"^encoder\.layer_norm\.(weight|bias)$", r"encoder.layer_norm.\1"),
    (r"^encoder\.layers\.(\d+)\.self_attn\.(k|q|v|out)_proj\.(weight|bias)$", r"encoder.layers.\1.attention.\2_proj.\3"),
    (r"^encoder\.layers\.(\d+)\.self_attn_layer_norm\.(weight|bias)$", r"encoder.layers.\1.layer_norm.\2"),
    (r"^encoder\.layers\.(\d+)\.fc1\.(weight|bias)$", r"encoder.layers.\1.feed_forward.intermediate_dense.\2"),
    (r"^encoder\.layers\.(\d+)\.fc2\.(weight|bias)$", r"encoder.layers.\1.feed_forward.output_dense.\2"),
    (r"^encoder\.layers\.(\d+)\.final_layer_norm\.(weight|bias)$", r"encoder.layers.\1.final_layer_norm.\2"),
    (r"^mask_emb$", r"masked_spec_embed"),
]


def _convert(src_path, dst_path):
    out = {}
    for k, v in load_file(src_path).items():
        if k.startswith("proj_fc."):
            out[k] = v
            continue
        k = k.removeprefix("m_ssl.model.")
        if k.split(".")[0] in ("quantizer", "project_q", "final_proj"):
            continue  # pretraining-only, unused with features_only
        for pat, rep in _MAP:
            nk, n = re.subn(pat, rep, k)
            if n:
                out["encoder." + nk] = v
                break
        else:
            raise KeyError(f"unmapped fairseq key: {k}")
    save_file(out, dst_path)
    return out


class AntiDeepfake:
    def __init__(self, device="mps"):
        self.device = torch.device(device if device != "mps" or torch.backends.mps.is_available() else "cpu")
        cfg = Wav2Vec2Config.from_json_file(os.path.join(MODEL_DIR, "config.json"))
        self.encoder = Wav2Vec2Model(cfg)
        self.head = torch.nn.Linear(cfg.hidden_size, 2)
        sd = load_file(HF_CACHE) if os.path.exists(HF_CACHE) else _convert(
            os.path.join(MODEL_DIR, "model.safetensors"), HF_CACHE)
        self.encoder.load_state_dict({k[8:]: v for k, v in sd.items() if k.startswith("encoder.")}, strict=True)
        self.head.load_state_dict({k[8:]: v for k, v in sd.items() if k.startswith("proj_fc.")}, strict=True)
        self.encoder.eval().to(self.device)
        self.head.eval().to(self.device)

    @torch.inference_mode()
    def p_fake(self, audio_float32_16k_mono: np.ndarray) -> float:
        wav = torch.as_tensor(np.asarray(audio_float32_16k_mono, dtype=np.float32)).reshape(-1)
        wav = torch.nn.functional.layer_norm(wav, wav.shape)  # README: whole-clip zero-mean/unit-var
        wav = wav.unsqueeze(0).to(self.device)
        emb = self.encoder(wav).last_hidden_state  # [1, T, 768]
        logits = self.head(emb.mean(dim=1))  # AdaptiveAvgPool1d(1) == mean over T
        return torch.softmax(logits, dim=1)[0, 0].item()  # index 0 = Fake


if __name__ == "__main__":
    import sys
    import time

    import soundfile as sf

    m = AntiDeepfake()
    for path in sys.argv[1:]:
        x, sr = sf.read(path, dtype="float32", always_2d=True)
        assert sr == 16000, f"{path}: need 16 kHz, got {sr}"
        print(f"{os.path.basename(path)}: p_fake={m.p_fake(x.mean(axis=1)):.4f}")
    # latency, 4 s window
    x = np.random.randn(64000).astype(np.float32)
    for dev in ("mps", "cpu"):
        mm = m if dev == str(m.device) else AntiDeepfake(dev)
        mm.p_fake(x)  # warm-up
        t = time.perf_counter()
        for _ in range(3):
            mm.p_fake(x)
        print(f"{mm.device}: {(time.perf_counter() - t) / 3 * 1000:.0f} ms per 4 s window")
