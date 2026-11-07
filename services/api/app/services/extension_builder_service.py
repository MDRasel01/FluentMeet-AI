"""
FluentMeet AI - Extension Packaging & Release Builder
Automates extension bundling, manifest validation, secret detection,
and zip package generation.
"""

import os
import io
import json
import zipfile
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional

from app.services.extension_storage_service import (
    extension_storage,
    FORBIDDEN_SECRET_PATTERNS,
    ManifestValidationError,
    SecurityScanError
)

class ExtensionBuilderService:
    def __init__(self, extension_root: Optional[Path] = None):
        if extension_root:
            self.extension_root = Path(extension_root)
        else:
            # Look relative to current file or repo root
            candidate_paths = [
                Path("apps/extension"),
                Path("../../apps/extension"),
                Path("../apps/extension"),
                Path("H:/Rasel/all_local_Projecrt/FluentMeet-AI/apps/extension")
            ]
            self.extension_root = None
            for p in candidate_paths:
                if (p / "manifest.json").exists():
                    self.extension_root = p.resolve()
                    break
            if not self.extension_root:
                self.extension_root = Path("apps/extension").resolve()

    def package_from_dist(self, dist_dir: Optional[Path] = None, version_override: Optional[str] = None) -> Dict[str, Any]:
        """
        Takes built files from dist_dir (or apps/extension/dist),
        verifies manifest.json exists, scans for forbidden files,
        and constructs an in-memory ZIP package.
        """
        target_dist = dist_dir or (self.extension_root / "dist")
        if not target_dist.exists():
            raise FileNotFoundError(f"Extension dist directory does not exist: {target_dist}. Run 'pnpm build' first.")

        manifest_file = target_dist / "manifest.json"
        if not manifest_file.exists():
            # Check if manifest.json exists in extension_root and copy
            root_manifest = self.extension_root / "manifest.json"
            if root_manifest.exists():
                manifest_content = root_manifest.read_text(encoding="utf-8")
                manifest_file.write_text(manifest_content, encoding="utf-8")
            else:
                raise ManifestValidationError(f"manifest.json not found in dist or extension root ({target_dist})")

        manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
        version = version_override or manifest_data.get("version", "1.0.0")
        clean_version = version.lstrip("v")
        manifest_data["version"] = clean_version

        # Create in-memory ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in target_dist.rglob("*"):
                if file_path.is_file():
                    rel_path = file_path.relative_to(target_dist).as_posix()

                    # Security scan
                    for pattern in FORBIDDEN_SECRET_PATTERNS:
                        if pattern in rel_path.lower():
                            raise SecurityScanError(f"Forbidden secret detected in dist: {rel_path}")

                    # Write file with relative path (manifest.json will be at root with synchronized version)
                    if rel_path == "manifest.json":
                        zf.writestr("manifest.json", json.dumps(manifest_data, indent=2))
                    else:
                        zf.write(file_path, arcname=rel_path)

        zip_bytes = zip_buffer.getvalue()

        # Validate the generated ZIP
        validation_info = extension_storage.validate_zip_artifact(zip_bytes, expected_version=version)
        sha256 = extension_storage.compute_sha256(zip_bytes)

        artifact_filename = f"fluentmeet-ai-v{version}.zip"

        return {
            "version": version,
            "filename": artifact_filename,
            "size_bytes": len(zip_bytes),
            "sha256": sha256,
            "zip_bytes": zip_bytes,
            "manifest": manifest_data,
            "validation_info": validation_info,
        }

builder_service = ExtensionBuilderService()
