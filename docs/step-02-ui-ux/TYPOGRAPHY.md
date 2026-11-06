# Typography System & Editorial Guidelines

**Product Name:** AI Meeting English Coach  
**Document ID:** TYPO-SYS-V1.0  
**Phase:** Step 02  
**Status:** Approved Typographic Baseline  

---

## 1. Font Families & Loading Strategy

The application employs a dual-stack typography strategy optimized for high-density SaaS productivity and crystal-clear transcript readability:

```
Primary Interface & Headings:
  Inter / Geist Sans, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif

Monospace & Technical Data:
  Geist Mono / JetBrains Mono, ui-monospace, SFMono-Regular, Menlo, monospace
```

- **Inter / Geist Sans:** Chosen for neutral letterforms, tall x-height, and superior legibility across varied pixel densities (Retina and standard 1080p displays).
- **JetBrains Mono:** Dedicated to audio timestamps (`[00:14:22]`), API tokens, error stack traces, and phonetic IPA notations (`/dɪˈvel.əp.mənt/`).

---

## 2. Typographic Scale & Hierarchy

| Token | Size | Line Height | Weight | Letter Spacing | Primary Purpose |
|---|---|---|---|---|---|
| `type-display` | 36px (2.25rem) | 44px (1.22) | Bold (700) | -0.025em | Marketing landing headlines, high-impact hero dials |
| `type-h1` | 30px (1.875rem)| 38px (1.26) | Bold (700) | -0.02em | Primary page headers ("Good morning, Priya") |
| `type-h2` | 24px (1.5rem) | 32px (1.33) | Semibold (600) | -0.015em | Major section headers ("Meetings Archive") |
| `type-h3` | 20px (1.25rem) | 28px (1.40) | Semibold (600) | -0.01em | Card headers, drawer titles |
| `type-h4` | 18px (1.125rem)| 26px (1.44) | Semibold (600) | -0.005em | Sub-card headers, modal titles |
| `type-body-lg` | 16px (1.0rem) | 24px (1.50) | Regular (400) | 0.00em | Lead summary paragraphs |
| `type-body` | 14px (0.875rem)| 20px (1.42) | Regular (400) | 0.00em | **Default body text, table cells, form labels** |
| `type-small` | 13px (0.8125rem)| 18px (1.38)| Regular (400) | 0.00em | Compact table rows, secondary captions |
| `type-caption` | 12px (0.75rem) | 16px (1.33) | Medium (500) | +0.01em | Timestamps, supporting hints, tooltips |
| `type-micro` | 11px (0.6875rem)| 14px (1.27) | Medium (500) | +0.02em | Status pill labels, uppercase column headers |

---

## 3. Editorial & Numerical Rules

### 3.1 Tabular Numerals Requirement
All dynamic metrics that change in real-time (elapsed recording timers, Words Per Minute indicators, audio duration scrubber, and score dials) must include the `.tabular-nums` CSS class (`font-variant-numeric: tabular-nums`). This prevents jitter and visual flickering as digits increment (e.g., transitions from `1` to `0`).

### 3.2 Transcript Line Length & Readability
To optimize reading comprehension during post-meeting review:
- Transcript text containers must maintain a maximum line length between **60 and 75 characters**.
- Paragraph line height for spoken utterances is locked to **1.6** to facilitate scanning without eye fatigue.

### 3.3 Phonetic IPA Representation
Phonetic pronunciation guides must be styled in monospace with distinctive syntax coloring:  
`Target IPA: `/dɪˈvel.əp.mənt/` with syllable stress capitalized or bolded.

