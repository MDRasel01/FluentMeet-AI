# Installation & Update Guide

## 1. Distribution Methods Overview

| Workflow | Target Audience | Installation Method | Update Mechanism |
|---|---|---|---|
| **Chrome Web Store** | General End Users / Enterprise | One-click from Chrome Web Store | **Automatic background updates** via Chrome |
| **Dashboard ZIP** | Developers, QA, Staging, Offline | Download ZIP & load unpacked | **Manual reload** or re-extracting into same directory |

---

## 2. Unpacked Installation Guide (Dashboard ZIP)

### Step 1: Download the ZIP File
1. Navigate to the Web Dashboard.
2. Click **Chrome Extension** in the left sidebar.
3. Click the **Download Chrome Extension (ZIP)** button.
4. Verify that the downloaded file is named `fluentmeet-ai-v<version>.zip`.

### Step 2: Extract the Package
1. Extract the contents of the ZIP file into a permanent directory on your computer (e.g., `C:\Extensions\FluentMeet-AI` or `~/Extensions/FluentMeet-AI`).
2. **Important:** Do not delete or move this directory after loading it into Chrome, or Chrome will not find the extension files.

### Step 3: Open Chrome Extensions Manager
1. In Google Chrome, open a new tab.
2. In the URL bar, type:
   ```
   chrome://extensions
   ```
   and press Enter.

### Step 4: Enable Developer Mode
1. In the top-right corner of the Extensions page, locate the **Developer mode** toggle switch.
2. Toggle it to the **ON** position. Three new buttons will appear in the top-left toolbar: *Load unpacked*, *Pack extension*, and *Update*.

### Step 5: Load the Extension
1. Click the **Load unpacked** button.
2. In the file dialog, navigate to and select the extracted folder (the directory containing `manifest.json` directly inside).
3. Click **Select Folder**.

### Step 6: Verify Extension Registration
1. Verify that **FluentMeet AI — Real-time English Meeting Coach** appears in the extensions list with version `v1.0.0` and status enabled.
2. Click the Chrome puzzle piece icon in the browser toolbar and pin the FluentMeet AI coach icon.

### Step 7: Sign In & Authenticate
1. Click the FluentMeet AI icon to launch the Side Panel.
2. Enter your SaaS account email and password to log in.
3. Once logged in, the side panel will display the *Ready & Waiting for Call* state.

### Step 8: Test Meeting Detection
1. Open a Google Meet, Zoom Web, or Microsoft Teams Web call in another tab.
2. The Side Panel will detect the meeting platform, prompt for audio capture confirmation, and begin live coaching.

---

## 3. Updating an Existing Unpacked Installation

When a new version is released on the Dashboard:
1. Download the new version ZIP from the **Chrome Extension** page.
2. Extract the new ZIP file, replacing the files in your existing permanent folder.
3. Open `chrome://extensions`.
4. Locate **FluentMeet AI** and click the circular **Reload (↻)** icon.
5. The extension will refresh with the new version code immediately while retaining your active login session!

