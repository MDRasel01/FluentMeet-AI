#!/usr/bin/env python3
"""
FluentMeet AI - Chrome Extension Production Release Packager CLI
Usage:
    python scripts/package_extension.py [--channel stable] [--out-dir storage/releases]
"""

import os
import sys
import argparse
import json
import hashlib
from pathlib import Path

# Add services/api to sys.path so we can import app services
repo_root = Path(__file__).resolve().parent.parent
api_dir = repo_root / "services" / "api"
if str(api_dir) not in sys.path:
    sys.path.insert(0, str(api_dir))

from app.services.extension_builder_service import builder_service
from app.services.extension_storage_service import extension_storage

def main():
    parser = argparse.ArgumentParser(description="Package FluentMeet AI Chrome Extension")
    parser.add_argument("--channel", default="stable", choices=["stable", "beta", "internal"], help="Release channel")
    parser.add_argument("--out-dir", default=None, help="Output destination folder")
    parser.add_argument("--version", default=None, help="Version override (default: from manifest.json)")
    args = parser.parse_args()

    print(f"📦 Packaging FluentMeet AI Chrome Extension (Channel: {args.channel})...")
    try:
        packaged = builder_service.package_from_dist(version_override=args.version)
        version = packaged["version"]
        filename = packaged["filename"]
        sha256 = packaged["sha256"]
        size_bytes = packaged["size_bytes"]
        zip_bytes = packaged["zip_bytes"]

        print(f"✅ Package validated successfully!")
        print(f"   - Version: v{version}")
        print(f"   - Artifact: {filename}")
        print(f"   - Package Size: {size_bytes:,} bytes ({size_bytes / 1024:.1f} KB)")
        print(f"   - SHA-256 Checksum: {sha256}")
        print(f"   - Manifest Version: {packaged['manifest'].get('manifest_version')}")

        if args.out_dir:
            out_path = Path(args.out_dir) / args.channel / version
            out_path.mkdir(parents=True, exist_ok=True)
            zip_dest = out_path / filename
            zip_dest.write_bytes(zip_bytes)
            (out_path / "checksum.sha256").write_text(f"{sha256}  {filename}\n", encoding="utf-8")
            (out_path / "release-manifest.json").write_text(
                json.dumps(packaged["manifest"], indent=2), encoding="utf-8"
            )
            print(f"📁 Artifact written to: {zip_dest}")
        else:
            storage_key, checksum, sz = extension_storage.store_release_artifact(
                channel=args.channel,
                version=version,
                filename=filename,
                data=zip_bytes,
                expected_checksum=sha256
            )
            print(f"💾 Stored in object storage: {storage_key}")

    except Exception as e:
        print(f"❌ Error packaging extension: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

