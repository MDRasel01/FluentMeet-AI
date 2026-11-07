"""
FluentMeet AI - Audio Timeline Synchronization & Clock Drift Engine
Specification: Step 06 - Section 11
"""

from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class SyncDiagnostics:
    clock_drift_ms: float
    is_discontinuous: bool
    cumulative_duration_ms: float
    is_drift_warning: bool = False

class AudioSynchronizer:
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        # source_id -> cumulative sample count
        self.cumulative_samples: Dict[int, int] = {}
        # source_id -> initial timestamp ms
        self.initial_timestamp_ms: Dict[int, float] = {}
        # source_id -> last timestamp ms
        self.last_timestamp_ms: Dict[int, float] = {}

    def track_chunk(
        self,
        source_id: int,
        timestamp_ms: Optional[float] = None,
        sample_count: int = 0,
        session_timestamp_ms: Optional[float] = None
    ) -> SyncDiagnostics:
        ts = timestamp_ms if timestamp_ms is not None else (session_timestamp_ms if session_timestamp_ms is not None else 0.0)
        if source_id not in self.initial_timestamp_ms:
            self.initial_timestamp_ms[source_id] = ts
            self.last_timestamp_ms[source_id] = ts
            self.cumulative_samples[source_id] = sample_count
            return SyncDiagnostics(
                clock_drift_ms=0.0,
                is_discontinuous=False,
                cumulative_duration_ms=0.0,
                is_drift_warning=False
            )

        prev_ts = self.last_timestamp_ms[source_id]
        is_discontinuous = ts < prev_ts or (ts - prev_ts) > 1000.0

        # Expected start time of this chunk based on previous cumulative samples
        prior_samples = self.cumulative_samples[source_id]
        prior_duration_ms = (prior_samples / self.sample_rate) * 1000.0

        self.last_timestamp_ms[source_id] = ts
        self.cumulative_samples[source_id] += sample_count
        total_duration_ms = (self.cumulative_samples[source_id] / self.sample_rate) * 1000.0

        elapsed_mono_ms = ts - self.initial_timestamp_ms[source_id]
        clock_drift_ms = round(abs(elapsed_mono_ms - prior_duration_ms), 2)
        is_warning = clock_drift_ms > 200.0 or is_discontinuous

        return SyncDiagnostics(
            clock_drift_ms=clock_drift_ms,
            is_discontinuous=is_discontinuous,
            cumulative_duration_ms=round(total_duration_ms, 2),
            is_drift_warning=is_warning
        )
