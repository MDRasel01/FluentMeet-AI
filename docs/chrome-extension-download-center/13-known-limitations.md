# Known Limitations & Future Roadmap

## 1. Known Architectural Limitations

1. **Unpacked Chrome Extension Manual Reload**:
   - Extensions loaded in Developer Mode (`chrome://extensions` → *Load unpacked*) cannot be automatically updated by the backend server.
   - Users must extract the newer ZIP over the existing folder and click the reload button (↻) in `chrome://extensions`.
   - **Remediation**: The Chrome Web Store channel is highlighted on the Dashboard as the recommended path for users requiring silent automatic background updates.

2. **Chrome Web Store Review Latency**:
   - Publishing an update to the Chrome Web Store is subject to Google's automated and manual review process, typically taking between 2 hours and 3 business days.
   - **Remediation**: The Dashboard ZIP distribution center allows urgent hotfixes and development builds to be distributed immediately to beta and internal users without waiting for Web Store review.

3. **In-Browser CRX Self-Hosting Restrictions**:
   - Modern versions of Google Chrome on Windows and macOS enforce strict Extension Install Verification policies that block direct inline installation of `.crx` files outside of enterprise domain group policy (GPO).
   - **Remediation**: The Download Center distributes clean standard `.zip` archives designed specifically for Developer Mode unpacked loading.

4. **Multi-Region Object Storage Redundancy**:
   - The current durable storage implementation utilizes local durable filesystem storage (`storage/releases/`).
   - For high-availability multi-region enterprise deployments, an S3 / Google Cloud Storage bucket adapter should be configured via environment variables.

---

## 2. Future Engineering Roadmap

- [ ] **Automated Chrome Web Store API Deployment**: Integrate `@google-chrome/webstore-upload` into GitHub Actions for automated store submissions.
- [ ] **In-Extension Upgrade Alert Banner**: When the extension polls `/api/v1/extensions/releases/latest` and detects a newer version than `chrome.runtime.getManifest().version`, display an interactive in-sidepanel update pill with a one-click redirect to the Dashboard or Web Store.
- [ ] **Signed Download URL S3 Presigner**: Generate AWS S3 / Cloudflare R2 presigned URLs with 15-minute expiration when running in multi-tenant cloud infrastructure.
- [ ] **Enterprise GPO / Intune Deployment Guide**: Document enterprise packaging and registry keys for silent multi-workstation deployment across corporate laptops.

