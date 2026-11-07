"""
FluentMeet AI - Step 06 Test Suite: Bit-Exact Audio Data Integrity Verification
Specification: Step 06 - Section 21.1 (Acceptance Gate: Bit-exact PCM Reconstruction)
"""

import pytest
import numpy as np
from unittest.mock import AsyncMock
from app.audio.protocol import BinaryAudioProtocol, AudioPacket
from app.audio.service import AudioIngestionService
from app.audio.storage.object_storage import AudioObjectStorage

def generate_reference_signal(freq: float, duration_seconds: float = 3.0, sample_rate: int = 16000) -> bytes:
    total_samples = int(sample_rate * duration_seconds)
    t = np.linspace(0, duration_seconds, total_samples, endpoint=False)
    # Generate 16-bit integer PCM
    samples = (np.sin(2 * np.pi * freq * t) * 15000).astype(np.int16)
    return samples.tobytes()

class TestAudioDataIntegrity:
    @pytest.mark.asyncio
    async def test_bit_exact_dual_channel_reconstruction(self, tmp_path):
        """
        Ingests 3 seconds of Source 0 (440 Hz) and Source 1 (880 Hz) in 100ms chunks.
        Reassembles all persisted segments and verifies bit-for-bit identity against reference signal.
        """
        temp_storage = AudioObjectStorage(base_dir=str(tmp_path))
        service = AudioIngestionService(storage=temp_storage)
        meeting_id = "integrity-test-meet-1"
        org_id = "org-integrity"

        # Generate reference signals
        ref_s0_bytes = generate_reference_signal(freq=440.0, duration_seconds=3.0)
        ref_s1_bytes = generate_reference_signal(freq=880.0, duration_seconds=3.0)

        chunk_ms = 100
        chunk_samples = int(16000 * (chunk_ms / 1000.0))
        chunk_bytes_len = chunk_samples * 2
        total_chunks = len(ref_s0_bytes) // chunk_bytes_len

        db_mock = AsyncMock()

        # Ingest interleaved chunks from Source 0 and Source 1
        s0_persisted_keys = []
        s1_persisted_keys = []

        for i in range(total_chunks):
            seq = i + 1
            ts_ms = i * float(chunk_ms)

            # --- Source 0 Chunk ---
            s0_pcm_chunk = ref_s0_bytes[i * chunk_bytes_len : (i + 1) * chunk_bytes_len]
            p0 = AudioPacket(
                version=1,
                source_id=0,
                sequence_number=seq,
                session_relative_timestamp_ms=ts_ms,
                sample_rate=16000,
                channels=1,
                encoding=1,
                sample_count=chunk_samples,
                meeting_id=meeting_id,
                pcm_payload=s0_pcm_chunk,
            )
            raw0 = BinaryAudioProtocol.encode(p0)
            _, l2_ack0 = await service.ingest_binary_packet(raw0, meeting_id, org_id, db_mock)
            if l2_ack0:
                s0_persisted_keys.append(l2_ack0["storageKey"])

            # --- Source 1 Chunk ---
            s1_pcm_chunk = ref_s1_bytes[i * chunk_bytes_len : (i + 1) * chunk_bytes_len]
            p1 = AudioPacket(
                version=1,
                source_id=1,
                sequence_number=seq,
                session_relative_timestamp_ms=ts_ms,
                sample_rate=16000,
                channels=1,
                encoding=1,
                sample_count=chunk_samples,
                meeting_id=meeting_id,
                pcm_payload=s1_pcm_chunk,
            )
            raw1 = BinaryAudioProtocol.encode(p1)
            _, l2_ack1 = await service.ingest_binary_packet(raw1, meeting_id, org_id, db_mock)
            if l2_ack1:
                s1_persisted_keys.append(l2_ack1["storageKey"])

        # Flush any remaining audio in buffers
        flushed_acks = await service.flush_remaining_audio(meeting_id, org_id, db_mock)
        for ack in flushed_acks:
            if ack["sourceId"] == 0:
                s0_persisted_keys.append(ack["storageKey"])
            elif ack["sourceId"] == 1:
                s1_persisted_keys.append(ack["storageKey"])

        # Reconstruct Source 0 audio from persisted segments in storage
        reconstructed_s0 = b""
        for key in s0_persisted_keys:
            reconstructed_s0 += temp_storage.get_object(key)

        # Reconstruct Source 1 audio from persisted segments in storage
        reconstructed_s1 = b""
        for key in s1_persisted_keys:
            reconstructed_s1 += temp_storage.get_object(key)

        # Acceptance Criteria 1: Zero Sample Loss (exact byte count)
        assert len(reconstructed_s0) == len(ref_s0_bytes), "Source 0 byte count mismatch!"
        assert len(reconstructed_s1) == len(ref_s1_bytes), "Source 1 byte count mismatch!"

        # Acceptance Criteria 2: Bit-for-bit exact PCM match
        assert reconstructed_s0 == ref_s0_bytes, "Source 0 reconstructed PCM differs from reference!"
        assert reconstructed_s1 == ref_s1_bytes, "Source 1 reconstructed PCM differs from reference!"

        # Acceptance Criteria 3: Zero Cross-Channel Bleed / Source Separation
        # S0 (440Hz) and S1 (880Hz) must be distinctly different
        assert reconstructed_s0 != reconstructed_s1
