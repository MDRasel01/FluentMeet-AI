# Step 07 — Speech-to-Text Pipeline (faster-whisper)

## 1. Engine Architecture
The primary ASR engine is `faster-whisper`, a reimplementation of OpenAI's Whisper model utilizing CTranslate2. CTranslate2 delivers up to 4x faster execution and 50% less memory consumption than standard PyTorch Whisper models through 8-bit quantization (`int8`) and fused matrix multiplications.

## 2. Model Profiles & Hardware Fallbacks

| Profile | Model Tag | Parameters | Execution Device | Compute Type | RTF (Real-Time Factor) | Memory Footprint |
|---|---|---|---|---|---|---|
| **Production Primary** | `large-v3` | 1550M | CUDA (NVIDIA GPU) | `float16` | 0.08x | ~4.5 GB VRAM |
| **High-Throughput** | `distil-large-v3` | 756M | CUDA / CPU | `int8` | 0.04x | ~2.1 GB RAM |
| **CPU Server Baseline** | `base.en` | 74M | CPU (AVX-512) | `int8` | 0.12x | ~350 MB RAM |
| **Local Dev / Testing** | `tiny.en` | 39M | CPU | `int8` | 0.05x | ~180 MB RAM |

## 3. Word-Level Timestamp Extraction
- `word_timestamps=True` is enabled on `WhisperModel.transcribe`.
- CTranslate2 uses dynamic time warping (DTW) on cross-attention weights to pinpoint the start and end of every word token.
- Offsets are converted to absolute meeting timestamps:
  $$\text{Timestamp}_{\text{abs}} = \text{Segment}_{\text{start\_ms}} + \text{Word}_{\text{relative\_ms}}$$

## 4. Confidence Score Calibration
Raw Whisper outputs log-probabilities per token. FluentMeet converts these into normalized confidence scores $[0.0, 1.0]$:
$$\text{Confidence} = \min\left(1.0, \max\left(0.0, e^{\text{avg\_logprob}}\right)\right)$$
If confidence is uncalibrated or absent, the system strictly stores `null` to avoid hallucinating artificial certainty. Words with $\text{Confidence} < 0.65$ are visually highlighted in the UI with warning indicators for coaching review.
