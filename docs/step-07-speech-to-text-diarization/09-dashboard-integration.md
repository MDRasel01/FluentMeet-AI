# Step 07 — Dashboard Frontend Integration (Next.js)

## 1. Feature Architecture
The transcript UI resides in `apps/dashboard/src/features/transcripts/` and integrates directly into the FluentMeet meeting session views.

```
apps/dashboard/src/features/transcripts/
├── types.ts                         # UI interfaces & data transfer types
├── useTranscriptFeed.ts             # Custom hook managing WebSocket & REST feed
├── TranscriptTimeline.tsx           # Interactive chronological transcript view
├── SpeakerManagerModal.tsx          # Modal to rename and identify speakers
├── TranscriptSegmentEditModal.tsx   # Modal for manual human text corrections
└── index.ts                         # Public feature barrel export
```

## 2. Key UI Capabilities

### 2.1 Real-Time Streaming & Auto-Scroll
- `useTranscriptFeed` opens an authenticated WebSocket connection upon meeting load.
- Streaming partial predictions are rendered in a distinct pulse-animated badge at the bottom of the feed.
- Intelligent auto-scroll detects user scroll position: if the user scrolls up to read past statements, auto-scroll pauses to prevent disrupting their reading flow.

### 2.2 Word-Level Confidence Highlighting
- Words with confidence scores below $0.65$ render with an amber dotted underline.
- Hovering reveals the calibrated confidence percentage tooltip, signaling to the user and coach that acoustic ambiguity occurred.

### 2.3 Conversational Overlap Warnings
- When `speaker.overlap` events are received, the timeline surfaces an alert badge displaying the count of cross-talk collisions.

### 2.4 Human-in-the-Loop Corrections
- Hovering over any utterance reveals an edit icon (`Edit3`).
- Clicking launches `TranscriptSegmentEditModal`, allowing instant correction of typos or speaker reattribution.
- Updates are saved optimistically and broadcast to all connected dashboard and extension clients.
