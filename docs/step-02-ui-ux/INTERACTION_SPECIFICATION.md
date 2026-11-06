# Interaction Design & Dynamic Behavior Specification

**Product Name:** AI Meeting English Coach  
**Document ID:** INTERACT-SPEC-V1.0  
**Phase:** Step 02  
**Status:** Approved Interaction Baseline  

---

## 1. Global Interaction Tenets

1. **Deterministic Feedback:** Every click, keystroke, and toggle must produce an immediate visual acknowledgement within 100ms.
2. **Synchronized Multi-Modality:** Text transcripts and audio playback maintain bidirectional state synchronization at all times.
3. **No Non-Functional Decorative Elements:** Every button, filter, tab, and pill in the interface executes a real state transition or data filter.

---

## 2. Core Interactive Workflows

```
┌─────────────────────────────────────────────────────────────┐
│             Audio-Transcript Bidirectional Sync             │
├───────────────────────────────┬─────────────────────────────┤
│ User Action:                  │ System Response:            │
│ 1. Clicks sentence in center  │ Audio seeks to timestamp.   │
│    transcript feed.           │ Audio player starts play.   │
├───────────────────────────────┼─────────────────────────────┤
│ 2. Scrubs timeline slider in  │ Active transcript segment   │
│    sticky bottom audio player.│ scrolls into viewport with  │
│                               │ indigo highlight background.│
├───────────────────────────────┼─────────────────────────────┤
│ 3. Clicks red mistake underline│ Right inspector drawer opens│
│    in transcript.             │ displaying rule & rephrase. │
└───────────────────────────────┴─────────────────────────────┘
```

---

## 3. Detailed Component Interaction Specifications

### 3.1 Navigation Interactions
- **Sidebar Collapse / Expand:**
  - *Trigger:* Clicking the toggle button (`← Collapse Sidebar`).
  - *Response:* Sidebar transitions from 240px to 64px width with a smooth 200ms ease-in-out transition. Navigation text labels fade out; tooltips appear on hover over icon-only buttons.
- **Active Navigation Highlights:**
  - *Trigger:* Route change.
  - *Response:* Active route item receives `bg-indigo-50 text-indigo-700` (`dark:bg-indigo-950/60 dark:text-indigo-300`) and removes active styles from previous routes.

### 3.2 Data Filtering & Search Interactions
- **Real-Time Archive Search:**
  - *Trigger:* Keystrokes in top global search or archive search input.
  - *Response:* Instantly filters the meeting table rows by matching title or participant names without page reloads.
- **Platform Pill Filters:**
  - *Trigger:* Clicking platform filter pills (`All`, `Google Meet`, `Zoom`, `Teams`).
  - *Response:* Active pill shifts to solid `bg-indigo-600 text-white`; meetings table instantly updates to display only matching platform records.

### 3.3 Audio Player Interactions
- **Play / Pause Toggle:**
  - *Trigger:* Clicking the 40px circular play/pause button or pressing `Spacebar`.
  - *Response:* Audio toggles playback; icon morphs between `Play` and `Pause`; elapsed timer increments in real time.
- **Timeline Scrubbing:**
  - *Trigger:* Clicking or dragging anywhere along the audio progress scrubber.
  - *Response:* Seeks audio playback to the clicked percentage; updates the active transcript sentence highlight.
- **Speed Toggle:**
  - *Trigger:* Clicking the speed pill (`0.75x`, `1.0x`, `1.25x`, `1.5x`).
  - *Response:* Cycles sequentially through speeds; audio playback rate changes immediately.

### 3.4 Language Coaching Interactions
- **Mistake Inspector Expansion:**
  - *Trigger:* Clicking an error span in the transcript or clicking a `GrammarErrorCard`.
  - *Response:* Reveals the side-by-side comparison ("What you said" vs. "Better alternative"), linguistic rule explanation, and audio clip playback trigger.
- **Add to Practice Deck Toggle:**
  - *Trigger:* Clicking `"Add to Practice"` on any grammar mistake card.
  - *Response:* Button morphs to `"In Practice Deck"` with a green checkmark (`Check`); mistake ID is saved to the user's personal flashcard deck in `/learning-center/mistakes`.

### 3.5 Modal & Overlay Interactions
- **Focus Trapping:** When a modal or confirmation dialog opens, focus is constrained within the dialog. Tab navigation cycles only through dialog buttons.
- **Escape Key Dismissal:** Pressing `Escape` or clicking the semi-transparent backdrop closes the modal without saving uncommitted changes.
- **Destructive Confirmation:** Purging data requires confirming inside a secondary dialog with a red destructive action button.

