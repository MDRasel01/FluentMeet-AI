# Design System & Component Library Specification

**Product Name:** AI Meeting English Coach  
**Document ID:** SPEC-DESIGN-V1.0  
**Status:** Approved Design System Blueprint  
**Version:** 1.0.0  

---

## 1. Design Tokens & CSS Variables

The design system is codified as semantic tokens that support dynamic theme switching (Light Mode, Dark Mode, and High Contrast). Hardcoded hex values outside these tokens are strictly prohibited across all codebases.

### 1.1 Color Tokens

```css
:root {
  /* Primary Brand Tokens */
  --color-primary: #635BFF;
  --color-primary-hover: #5147E5;
  --color-primary-active: #4338CA;
  --color-primary-soft: #F0EFFF;
  --color-primary-contrast: #FFFFFF;

  /* Neutral Surface & Background Tokens (Light) */
  --color-bg-app: #F8FAFC;
  --color-bg-surface: #FFFFFF;
  --color-bg-surface-elevated: #FFFFFF;
  --color-bg-subtle: #F1F5F9;
  --color-border-subtle: #E2E8F0;
  --color-border-strong: #CBD5E1;

  /* Neutral Text Tokens (Light) */
  --color-text-heading: #111827;
  --color-text-body: #475569;
  --color-text-muted: #94A3B8;
  --color-text-inverse: #FFFFFF;

  /* Status Tokens */
  --color-status-success: #16A34A;
  --color-status-success-soft: #DCFCE7;
  --color-status-warning: #F59E0B;
  --color-status-warning-soft: #FEF3C7;
  --color-status-error: #DC2626;
  --color-status-error-soft: #FEE2E2;
  --color-status-info: #2563EB;
  --color-status-info-soft: #DBEAFE;

  /* Focus & Elevation */
  --focus-ring: 0 0 0 2px #FFFFFF, 0 0 0 4px #635BFF;
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
}

.dark {
  /* Neutral Surface & Background Tokens (Dark) */
  --color-bg-app: #0B1020;
  --color-bg-surface: #111827;
  --color-bg-surface-elevated: #1F2937;
  --color-bg-subtle: #172033;
  --color-border-subtle: #273449;
  --color-border-strong: #374151;

  /* Neutral Text Tokens (Dark) */
  --color-text-heading: #F8FAFC;
  --color-text-body: #9CA3AF;
  --color-text-muted: #64748B;
  --color-text-inverse: #0B1020;

  /* Primary Dark Overrides */
  --color-primary-soft: #1E1B4B;

  /* Focus & Elevation (Dark) */
  --focus-ring: 0 0 0 2px #0B1020, 0 0 0 4px #635BFF;
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.5);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.5);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.6);
}
```

---

## 2. Typography System

### 2.1 Font Families
- **Primary Interface Font:** `Inter`, `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `Roboto`, `sans-serif`
- **Data & Numerical Font:** `Geist Sans`, `Inter`, `sans-serif`
- **Monospace & Code Font:** `JetBrains Mono`, `Geist Mono`, `ui-monospace`, `monospace`

### 2.2 Type Hierarchy

| Token | Font Size | Line Height | Font Weight | Typical Use Case |
|---|---|---|---|---|
| `type-display` | 36px (2.25rem) | 44px (1.22) | Bold (700) | Landing page marketing headers |
| `type-h1` | 30px (1.875rem)| 38px (1.26) | Bold (700) / Semibold (600) | Dashboard Primary Page Titles |
| `type-h2` | 24px (1.5rem) | 32px (1.33) | Semibold (600) | Major Section Headers |
| `type-h3` | 18px (1.125rem)| 26px (1.44) | Semibold (600) | Card Headers & Modal Titles |
| `type-body-lg` | 16px (1.0rem) | 24px (1.5) | Regular (400) / Medium (500) | Primary Lead Paragraphs |
| `type-body` | 14px (0.875rem)| 20px (1.42) | Regular (400) | Default Body Text & Table Cells |
| `type-body-sm` | 12px (0.75rem) | 16px (1.33) | Medium (500) / Regular (400) | Supporting Labels & Timestamps |
| `type-caption` | 11px (0.6875rem)|14px (1.27) | Medium (500) | Micro Badges & Axis Labels |

---

## 3. Spacing, Radius & Layout Scale

### 3.1 Spacing Scale (Base: 4px)
- `space-1`: 4px | `space-2`: 8px | `space-3`: 12px | `space-4`: 16px
- `space-6`: 24px (Standard Card Padding & Section Gaps)
- `space-8`: 32px | `space-12`: 48px | `space-16`: 64px

### 3.2 Border Radius Scale
- `radius-sm`: 4px (Checkboxes, micro badges)
- `radius-md`: 8px (Form inputs, standard buttons, dropdown menus)
- `radius-lg`: 12px (Standard cards, modal containers)
- `radius-xl`: 16px (Feature callout panels, side panel floating widgets)
- `radius-full`: 9999px (Avatars, pills, toggle switches)

---

## 4. UI Component Library Specifications

The application uses an atomic component architecture. Every component adheres to an explicit state machine:
`[Default] ──► [Hover] ──► [Focus] ──► [Active] ──► [Disabled] ──► [Loading]`

### 4.1 Button & Icon Button
- **Variants:**
  - `Primary`: Solid `--color-primary`, white text.
  - `Secondary`: White/Surface bg, `--color-border-subtle` border, `--color-text-heading` text.
  - `Destructive`: Solid `--color-status-error` or error border.
  - `Ghost`: Transparent bg, hover subtle bg.
- **Sizes:** Small (32px height, 12px font), Medium (38px height, 14px font), Large (46px height, 16px font).
- **States:** Hover (darken 8%), Focus (2px offset ring), Active (scale 0.98), Disabled (opacity 50%, not-allowed cursor), Loading (replaces label with inline SVG spinner, maintains button dimensions).

### 4.2 Form Inputs (Input, Select, Textarea)
- **Props:** `label`, `errorText`, `helperText`, `leadingIcon`, `trailingIcon`, `required`, `disabled`.
- **States:**
  - `Default`: 1px `--color-border-subtle`, surface bg.
  - `Focus`: 1px `--color-primary` border + 3px primary soft glow ring.
  - `Error`: 1px `--color-status-error` border + error helper text below.
  - `Disabled`: Subtle bg, muted placeholder, read-only.

### 4.3 Interactive Audio Player
- **Props:** `src`, `duration`, `currentTime`, `waveformData`, `onSeek`, `playbackRate` (0.75x, 1.0x, 1.25x, 1.5x).
- **Subcomponents:**
  - **Play/Pause Button:** 36px circular toggle with high-contrast icon.
  - **Mini Waveform / Scrubber:** Canvas or SVG-rendered waveform bars. Clicking seeks to timestamp. Highlight bar indicates buffer and elapsed time.
  - **Timestamp Indicator:** Monospace display (`00:14:22 / 00:45:00`).
  - **Speed Selector:** Compact dropdown pill toggling playback rate.

### 4.4 Transcript Segment Component
- **Props:** `speakerName`, `speakerColor`, `timestampStart`, `timestampEnd`, `text`, `mistakes` (array of flagged ranges), `isActive`, `onClick`.
- **Visuals:**
  - Displays speaker badge, formatted timestamp (`[14:22]`), and full spoken text.
  - Flagged grammatical or lexical mistakes have an interactive wavy underline (amber for nuance, red for grammar, blue for pronunciation).
  - Hovering a wavy underline displays a micro-popover with quick correction.
  - When audio plays this segment, the background shifts to `--color-primary-soft` with a smooth 150ms transition.

### 4.5 Score Indicator Dial & Pills
- **Props:** `score` (0-100 or 0.0-9.0), `dimension` (Grammar, Vocabulary, Fluency, Pronunciation), `trend` (+3% vs last meeting), `size` (`sm`, `md`, `lg`).
- **Color Rules:**
  - $\ge$ 85: `--color-status-success` (Green)
  - 70–84: `--color-status-info` (Blue)
  - 50–69: `--color-status-warning` (Amber)
  - < 50: `--color-status-error` (Red)
  - Insufficient Data: Neutral Gray with tooltip: *"Needs $\ge$ 2 minutes of active speech to score"*.

### 4.6 Stat Card & Chart Card
- **Structure:**
  - Card Header: Metric Title + Tooltip Info Icon + Filter/Date Range.
  - Card Body: Primary Large Metric (`type-display` or `type-h1`) + Trend Pill (`+12% vs last month` with green/red arrow).
  - Card Footer / Chart Area: Micro sparkline or responsive area/bar chart.

### 4.7 Feedback & Dialog Components (Toast, Modal, Drawer, Confirmation)
- **Toast Notifications:** Fixed top-right floating stack. Auto-dismiss after 4000ms. Types: Success, Error, Warning, Info.
- **Confirmation Dialog:** Accessible modal trapping focus. Requires explicit confirmation for destructive operations (e.g., "Permanently Delete Meeting Recording & Transcript").

