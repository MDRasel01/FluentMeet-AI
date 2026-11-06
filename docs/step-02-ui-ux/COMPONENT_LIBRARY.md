# Shared Component Library Specification

**Product Name:** AI Meeting English Coach  
**Document ID:** COMP-LIB-V1.0  
**Phase:** Step 02  
**Status:** Approved Component Reference  

---

## 1. Component Architecture Overview

All shared UI components are centrally located in `design-system/components/` and exported via `design-system/components/index.ts`. They are built with React 19, TypeScript, and Tailwind CSS using `clsx` for deterministic class merging.

```
┌─────────────────────────────────────────────────────────────┐
│                 Component Library Structure                 │
├─────────────────┬───────────────────────────────────────────┤
│ Actions         │ Button, IconButton, ActionMenu            │
│ Forms           │ Input, Select, Textarea, Checkbox, Switch │
│ Data Display    │ Card, StatCard, ScoreIndicator, Badge     │
│ Audio & Speech  │ AudioPlayer, TranscriptSegment            │
│ Coaching Cards  │ GrammarErrorCard, VocabularyCard          │
│ Overlays        │ Modal, Drawer, Tooltip, ConfirmationDialog│
│ Universal States│ SkeletonLoader, EmptyState, ErrorState    │
└─────────────────┴───────────────────────────────────────────┘
```

---

## 2. Core Component Specifications

### 2.1 Button Component (`Button.tsx`)
- **Location:** `design-system/components/Button.tsx`
- **Variants:** `primary`, `secondary`, `outline`, `ghost`, `destructive`, `link`.
- **Sizes:** `sm` (32px), `md` (38px), `lg` (46px).
- **Props:** `loading?: boolean`, `leadingIcon?: ReactNode`, `trailingIcon?: ReactNode`, `fullWidth?: boolean`.
- **State Behavior:**
  - `Loading`: Displays animated `Loader2` SVG spinner, disables pointer events, preserves button width.
  - `Focus-visible`: Renders high-contrast 2px offset ring (`ring-indigo-500`).
  - `Disabled`: Opacity 50%, pointer-events-none.

### 2.2 Form Input Component (`Input.tsx`)
- **Location:** `design-system/components/Input.tsx`
- **Props:** `label?: string`, `error?: string`, `helperText?: string`, `leadingIcon?: ReactNode`, `trailingIcon?: ReactNode`.
- **State Behavior:**
  - `Default`: 1px slate-300 border, white background.
  - `Focus`: 2px indigo-500 border ring.
  - `Error`: Rose-500 border with subtext alert icon and message.
  - `Disabled`: Slate-100 fill with muted cursor.

### 2.3 Stat Card Component (`StatCard.tsx`)
- **Location:** `design-system/components/StatCard.tsx`
- **Props:** `title: string`, `value: string | number`, `change?: string`, `trend?: 'up' | 'down' | 'neutral'`, `supportingText?: string`, `icon?: ReactNode`.
- **Visuals:** Displays metric title, prominent value with `.tabular-nums`, and trend pill with green/rose directional arrows (`TrendingUp`, `TrendingDown`).

### 2.4 Score Indicator Component (`ScoreIndicator.tsx`)
- **Location:** `design-system/components/ScoreIndicator.tsx`
- **Props:** `score: number`, `maxScore?: number`, `label?: string`, `size?: 'sm' | 'md' | 'lg'`, `insufficientData?: boolean`.
- **Semantic Colors:**
  - $\ge$ 85: Emerald (`#16A34A` / `bg-emerald-50`)
  - 70–84: Indigo (`#6366F1` / `bg-indigo-50`)
  - 50–69: Amber (`#D97706` / `bg-amber-50`)
  - < 50: Rose (`#DC2626` / `bg-rose-50`)
  - `insufficientData`: Neutral Slate pill reading *"Insufficient Data"* with explanatory sublabel.

### 2.5 Audio Player Component (`AudioPlayer.tsx`)
- **Location:** `design-system/components/AudioPlayer.tsx`
- **Props:** `currentTime: number`, `duration: number`, `isPlaying?: boolean`, `onPlayPause?: () => void`, `onSeek?: (secs: number) => void`.
- **Features:** Play/Pause 40px circular button, 5-second rewind/forward skips, interactive timeline scrubber with hover seek thumb, elapsed/total time in `.tabular-nums`, and 4-speed toggle (0.75x, 1x, 1.25x, 1.5x).

### 2.6 Transcript Segment Component (`TranscriptSegment.tsx`)
- **Location:** `design-system/components/TranscriptSegment.tsx`
- **Props:** `speakerName: string`, `speakerColor: string`, `timestamp: string`, `text: string`, `mistakes?: MistakeSpan[]`, `isActive?: boolean`.
- **Features:** Displays speaker avatar pill, timestamp badge, and spoken sentence. Mistake spans carry clickable tags that expand into grammar explanations. When synced with active audio, background shifts smoothly to `bg-indigo-50/70`.

### 2.7 Grammar Error Card (`GrammarErrorCard.tsx`)
- **Location:** `design-system/components/GrammarErrorCard.tsx`
- **Props:** `originalSentence: string`, `correctedSentence: string`, `errorCategory: string`, `severity?: 'high' | 'medium' | 'low'`, `explanation: string`, `timestamp?: string`, `onPlayAudio?: () => void`, `onAddToPractice?: () => void`, `isSaved?: boolean`.
- **Features:** Side-by-side or stacked "What you said" (rose) vs. "Better alternative" (emerald), linguistic rule explanation, play audio excerpt button, and save to practice deck toggle.

### 2.8 Universal State Components (`EmptyState.tsx`, `ErrorState.tsx`, `SkeletonLoader.tsx`)
- **EmptyState:** Clean container with icon, heading, descriptive explanation, and primary/secondary CTAs. Strictly avoids fake mock metrics.
- **ErrorState:** Inline or centered card with error triangle, cause description, and "Retry Connection" button.
- **SkeletonLoader:** Pulse animated shimmer placeholder mirroring cards, table rows, and score dials.

### 2.9 Overlay Components (`Modal.tsx`, `ConfirmationDialog.tsx`)
- **Modal:** Focus-trapping accessible dialog with backdrop blur, escape key listener, scroll locking, and customizable header/body/footer.
- **ConfirmationDialog:** Specialized modal for destructive operations (e.g., account data purging, token revocation).

