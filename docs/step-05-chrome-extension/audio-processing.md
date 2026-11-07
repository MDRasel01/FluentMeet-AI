# Audio Processing, Resampling & Format Normalization
## Specification: Step 05 — Section 9.4 & Section 9.5

---

## 1. Processing Pipeline Stages

Audio frames flow from Web Audio nodes into an AudioWorklet running on a high-priority real-time audio thread:

```mermaid
flowchart TD
    Frames["Web Audio Input Frames\n(128 samples per render quantum @ 44.1kHz or 48kHz)"]
    Downmix["Mono Downmix\n(Average across input channels)"]
    Buffer["AudioWorklet Frame Accumulator\n(2048 sample blocks)"]
    Emit["Worklet Port PostMessage\n(Float32Array buffer transfer)"]
    Resample["Linear Interpolation Resampler\n(Normalized to 16,000 Hz)"]
    Convert["PCM S16LE Converter\n(Float32 [-1.0, 1.0] -> Int16 [-32768, 32767])"]
    Metrics["Signal Health Evaluator\n(RMS, Peak %, Clipping, Silence)"]
    Encode["Binary Frame Serialization\n(Header + S16LE payload)"]

    Frames --> Downmix --> Buffer --> Emit --> Resample --> Convert --> Metrics --> Encode
```

---

## 2. Mathematical Resampling Algorithm

Because modern audio interfaces operate at 48,000 Hz or 44,100 Hz, while downstream speech models require standardized **16,000 Hz**, dynamic resampling is required.

In `audio-resampler.ts`, we implement linear interpolation downsampling:

$$ \text{ratio} = \frac{f_{\text{input}}}{f_{\text{target}}} = \frac{48000}{16000} = 3.0 $$

For output index $i$:
$$ \text{pos} = i \times \text{ratio} $$
$$ k = \lfloor \text{pos} \rfloor, \quad \alpha = \text{pos} - k $$
$$ x_{\text{out}}[i] = x_{\text{in}}[k] + \alpha \cdot (x_{\text{in}}[k+1] - x_{\text{in}}[k]) $$

This runs in $O(N)$ with zero allocation in the hot loop, consuming $< 1.5\%$ CPU on standard client machines.

---

## 3. Float32 to Signed 16-Bit PCM (S16LE) Conversion

Audio samples in Web Audio are Float32 values constrained to $[-1.0, +1.0]$. In `audio-resampler.ts`:
```typescript
public static floatToPcmS16LE(floatSamples: Float32Array): Int16Array {
  const int16Array = new Int16Array(floatSamples.length);
  for (let i = 0; i < floatSamples.length; i++) {
    const s = Math.max(-1, Math.min(1, floatSamples[i]));
    int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
  }
  return int16Array;
}
```
- Minimum value: $-1.0 \times 32768 = -32768$ (`0x8000`).
- Maximum value: $+1.0 \times 32767 = +32767$ (`0x7FFF`).
- Zero value: $0.0 \to 0$.

---

## 4. Signal Health & VU Dynamics

The `calculateMetrics` method computes:
1. **RMS Volume (0–100%):**
   $$ \text{RMS} = \sqrt{\frac{1}{N} \sum_{i=1}^N x[i]^2} $$
   Scaled to perceived loudness for the Side Panel VU meters.
2. **Peak Volume (0–100%):** Highest absolute sample in the chunk.
3. **Clipping:** Flagged if $\max(|x[i]|) \ge 0.99$.
4. **Silence:** Flagged if normalized RMS $< 1\%$.

