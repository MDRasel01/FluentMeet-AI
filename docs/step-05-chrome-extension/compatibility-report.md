# Browser & Platform Compatibility Matrix
## Specification: Step 05 — Section 20.13

---

## 1. Operating System Compatibility

| Operating System | Supported | Minimum Tested Version | Verification Notes |
|---|---|---|---|
| **Microsoft Windows** | **YES** | Windows 10 / 11 64-bit | Primary test execution environment. Both WASAPI speaker routing and microphone capture validated. |
| **macOS** | **YES** | macOS 12 (Monterey)+ | Standard CoreAudio tab capture and permission prompts. |
| **Linux** | **YES** | Ubuntu 22.04 LTS (X11 / Wayland) | PulseAudio / PipeWire capture supported by Chrome 116+. |
| **ChromeOS** | **YES** | ChromeOS 116+ | Native system audio pass-through verified. |

---

## 2. Browser Version Requirements

- **Minimum Required Version:** **Chrome 116.0+**
  - *Reasoning:* Chrome 116 introduced the ability to share `chrome.tabCapture.getMediaStreamId()` across same-origin offscreen documents, and stabilized `chrome.runtime.getContexts({ contextTypes: ['OFFSCREEN_DOCUMENT'] })`.
- **Target Version:** **Chrome 120.0+ / Current Stable**
- **Chromium Derivatives (Edge, Brave, Opera):** Supported provided Manifest V3 SidePanel and Offscreen APIs are enabled.

