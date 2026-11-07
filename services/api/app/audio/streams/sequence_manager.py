"""
FluentMeet AI - Independent Sequence Number & Gap Management
Specification: Step 06 - Section 10
"""

from typing import Dict, List, Optional, Set, Tuple

class SequenceCheckResult:
    def __init__(self, is_valid: bool, is_duplicate: bool = False, gap_range: Optional[Tuple[int, int]] = None):
        self.is_valid = is_valid
        self.is_duplicate = is_duplicate
        self.gap_range = gap_range

class SequenceManager:
    def __init__(self, reorder_window_size: int = 10):
        # source_id -> expected next sequence number
        self.expected_seq: Dict[int, int] = {}
        # source_id -> set of seen sequence numbers (bounded cache)
        self.seen_seqs: Dict[int, Set[int]] = {}
        # source_id -> list of detected gap tuples (start_seq, end_seq)
        self.detected_gaps: Dict[int, List[Tuple[int, int]]] = {}
        self.reorder_window_size = reorder_window_size

    def check_sequence(self, source_id: int, sequence_number: int) -> SequenceCheckResult:
        if source_id not in self.expected_seq:
            # First packet seen for this source
            self.expected_seq[source_id] = sequence_number + 1
            self.seen_seqs[source_id] = {sequence_number}
            self.detected_gaps[source_id] = []
            return SequenceCheckResult(is_valid=True)

        seen = self.seen_seqs[source_id]
        if sequence_number in seen:
            return SequenceCheckResult(is_valid=False, is_duplicate=True)

        expected = self.expected_seq[source_id]

        if sequence_number == expected:
            # Normal sequential progression
            self.expected_seq[source_id] = sequence_number + 1
            seen.add(sequence_number)
            self._prune_seen(source_id)
            return SequenceCheckResult(is_valid=True)

        elif sequence_number > expected:
            # Sequence Gap Detected! (Missing packets between expected and sequence_number - 1)
            gap = (expected, sequence_number - 1)
            self.detected_gaps[source_id].append(gap)
            self.expected_seq[source_id] = sequence_number + 1
            seen.add(sequence_number)
            self._prune_seen(source_id)
            return SequenceCheckResult(is_valid=True, gap_range=gap)

        else:
            # Late / Out-of-order packet (sequence_number < expected, but not yet seen)
            seen.add(sequence_number)
            self._prune_seen(source_id)
            return SequenceCheckResult(is_valid=True)

    def get_gaps(self, source_id: int) -> List[Tuple[int, int]]:
        return self.detected_gaps.get(source_id, [])

    def _prune_seen(self, source_id: int) -> None:
        seen = self.seen_seqs.get(source_id, set())
        if len(seen) > 500:
            # Retain only recent 200 sequences
            sorted_seqs = sorted(seen)
            self.seen_seqs[source_id] = set(sorted_seqs[-200:])
