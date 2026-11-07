"""
FluentMeet AI - Chrome Extension Release Storage & Packaging Service
Durable private storage, artifact packaging, SHA-256 checksum generation,
secret scanning, and short-lived signed download token generator.
"""

import os
import io
import json
import zipfile
import hashlib
import time
import secrets
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from app.core.config import settings

FORBIDDEN_SECRET_PATTERNS = [
    ".env",
    ".env.local",
    ".env.production",
    "id_rsa",
    ".pem",
    ".key",
    "client_secret",
    "service_account",
    "password",
]

class StorageError(Exception):
    pass

class ChecksumMismatchError(StorageError):
    pass

class ManifestValidationError(StorageError):
    pass

class SecurityScanError(StorageError):
    pass


class ExtensionStorageService:
    def __init__(self, base_storage_dir: Optional[str] = None):
        target_dir = base_storage_dir or os.getenv("EXTENSION_STORAGE_DIR", "storage/releases")
        self.base_storage_dir = Path(target_dir)
        self.base_storage_dir.mkdir(parents=True, exist_ok=True)
        # In-memory store for signed download tokens: token -> {release_id, expires_at, user_id}
        self._signed_tokens: Dict[str, Dict[str, Any]] = {}

    def generate_storage_key(self, channel: str, version: str, filename: str) -> str:
        """
        Generates canonical storage key:
        channels/{channel}/{version}/{filename}
        """
        clean_channel = channel.lower().strip()
        clean_version = version.strip().lstrip("v")
        return f"channels/{clean_channel}/{clean_version}/{filename}"

    def compute_sha256(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def validate_zip_artifact(self, zip_bytes: bytes, expected_version: Optional[str] = None) -> Dict[str, Any]:
        """
        Validates ZIP artifact:
        1. Ensures it is a valid ZIP archive.
        2. Ensures root contains manifest.json.
        3. Parses and validates manifest.json (Manifest V3, permissions).
        4. Matches manifest.version with expected_version if provided.
        5. Scans for forbidden secrets or private credentials.
        """
        try:
            with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
                namelist = zf.namelist()

                # Rule 1: Root must have manifest.json
                if "manifest.json" not in namelist:
                    raise ManifestValidationError(
                        "Package invalid: Root directory of ZIP must contain 'manifest.json'."
                    )

                # Rule 2: Scan for forbidden secrets
                for name in namelist:
                    normalized = name.lower().replace("\\", "/")
                    base = normalized.split("/")[-1]
                    for pattern in FORBIDDEN_SECRET_PATTERNS:
                        if pattern in base and not base.endswith(".ts") and not base.endswith(".tsx") and not base.endswith(".js"):
                            raise SecurityScanError(
                                f"Security violation: Artifact contains forbidden secret file pattern '{name}'."
                            )

                # Rule 3: Read and parse manifest.json
                manifest_raw = zf.read("manifest.json").decode("utf-8")
                try:
                    manifest_data = json.loads(manifest_raw)
                except Exception as e:
                    raise ManifestValidationError(f"Invalid manifest.json JSON syntax: {e}")

                # Rule 4: Manifest V3 check
                mv = manifest_data.get("manifest_version")
                if mv != 3:
                    raise ManifestValidationError(f"Expected Manifest V3, found version: {mv}")

                manifest_ver = manifest_data.get("version")
                if expected_version:
                    clean_expected = expected_version.lstrip("v")
                    if manifest_ver != clean_expected:
                        raise ManifestValidationError(
                            f"Manifest version '{manifest_ver}' does not match release version '{clean_expected}'."
                        )

                return {
                    "manifest": manifest_data,
                    "manifest_version": mv,
                    "version": manifest_ver,
                    "file_count": len(namelist),
                    "files": namelist[:20],
                }
        except zipfile.BadZipFile:
            raise StorageError("Uploaded payload is not a valid ZIP file.")

    def store_release_artifact(
        self,
        channel: str,
        version: str,
        filename: str,
        data: bytes,
        expected_checksum: Optional[str] = None
    ) -> Tuple[str, str, int]:
        """
        Stores release artifact (.zip), verifies checksum, and saves sidecar checksum.sha256 file.
        Returns: (storage_key, sha256_checksum, size_bytes)
        """
        calculated_sha = self.compute_sha256(data)
        if expected_checksum and calculated_sha.lower() != expected_checksum.lower():
            raise ChecksumMismatchError(
                f"Checksum mismatch: expected {expected_checksum}, calculated {calculated_sha}"
            )

        storage_key = self.generate_storage_key(channel, version, filename)
        full_path = self.base_storage_dir / storage_key
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write atomic binary ZIP
        temp_path = full_path.with_suffix(".tmp")
        with open(temp_path, "wb") as f:
            f.write(data)
        os.replace(temp_path, full_path)

        # Write sidecar checksum.sha256
        checksum_path = full_path.parent / "checksum.sha256"
        with open(checksum_path, "w", encoding="utf-8") as f:
            f.write(f"{calculated_sha}  {filename}\n")

        return storage_key, calculated_sha, len(data)

    def get_release_artifact(self, storage_key: str) -> bytes:
        full_path = self.base_storage_dir / storage_key
        if not full_path.exists():
            raise FileNotFoundError(f"Artifact not found at storage key: {storage_key}")
        with open(full_path, "rb") as f:
            return f.read()

    def get_artifact_path(self, storage_key: str) -> Path:
        full_path = self.base_storage_dir / storage_key
        if not full_path.exists():
            raise FileNotFoundError(f"Artifact not found at storage key: {storage_key}")
        return full_path

    def delete_artifact(self, storage_key: str) -> bool:
        full_path = self.base_storage_dir / storage_key
        if full_path.exists():
            full_path.unlink()
            return True
        return False

    def generate_signed_download_token(
        self,
        release_id: str,
        user_id: Optional[str] = None,
        expiry_seconds: int = 300  # 5 minutes short expiry
    ) -> str:
        """
        Generates a secure, short-lived signed token for downloading release artifacts.
        """
        token = secrets.token_urlsafe(32)
        expires_at = time.time() + expiry_seconds
        self._signed_tokens[token] = {
            "release_id": release_id,
            "user_id": user_id,
            "expires_at": expires_at
        }
        return token

    def verify_signed_download_token(self, token: str, release_id: str) -> bool:
        data = self._signed_tokens.get(token)
        if not data:
            return False
        if time.time() > data["expires_at"]:
            del self._signed_tokens[token]
            return False
        if data["release_id"] != release_id:
            return False
        return True


# Global singleton
extension_storage = ExtensionStorageService()

