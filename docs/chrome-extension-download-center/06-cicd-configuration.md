# CI/CD Configuration & Automated Build Pipeline

## 1. Automated Pipeline Overview

The CI/CD pipeline is defined in `.github/workflows/extension-release.yml`. It runs automatically when a release tag is pushed (`v*.*.*`) or when triggered manually via `workflow_dispatch`.

```
Git Tag Push (v*.*.*)
         |
         v
Install Monorepo Dependencies (pnpm)
         |
         v
Run Vitest Extension Unit Tests
         |
         v
Typecheck & Lint (tsc --noEmit)
         |
         v
Vite Extension Build (dist/)
         |
         v
Automated Packager & Secret Scan (scripts/package_extension.py)
         |
         v
Verify Root Manifest V3 in Generated ZIP
         |
         v
Upload Artifacts to Workflow Run
         |
         v
Publish GitHub Release with ZIP & Checksum
```

---

## 2. Packaging CLI (`scripts/package_extension.py`)

The packaging engine guarantees production compliance before any artifact is uploaded:

```bash
# Run packager CLI
python scripts/package_extension.py --channel stable --out-dir storage/releases
```

### Steps Performed by Packager:
1. **Source Inspection**: Validates that `apps/extension/dist` contains all compiled chunks (`service-worker.js`, `sidepanel.html`, `pcm-processor.js`).
2. **Root Manifest Placement**: Places `manifest.json` directly at the root of the ZIP archive.
3. **Secret Scan**: Inspects every file name and path for forbidden patterns:
   - `.env`, `.env.*`
   - `.pem`, `.key`, `id_rsa`
   - `client_secret`, `service_account`
   - `password`, token files
4. **SHA-256 Checksum**: Generates 64-character hexadecimal SHA-256 hash.
5. **Sidecar Generation**: Emits sidecar `checksum.sha256` and `release-manifest.json`.

---

## 3. GitHub Actions Workflow Configuration

```yaml
name: Chrome Extension Automated Build & Release Pipeline

on:
  push:
    tags:
      - 'v*.*.*'
  workflow_dispatch:
    inputs:
      channel:
        description: 'Release channel (stable, beta, internal)'
        required: true
        default: 'stable'
        type: choice
        options:
          - stable
          - beta
          - internal

jobs:
  validate-and-build:
    name: Build, Scan & Package Extension
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - uses: pnpm/action-setup@v3
        with:
          version: 9
      - run: pnpm install --frozen-lockfile=false
      - run: pnpm --filter @fluentmeet/extension test
      - run: pnpm --filter @fluentmeet/extension build
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: python scripts/package_extension.py --channel ${{ inputs.channel || 'stable' }} --out-dir dist-releases
      - uses: actions/upload-artifact@v4
        with:
          name: extension-release-artifacts
          path: dist-releases/
```

