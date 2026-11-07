"""
FluentMeet AI - Step 06 Test Suite: Binary Audio Protocol
Specification: Step 06 - Section 7, 8 & 21 (REQ-ING-004, REQ-ING-005)
"""

import pytest
import struct
import numpy as np
from app.audio.protocol import BinaryAudioProtocol, AudioPacket, ProtocolValidationError

def create_synthetic_pcm(duration_ms: int = 100, sample_rate: int = 16000) -> bytes:
    sample_count = int(sample_rate * (duration_ms / 1000.0))
    # Generate 440 Hz tone
    t = np.linspace(0, duration_ms / 1000.0, sample_count, endpoint=False)
    waveform = (np.sin(2 * np.pi * 440 * t) * 16384).astype(np.int16)
    return waveform.tobytes()

class TestBinaryAudioProtocol:
    def test_encode_and_decode_parity(self):
        pcm = create_synthetic_pcm(100)
        sample_count = len(pcm) // 2
        meeting_id = "test-meeting-uuid-1234"

        packet = AudioPacket(
            version=1,
            source_id=0,
            sequence_number=101,
            session_relative_timestamp_ms=1500.5,
            sample_rate=16000,
            channels=1,
            encoding=1,
            sample_count=sample_count,
            meeting_id=meeting_id,
            pcm_payload=pcm,
        )

        encoded = BinaryAudioProtocol.encode(packet)
        assert len(encoded) == 23 + len(meeting_id.encode("utf-8")) + len(pcm)

        decoded = BinaryAudioProtocol.decode(encoded)
        assert decoded.version == 1
        assert decoded.source_id == 0
        assert decoded.sequence_number == 101
        assert abs(decoded.session_relative_timestamp_ms - 1500.5) < 1e-4
        assert decoded.sample_rate == 16000
        assert decoded.channels == 1
        assert decoded.encoding == 1
        assert decoded.sample_count == sample_count
        assert decoded.meeting_id == meeting_id
        assert decoded.pcm_payload == pcm

    def test_source_id_remote_and_mic(self):
        pcm = create_synthetic_pcm(50)
        for source_id in [0, 1]:
            packet = AudioPacket(
                version=1,
                source_id=source_id,
                sequence_number=1,
                session_relative_timestamp_ms=0.0,
                sample_rate=16000,
                channels=1,
                encoding=1,
                sample_count=len(pcm) // 2,
                meeting_id="meet-1",
                pcm_payload=pcm,
            )
            encoded = BinaryAudioProtocol.encode(packet)
            decoded = BinaryAudioProtocol.decode(encoded)
            assert decoded.source_id == source_id

    def test_reject_packet_too_short(self):
        with pytest.raises(ProtocolValidationError) as exc:
            BinaryAudioProtocol.decode(b"short_bytes_12345")
        assert "too short" in str(exc.value)

    def test_reject_invalid_source_id(self):
        pcm = create_synthetic_pcm(50)
        # Construct header with source_id = 99
        header = struct.pack(">BBI d HBBIB", 1, 99, 1, 0.0, 16000, 1, 1, len(pcm)//2, 4)
        raw = header + b"meet" + pcm
        with pytest.raises(ProtocolValidationError) as exc:
            BinaryAudioProtocol.decode(raw)
        assert "Invalid source_id" in str(exc.value)

    def test_reject_unsupported_version(self):
        pcm = create_synthetic_pcm(50)
        header = struct.pack(">BBI d HBBIB", 9, 0, 1, 0.0, 16000, 1, 1, len(pcm)//2, 4)
        raw = header + b"meet" + pcm
        with pytest.raises(ProtocolValidationError) as exc:
            BinaryAudioProtocol.decode(raw)
        assert "Unsupported protocol version" in str(exc.value)

    def test_reject_payload_size_mismatch(self):
        pcm = create_synthetic_pcm(50)
        # Claim 1000 samples but only send 50 samples of PCM
        header = struct.pack(">BBI d HBBIB", 1, 0, 1, 0.0, 16000, 1, 1, 1000, 4)
        raw = header + b"meet" + pcm
        with pytest.raises(ProtocolValidationError) as exc:
            BinaryAudioProtocol.decode(raw)
        assert "Payload size mismatch" in str(exc.value)
