"""
FluentMeet AI - Step 06 Test Suite: Durable Audio Object Storage
Specification: Step 06 - Section 13, 14 & 21 (REQ-ING-012, REQ-ING-013)
"""

import pytest
import hashlib
from app.audio.storage.object_storage import AudioObjectStorage

class TestAudioStorage:
    def test_generate_storage_key_pattern(self):
        storage = AudioObjectStorage(base_dir="./test_storage_dir")
        key = storage.generate_storage_key(
            organization_id="org-acme-1",
            meeting_id="meeting-xyz-9",
            stream_id="stream-source-0",
            source_id=0,
            segment_id="seg-uuid-456"
        )
        expected = "organizations/org-acme-1/meetings/meeting-xyz-9/streams/stream-source-0/sources/0/segments/seg-uuid-456.pcm"
        assert key == expected

    def test_put_and_get_object_with_checksum(self, tmp_path):
        storage = AudioObjectStorage(base_dir=str(tmp_path))
        key = "test_org/test_meeting/sources/0/segments/seg1.pcm"
        data = b"\x01\x02\x03\x04" * 1000
        expected_checksum = hashlib.sha256(data).hexdigest()

        # Upload
        returned_checksum = storage.put_object(key, data, expected_checksum=expected_checksum)
        assert returned_checksum == expected_checksum

        # Verify exists
        assert storage.exists(key) is True

        # Retrieve and verify bit-for-bit identity
        retrieved_bytes = storage.get_object(key)
        assert retrieved_bytes == data

        # Check metadata
        meta = storage.get_metadata(key)
        assert meta["size_bytes"] == len(data)
        assert meta["checksum"] == expected_checksum

    def test_reject_corrupt_data_checksum_mismatch(self, tmp_path):
        storage = AudioObjectStorage(base_dir=str(tmp_path))
        key = "corrupt_test.pcm"
        data = b"correct_data"
        wrong_checksum = "0000000000000000000000000000000000000000000000000000000000000000"

        with pytest.raises(ValueError) as exc:
            storage.put_object(key, data, expected_checksum=wrong_checksum)
        assert "Checksum mismatch" in str(exc.value)
        assert storage.exists(key) is False
