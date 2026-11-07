/**
 * FluentMeet AI - Audio Normalization, Resampling & PCM S16LE Conversion
 * Specification: Step 05 - Section 9.4 & 9.5
 */

export class AudioResampler {
  /**
   * Downsamples or upsamples single-channel Float32Array to targetSampleRate using linear interpolation.
   */
  public static resample(
    inputData: Float32Array,
    inputSampleRate: number,
    targetSampleRate: number
  ): Float32Array {
    if (inputSampleRate === targetSampleRate) {
      return inputData;
    }

    const ratio = inputSampleRate / targetSampleRate;
    const outputLength = Math.round(inputData.length / ratio);
    const output = new Float32Array(outputLength);

    for (let i = 0; i < outputLength; i++) {
      const position = i * ratio;
      const index = Math.floor(position);
      const fraction = position - index;

      const sample1 = inputData[index] || 0;
      const sample2 = inputData[index + 1] !== undefined ? inputData[index + 1] : sample1;
      output[i] = sample1 + fraction * (sample2 - sample1);
    }

    return output;
  }

  /**
   * Converts Float32 audio samples (-1.0 to 1.0) to Int16 PCM (S16LE).
   */
  public static floatToPcmS16LE(floatSamples: Float32Array): Int16Array {
    const int16Array = new Int16Array(floatSamples.length);
    for (let i = 0; i < floatSamples.length; i++) {
      // Clamp between -1.0 and 1.0
      let s = Math.max(-1, Math.min(1, floatSamples[i]));
      int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
    }
    return int16Array;
  }

  /**
   * Computes audio signal dynamics: RMS (0-100), Peak (0-100), Clipping, Silence.
   */
  public static calculateMetrics(floatSamples: Float32Array): {
    rmsVolume: number;
    peakVolume: number;
    isClipping: boolean;
    isSilent: boolean;
  } {
    if (floatSamples.length === 0) {
      return { rmsVolume: 0, peakVolume: 0, isClipping: false, isSilent: true };
    }

    let sumSquares = 0;
    let peak = 0;
    let isClipping = false;

    for (let i = 0; i < floatSamples.length; i++) {
      const absSample = Math.abs(floatSamples[i]);
      sumSquares += absSample * absSample;
      if (absSample > peak) {
        peak = absSample;
      }
      if (absSample >= 0.99) {
        isClipping = true;
      }
    }

    const rms = Math.sqrt(sumSquares / floatSamples.length);
    const rmsVolume = Math.min(100, Math.round(rms * 100 * 2.5)); // Normalized scale
    const peakVolume = Math.min(100, Math.round(peak * 100));
    const isSilent = rmsVolume < 1;

    return { rmsVolume, peakVolume, isClipping, isSilent };
  }
}

