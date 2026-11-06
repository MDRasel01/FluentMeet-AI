# Design System Specification & Token Architecture

**Product Name:** AI Meeting English Coach  
**Document ID:** DESIGN-SYS-V1.0  
**Phase:** Step 02  
**Status:** Approved Technical Design System  

---

## 1. System Architecture & Centralization Rules

The **AI Meeting English Coach Design System** is codified as a centralized collection of TypeScript tokens, CSS Custom Properties, and modular React components located in `design-system/`:

```
design-system/
├── tokens/
│   ├── colors.ts          # Hex palettes for Primary, Neutral, Semantic & Dark
│   ├── typography.ts      # Font stacks, sizes, line heights & weights
│   ├── spacing.ts         # 4px incremental scale (0px to 96px)
│   ├── radius.ts          # Border radius scale (xs: 4px to full: 9999px)
│   ├── shadows.ts         # Elevation box shadows for light and dark modes
│   ├── breakpoints.ts     # Responsive viewport boundaries (320px to 1600px)
│   └── index.ts           # Unified export bundle
├── themes/
│   ├── light.ts           # Semantic light theme mappings
│   ├── dark.ts            # High-contrast dark theme mappings
│   └── index.ts
└── components/            # Atomic, accessible React components
```

### The Cardinal Rule of Component Styling
> [!IMPORTANT]
> **Zero Hardcoded Values:** No UI component may define custom hex codes, random pixel paddings, or arbitrary border radii. All visual properties must consume either Tailwind theme utility classes or tokens exported from `design-system/tokens`.

---

## 2. Token Registry Overview

### 2.1 Color Tokens
- **Primary Brand:** Indigo (`#6366F1` / `primary-500`) with hover states (`#4F46E5` / `primary-600`) and soft background tints (`#EEF2FF` / `primary-50`).
- **Neutrals:** Slate palette ranging from Pure White (`#FFFFFF`) to Deepest Slate (`#0F172A` / `#020617`).
- **Semantic Status:**
  - Success: Emerald (`#16A34A` / soft `#DCFCE7`)
  - Warning: Amber (`#D97706` / soft `#FEF3C7`)
  - Danger / Error: Rose (`#DC2626` / soft `#FEE2E2`)
  - Info: Sky / Blue (`#2563EB` / soft `#DBEAFE`)

### 2.2 Typography Tokens
- **Primary Interface Stack:** `Inter`, `Geist Sans`, `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `sans-serif`.
- **Monospace & Timestamps:** `Geist Mono`, `JetBrains Mono`, `monospace`.
- **Tabular Numerals:** Standard `.tabular-nums` class applied to all timers, percentages, and score dials to eliminate layout jitter during live updates.

### 2.3 4px Spacing Scale
- `space-1`: 4px | `space-2`: 8px | `space-3`: 12px | `space-4`: 16px
- `space-5`: 20px | `space-6`: 24px (Standard Card Padding)
- `space-8`: 32px | `space-10`: 40px | `space-12`: 48px | `space-16`: 64px

### 2.4 Border Radius Scale
- `radius-xs`: 4px (micro tags, tooltips)
- `radius-sm`: 6px (compact buttons, sub-badges)
- `radius-md`: 8px (default form inputs, standard buttons)
- `radius-lg`: 12px (cards, audio player, modal containers)
- `radius-xl`: 16px (large feature panels, sidepanel frames)
- `radius-full`: 9999px (avatars, pills, score dials)

---

## 3. Light & Dark Theme Support

Theme switching is powered by the Tailwind `darkMode: 'class'` directive. The `.dark` class on the root `<html>` element toggles CSS custom variables:

| CSS Variable | Light Theme Value | Dark Theme Value | Purpose |
|---|---|---|---|
| `--color-bg-app` | `#F8FAFC` (Slate-50) | `#0B1020` (Deep Dark) | App body background |
| `--color-bg-surface` | `#FFFFFF` (Pure White) | `#111827` (Slate-900) | Card & sidebar surface |
| `--color-border-subtle` | `#E2E8F0` (Slate-200) | `#273449` (Dark Slate) | Dividers and borders |
| `--color-text-heading` | `#0F172A` (Slate-900) | `#F8FAFC` (Slate-50) | Primary headings |
| `--color-text-body` | `#334155` (Slate-700) | `#CBD5E1` (Slate-300) | Body reading text |
| `--color-text-muted` | `#64748B` (Slate-500) | `#94A3B8` (Slate-400) | Supporting labels |

---

## 4. Reusable Component Categories

The system provides 30+ production components categorized as:
1. **Buttons & Actions:** `Button` (Primary, Secondary, Outline, Ghost, Destructive, Link with Loading/Disabled states), `IconButton`.
2. **Form Controls:** `Input`, `Select`, `Textarea`, `Checkbox`, `Switch`.
3. **Data Display:** `Card`, `StatCard`, `MetricCard`, `Badge`, `Avatar`, `AvatarGroup`, `ProgressBar`, `ScoreIndicator`.
4. **Navigation:** `Tabs`, `Breadcrumb`, `Pagination`.
5. **Overlays & Feedback:** `Modal`, `Drawer`, `Tooltip`, `ConfirmationDialog`, `Alert`.
6. **Universal UI States:** `SkeletonLoader`, `EmptyState`, `ErrorState`.
7. **Domain-Specific Components:** `AudioPlayer` (synchronized timeline scrubber), `TranscriptSegment` (interactive wavy mistake highlights), `GrammarErrorCard` (native rephrase with audio excerpt), `VocabularyCard`.

