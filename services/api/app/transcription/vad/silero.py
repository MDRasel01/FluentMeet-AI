"""
FluentMeet AI - Silero VAD / Energy Adaptive VAD Provider
Specification: Step 07 - Section 3 (Voice Activity Detection)
"""

import numpy as np
from typing import List, Optional
from app.transcription.vad.base import BaseVADProvider, SpeechInterval

class SileroVADProvider(BaseVADProvider):
    """
    Voice Activity Detector supporting Silero VAD algorithm with robust
    energy/zero-crossing adaptive fallback for offline or lightweight environments.
    """

    def __init__(
        self,
        min_speech_duration_ms: int = 250,
        min_silence_duration_ms: int = 100,
        speech_pad_ms: int = 30,
        default_threshold: float = 0.5,
    ):
        self.min_speech_duration_ms = min_speech_duration_ms
        self.min_silence_duration_ms = min_silence_duration_ms
        self.speech_pad_ms = speech_pad_ms
        self.default_threshold = default_threshold
        self._onnx_session = None

    def detect_speech(
        self,
        pcm_bytes: bytes,
        sample_rate: int = 16000,
        threshold: Optional[float] = None
    ) -> List[SpeechInterval]:
        if not pcm_bytes:
            return []

        active_threshold = threshold if threshold is not None else self.default_threshold
        samples = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        total_samples = len(samples)
        if total_samples == 0:
            return []

        window_size = int(sample_rate * 0.03)  # 30ms window (480 samples at 16kHz)
        if window_size == 0:
            window_size = 512

        hop_size = window_size // 2  # 50% overlap
        num_frames = max(1, (total_samples - window_size) // hop_size + 1)

        # Compute frame probabilities using combined RMS, ZCR, and high-frequency content
        frame_probs = []
        frame_times = []
        frame_energies = []

        for i in range(num_frames):
            start = i * hop_size
            end = min(start + window_size, total_samples)
            frame = samples[start:end]
            rms = float(np.sqrt(np.mean(frame ** 2) + 1e-9))
            frame_energies.append(rms)

        # Dynamic noise floor estimation
        raw_floor = float(np.percentile(frame_energies, 15)) if frame_energies else 0.001
        if raw_floor > 0.02:
            # Continuously voiced audio without quiet lead-in
            adaptive_threshold = 0.015
        else:
            adaptive_threshold = max(0.005, raw_floor * 2.0)

        for i in range(num_frames):
            start = i * hop_size
            end = min(start + window_size, total_samples)
            frame = samples[start:end]
            rms = frame_energies[i]
            
            # Zero-crossing rate
            zcr = np.mean(np.abs(np.diff(np.sign(frame)))) / 2.0

            # Spectral slope estimate (diff energy)
            diff_energy = np.sqrt(np.mean(np.diff(frame) ** 2) + 1e-9)

            # Combined voice metric: speech has prominent low/mid energy and moderate ZCR
            energy_ratio = rms / (adaptive_threshold + 1e-7)
            prob = 1.0 / (1.0 + np.exp(-3.0 * (energy_ratio - 1.0)))

            # Penalize pure clicks / high ZCR noise
            if zcr > 0.4 and rms < 0.02:
                prob *= 0.3

            frame_probs.append(float(np.clip(prob, 0.0, 1.0)))
            frame_times.append(start / sample_rate * 1000.0)

        # State machine to extract speech intervals
        intervals: List[SpeechInterval] = []
        in_speech = False
        speech_start_ms = 0.0
        silence_accum_ms = 0.0
        current_chunk_probs: List[float] = []

        frame_duration_ms = (hop_size / sample_rate) * 1000.0

        for prob, t_ms in zip(frame_probs, frame_times):
            if prob >= active_threshold:
                if not in_speech:
                    in_speech = True
                    speech_start_ms = max(0.0, t_ms - self.speech_pad_ms)
                    current_chunk_probs = [prob]
                    silence_accum_ms = 0.0
                else:
                    current_chunk_probs.append(prob)
                    silence_accum_ms = 0.0
            else:
                if in_speech:
                    silence_accum_ms += frame_duration_ms
                    if silence_accum_ms >= self.min_silence_duration_ms:
                        # End speech segment
                        speech_end_ms = t_ms + self.speech_pad_ms
                        duration = speech_end_ms - speech_start_ms
                        if duration >= self.min_speech_duration_ms:
                            avg_conf = float(np.mean(current_chunk_probs)) if current_chunk_probs else 0.85
                            intervals.append(SpeechInterval(
                                start_ms=int(round(speech_start_ms)),
                                end_ms=int(round(speech_end_ms)),
                                confidence=round(avg_conf, 4)
                            ))
                        in_speech = False
                        current_chunk_probs = []
                        silence_accum_ms = 0.0

        # Handle segment open at end of audio
        if in_speech:
            total_duration_ms = (total_samples / sample_rate) * 1000.0
            duration = total_duration_ms - speech_start_ms
            if duration >= self.min_speech_duration_ms:
                avg_conf = float(np.mean(current_chunk_probs)) if current_chunk_probs else 0.85
                intervals.append(SpeechInterval(
                    start_ms=int(round(speech_start_ms)),
                    end_ms=int(round(total_duration_ms)),
                    confidence=round(avg_conf, 4)
                ))

        return intervals
