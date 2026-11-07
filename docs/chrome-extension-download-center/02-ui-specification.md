# UI Specification — Chrome Extension Download Center

## 1. Navigation Placement & Hierarchy

In accordance with the specification guidelines, the Chrome Extension navigation item is placed within the primary sidebar navigation hierarchy under the **System** grouping:

```
Navigation Hierarchy:
├── Workspace
│   ├── Dashboard Overview
│   └── All Meetings
├── My English
│   ├── My Performance
│   ├── Grammar Analysis
│   ├── Vocabulary
│   ├── Fluency Dynamics
│   ├── Pronunciation
│   └── IELTS Benchmarking
├── Learning
│   ├── Learning Center
│   ├── Mistake History
│   └── Improvement Plan
├── Organization
│   └── Team Analytics
└── System
    ├── Integrations
    ├── Chrome Extension  <--- [Dedicated Navigation Entry]
    ├── Billing & Usage
    └── Settings
```

- **Navigation Label:** `Chrome Extension`
- **Icon:** `Puzzle` (lucide-react)
- **Active State:** Indigo pill highlight (`bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300`)
- **Responsive Behavior:** Collapses into 16px icon-only rail on desktop when collapsed; drawer toggle on mobile viewports (<768px).

---

## 2. Page Layout Structure

### 2.1 Header Section
- **Page Title:** `Chrome Extension`
- **Version Badge:** `v1.0.0 Stable`
- **Subtitle:** `Download, install and manage the latest version of your meeting assistant extension.`
- **Header Actions:** `Check for Updates` button with live fetch trigger.

### 2.2 Dual Distribution Callout Banner
- Explains the difference between the **Chrome Web Store** channel (automatic silent background updates) and the **Dashboard ZIP Download** channel (unpacked manual installation, testing, and archive).
- Includes external deep link button: `Install from Chrome Web Store`.

### 2.3 Main Download Card
- **Extension Identity:**
  - Gradient badge logo (`FM`)
  - Full title: `FluentMeet AI — Real-time English Meeting Coach`
  - Badges: `Stable`, `Available & Verified`
- **Release Metadata Grid:**
  - Latest Version: e.g. `v1.0.0`
  - Release Date: Formatted date (e.g. `07 November 2026`)
  - Package: `ZIP (96.0 KB)`
  - Browser Support: `Chrome 116+ (Manifest V3)`
- **Download Action Button:**
  - Prominent primary button: `Download Chrome Extension (ZIP)`
  - Triggers direct download of `/api/v1/extensions/releases/latest/download?channel=stable`
- **SHA-256 Checksum Card:**
  - Full checksum display with one-click `Copy Checksum` button.
  - Green `Copied!` feedback state.
- **Release Notes Highlights:**
  - Bulleted summary of new features, performance gains, and bug fixes.

### 2.4 Installation & Setup Guide (9-Step Responsive Cards)
1. **Download Package:** Download the latest verified ZIP bundle.
2. **Extract ZIP Archive:** Extract into a permanent local directory (do not delete or relocate).
3. **Open `chrome://extensions`:** Enter the extensions management URL in Chrome.
4. **Enable Developer Mode:** Switch the toggle in the top-right corner to ON.
5. **Select "Load Unpacked":** Click the toolbar button in the top-left.
6. **Select Extracted Folder:** Pick the directory containing `manifest.json` at root.
7. **Pin Extension Icon:** Pin FluentMeet AI to Chrome's extension toolbar.
8. **Sign In with SaaS Account:** Open the Side Panel and authenticate with SaaS credentials.
9. **Verify Meeting Sync:** Open Google Meet, Zoom, or Teams to verify coaching activates.

### 2.5 Version History Table
- **Columns:**
  - `Version` (with expandable disclosure arrow)
  - `Channel` (Stable / Beta / Internal)
  - `Release Date`
  - `Package Size`
  - `Status` (Current Stable / Archived)
  - `SHA-256 Checksum` (truncated with copy button)
  - `Download Action` (dedicated button per historical release)
- **Expanded Drawer View:**
  - Full un-truncated SHA-256 checksum
  - Build identifier (e.g. `build-20261107-001`)
  - Git commit SHA (e.g. `7f9a2b1`)
  - Manifest version (`MV3`)
  - Detailed changelog list

---

## 3. Super Admin Management Console (Screen 14)

Accessible via **Admin Panel → Extension Releases**:
- **Operational Metrics Banner:** Total Releases, Current Stable Version, Total Downloads, Security Model.
- **Filtering Toolbar:** Channel selector (`All`, `Stable`, `Beta`, `Internal`) and Status dropdown (`All`, `Draft`, `Ready for Review`, `Approved`, `Published`, `Withdrawn`, `Failed`).
- **Create Release Modal:** Form supporting Version (SemVer), Channel, Min Chrome Version, Commit SHA, and bulleted release notes.
- **Interactive Action Matrix:**
  - `Build` (triggers packaging from dist)
  - `Validate` (verifies Manifest V3, permissions, secret scan, checksum)
  - `Approve` (transitions to approved)
  - `Publish` (transitions to published and updates live pointer)
  - `Withdraw` (immediately pulls release from public distribution)
  - `Rollback` (rolls back latest pointer to previous stable release)
  - `Logs` (opens event audit drawer)

