"""
FluentMeet AI - Pyannote Speaker Diarization Provider
Specification: Step 07 - Section 5 (Speaker Diarization Pipeline)
"""

import logging
from typing import Optional, List, Dict, Any
import numpy as np
from app.transcription.diarization.base import (
    BaseDiarizationProvider,
    DiarizationResult,
    DiarizationSegment,
    OverlapInterval
)

logger = logging.getLogger("transcription.diarization")

class PyannoteDiarizationProvider(BaseDiarizationProvider):
    def __init__(
        self,
        hf_token: Optional[str] = None,
        pipeline_instance: Optional[Any] = None,
        min_turn_duration_ms: int = 250
    ):
        self.hf_token = hf_token
        self._pipeline = pipeline_instance
        self.min_turn_duration_ms = min_turn_duration_ms

    def _get_pipeline(self):
        if self._pipeline is None and self.hf_token:
            try:
                from pyannote.audio import Pipeline
                self._pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1",
                    use_auth_token=self.hf_token
                )
            except Exception as e:
                logger.warning(f"Could not load HuggingFace pyannote pipeline: {e}. Falling back to acoustic clustering.")
        return self._pipeline

    def diarize(
        self,
        pcm_bytes: bytes,
        sample_rate: int = 16000,
        num_speakers: Optional[int] = None,
        source_id: int = 1
    ) -> DiarizationResult:
        if not pcm_bytes:
            return DiarizationResult()

        samples = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        total_samples = len(samples)
        total_duration_ms = int(round((total_samples / sample_rate) * 1000.0))

        # Check for absolute silence (RMS < 0.005)
        rms = float(np.sqrt(np.mean(samples ** 2) + 1e-9))
        if rms < 0.005:
            return DiarizationResult()

        # REQ: Source 0 is ALWAYS the local user (deterministic attribution)
        if source_id == 0:
            return DiarizationResult(
                turns=[
                    DiarizationSegment(
                        speaker_label="speaker_user_me",
                        start_ms=0,
                        end_ms=total_duration_ms,
                        confidence=0.98
                    )
                ],
                overlaps=[]
            )

        # Source 1: Check if official pyannote pipeline is available
        pipeline = self._get_pipeline()
        if pipeline is not None:
            try:
                import torch
                waveform = torch.from_numpy(samples).unsqueeze(0)  # (1, num_samples)
                diarization = pipeline({"waveform": waveform, "sample_rate": sample_rate})
                turns: List[DiarizationSegment] = []
                for turn, _, speaker in diarization.itertracks(yield_label=True):
                    turns.append(DiarizationSegment(
                        speaker_label=f"speaker_{speaker.lower()}",
                        start_ms=int(round(turn.start * 1000.0)),
                        end_ms=int(round(turn.end * 1000.0)),
                        confidence=0.92
                    ))
                return DiarizationResult(turns=turns, overlaps=[])
            except Exception as e:
                logger.warning(f"Pyannote inference error: {e}. Falling back to acoustic clustering.")

        # Robust Acoustic Clustering Fallback (Energy & Spectral Dynamics)
        return self._cluster_acoustic_features(samples, sample_rate, num_speakers)

    def _cluster_acoustic_features(
        self,
        samples: np.ndarray,
        sample_rate: int,
        num_speakers: Optional[int] = None
    ) -> DiarizationResult:
        total_samples = len(samples)
        window_ms = 400  # 400ms analysis windows
        window_samples = int(sample_rate * (window_ms / 1000.0))
        hop_samples = window_samples // 2

        if total_samples < window_samples:
            return DiarizationResult(
                turns=[DiarizationSegment("speaker_001", 0, int((total_samples / sample_rate) * 1000), 0.90)],
                overlaps=[]
            )

        num_windows = max(1, (total_samples - window_samples) // hop_samples + 1)
        features = []
        valid_indices = []

        for w_idx in range(num_windows):
            s_start = w_idx * hop_samples
            s_end = s_start + window_samples
            chunk = samples[s_start:s_end]

            chunk_rms = float(np.sqrt(np.mean(chunk ** 2) + 1e-9))
            if chunk_rms < 0.008:
                continue  # Skip silent window

            # Feature extraction: RMS, Zero Crossing Rate, Spectral Centroid, Band Energy
            zcr = float(np.mean(np.abs(np.diff(np.sign(chunk)))) / 2.0)
            fft_mag = np.abs(np.fft.rfft(chunk))
            freqs = np.fft.rfftfreq(len(chunk), 1.0 / sample_rate)
            spectral_centroid = float(np.sum(freqs * fft_mag) / (np.sum(fft_mag) + 1e-9))

            # Spectral rolloff (85% energy point)
            cum_energy = np.cumsum(fft_mag)
            rolloff_idx = np.where(cum_energy >= 0.85 * cum_energy[-1])[0]
            spectral_rolloff = float(freqs[rolloff_idx[0]]) if len(rolloff_idx) > 0 else 4000.0

            features.append([chunk_rms, zcr, spectral_centroid / 4000.0, spectral_rolloff / 8000.0])
            valid_indices.append(w_idx)

        if not features:
            return DiarizationResult()

        X = np.array(features)
        k = num_speakers if num_speakers and num_speakers > 1 else 2
        k = min(k, len(X))

        # K-Means clustering across acoustic features
        labels = self._simple_kmeans(X, k=k)

        # Build contiguous turns
        turns: List[DiarizationSegment] = []
        current_speaker = None
        turn_start_ms = 0
        turn_end_ms = 0

        for idx, cluster_id in zip(valid_indices, labels):
            speaker_label = f"speaker_{cluster_id + 1:03d}"
            w_start_ms = int(round((idx * hop_samples / sample_rate) * 1000.0))
            w_end_ms = int(round(((idx * hop_samples + window_samples) / sample_rate) * 1000.0))

            if current_speaker is None:
                current_speaker = speaker_label
                turn_start_ms = w_start_ms
                turn_end_ms = w_end_ms
            elif current_speaker == speaker_label:
                turn_end_ms = w_end_ms
            else:
                if (turn_end_ms - turn_start_ms) >= self.min_turn_duration_ms:
                    turns.append(DiarizationSegment(
                        speaker_label=current_speaker,
                        start_ms=turn_start_ms,
                        end_ms=turn_end_ms,
                        confidence=0.88
                    ))
                current_speaker = speaker_label
                turn_start_ms = w_start_ms
                turn_end_ms = w_end_ms

        if current_speaker and (turn_end_ms - turn_start_ms) >= self.min_turn_duration_ms:
            turns.append(DiarizationSegment(
                speaker_label=current_speaker,
                start_ms=turn_start_ms,
                end_ms=turn_end_ms,
                confidence=0.88
            ))

        # Detect overlaps (e.g., overlapping contiguous turns)
        overlaps = self._detect_turn_overlaps(turns)

        return DiarizationResult(turns=turns, overlaps=overlaps)

    def _simple_kmeans(self, X: np.ndarray, k: int, max_iters: int = 20) -> np.ndarray:
        if len(X) <= k:
            return np.arange(len(X))

        # Seed centroids with extremes along 1st principal component or centroid feature
        centroids = X[np.linspace(0, len(X) - 1, k, dtype=int)]
        labels = np.zeros(len(X), dtype=int)

        for _ in range(max_iters):
            # Compute squared euclidean distances
            dists = np.sum((X[:, np.newaxis, :] - centroids[np.newaxis, :, :]) ** 2, axis=2)
            new_labels = np.argmin(dists, axis=1)

            if np.array_equal(labels, new_labels):
                break
            labels = new_labels

            # Recompute centroids
            for j in range(k):
                pts = X[labels == j]
                if len(pts) > 0:
                    centroids[j] = np.mean(pts, axis=0)

        return labels

    def _detect_turn_overlaps(self, turns: List[DiarizationSegment]) -> List[OverlapInterval]:
        overlaps: List[OverlapInterval] = []
        for i in range(len(turns)):
            for j in range(i + 1, len(turns)):
                t1 = turns[i]
                t2 = turns[j]
                if t1.speaker_label != t2.speaker_label:
                    overlap_start = max(t1.start_ms, t2.start_ms)
                    overlap_end = min(t1.end_ms, t2.end_ms)
                    if overlap_end > overlap_start:
                        overlaps.append(OverlapInterval(
                            start_ms=overlap_start,
                            end_ms=overlap_end,
                            overlapping_speakers=[t1.speaker_label, t2.speaker_label],
                            confidence=0.90
                        ))
        return overlaps
