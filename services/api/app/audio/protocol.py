"""
FluentMeet AI - Binary Audio Protocol (Step 06 & Step 05 Parity)
Specification: Step 06 - Section 7

Framing Layout:
[00] Protocol Version (Uint8) - 1 byte
[01] Source ID (Uint8: 0=Remote Tab, 1=Local Mic) - 1 byte
[02..05] Sequence Number (Uint32 Big-Endian) - 4 bytes
[06..13] Timestamp Ms (Float64 Big-Endian) - 8 bytes
[14..15] Sample Rate (Uint16 Big-Endian) - 2 bytes
[16] Channel Count (Uint8) - 1 byte
[17] Encoding (Uint8: 1=PCM_S16LE) - 1 byte
[18..21] Sample Count (Uint32 Big-Endian) - 4 bytes
[22] Meeting ID Length N (Uint8) - 1 byte
[23..23+N-1] Meeting ID String (UTF-8 bytes) - N bytes
[23+N..End] Raw PCM S16LE Audio Bytes
"""

import struct
from dataclasses import dataclass
from typing import Tuple, Optional

PROTOCOL_VERSION = 1
ENCODING_PCM_S16LE = 1

SOURCE_REMOTE_TAB = 0
SOURCE_LOCAL_MIC = 1

HEADER_MIN_SIZE = 23

class ProtocolValidationError(Exception):
    """Raised when an incoming binary packet fails protocol framing validation."""
    pass

class AudioPacket:
    def __init__(
        self,
        source_id: int,
        sequence_number: int,
        session_relative_timestamp_ms: float,
        sample_rate: int,
        channels: int,
        encoding: int,
        sample_count: int,
        meeting_id: str,
        pcm_payload: bytes,
        protocol_version: int = PROTOCOL_VERSION,
        version: Optional[int] = None,
    ):
        self.protocol_version = version if version is not None else protocol_version
        self.source_id = source_id
        self.sequence_number = sequence_number
        self.session_relative_timestamp_ms = session_relative_timestamp_ms
        self.sample_rate = sample_rate
        self.channels = channels
        self.encoding = encoding
        self.sample_count = sample_count
        self.meeting_id = meeting_id
        self.pcm_payload = pcm_payload

    @property
    def version(self) -> int:
        return self.protocol_version

    def __repr__(self) -> str:
        return (
            f"AudioPacket(source={self.source_id}, seq={self.sequence_number}, "
            f"ts={self.session_relative_timestamp_ms}, samples={self.sample_count}, "
            f"meeting={self.meeting_id})"
        )

class BinaryAudioProtocol:
    @staticmethod
    def decode(raw_bytes: bytes) -> AudioPacket:
        if len(raw_bytes) < HEADER_MIN_SIZE:
            raise ProtocolValidationError(
                f"Binary frame too short/small: {len(raw_bytes)} bytes < minimum {HEADER_MIN_SIZE} bytes"
            )

        # Unpack header up to meeting_id length
        version, source_id, seq_num, ts_ms, sample_rate, channels, encoding, sample_count, m_len = (
            struct.unpack_from(">BBI d HBBIB", raw_bytes, 0)
        )

        if version != PROTOCOL_VERSION:
            raise ProtocolValidationError(f"Unsupported protocol version: {version}. Expected {PROTOCOL_VERSION}")

        if source_id not in (SOURCE_REMOTE_TAB, SOURCE_LOCAL_MIC):
            raise ProtocolValidationError(f"Invalid source_id: {source_id}")

        if encoding != ENCODING_PCM_S16LE:
            raise ProtocolValidationError(f"Unsupported encoding ID: {encoding}. Expected 1 (PCM S16LE)")

        header_total = HEADER_MIN_SIZE + m_len
        if len(raw_bytes) < header_total:
            raise ProtocolValidationError("Frame truncated inside meeting ID field")

        try:
            meeting_id = raw_bytes[HEADER_MIN_SIZE:header_total].decode("utf-8")
        except UnicodeDecodeError:
            raise ProtocolValidationError("Invalid UTF-8 string in meeting ID header")

        pcm_payload = raw_bytes[header_total:]

        # Validate expected payload length: sample_count * channels * 2 bytes
        expected_bytes = sample_count * channels * 2
        if len(pcm_payload) != expected_bytes:
            raise ProtocolValidationError(
                f"Payload size mismatch: expected {expected_bytes} bytes for {sample_count} samples, got {len(pcm_payload)}"
            )

        return AudioPacket(
            protocol_version=version,
            source_id=source_id,
            sequence_number=seq_num,
            session_relative_timestamp_ms=ts_ms,
            sample_rate=sample_rate,
            channels=channels,
            encoding=encoding,
            sample_count=sample_count,
            meeting_id=meeting_id,
            pcm_payload=pcm_payload,
        )

    @staticmethod
    def encode(packet: AudioPacket) -> bytes:
        m_bytes = packet.meeting_id.encode("utf-8")
        m_len = min(len(m_bytes), 255)
        m_bytes = m_bytes[:m_len]

        header = struct.pack(
            ">BBI d HBBIB",
            packet.protocol_version,
            packet.source_id,
            packet.sequence_number,
            packet.session_relative_timestamp_ms,
            packet.sample_rate,
            packet.channels,
            packet.encoding,
            packet.sample_count,
            m_len
        )
        return header + m_bytes + packet.pcm_payload
