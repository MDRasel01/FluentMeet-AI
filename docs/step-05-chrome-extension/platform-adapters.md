# Meeting Platform Adapters & Metadata Engine
## Specification: Step 05 — Section 6 & Section 11

---

## 1. Platform Adapter Strategy

Virtual meeting platforms frequently update their DOM hierarchies and class names. FluentMeet AI protects itself against breakage using:
1. **Semantic Attribute Prioritization:** Uses `data-tid`, `data-self-name`, `data-call-ui`, and `aria-label` before falling back to obfuscated CSS classes.
2. **Graceful Fallbacks:** If participant metadata cannot be parsed from the DOM, the audio capture continues uninterrupted; participant metadata is simply marked as `unknown`.
3. **MutationObserver Teardown:** All DOM observers are strictly disconnected when navigating or closing calls to prevent memory leaks.

---

## 2. Platform Comparison Matrix

| Platform | Supported URL Patterns | Active Meeting Detection Signals | Participant Extraction Selectors | Disconnect Signals |
|---|---|---|---|---|
| **Google Meet** | `^https://meet.google.com/[a-z]{3}-[a-z]{4}-[a-z]{3}` | `[aria-label*="Leave call"]`, `[data-call-ui]`, `div[jscontroller]` | `[data-self-name]`, `div[data-participant-id]`, `span.ZjFb7c` | `[data-call-ended="true"]`, missing call bar |
| **Zoom Web Client** | `https://*.zoom.us/wc/*`, `https://*.zoom.us/j/*` | `.footer`, `.meeting-control`, `[aria-label*="Leave"]` | `.participants-item__display-name`, `.speaker-name` | `.meeting-ended`, `.leave-dialog` |
| **Microsoft Teams Web** | `teams.microsoft.com/*meet*`, `teams.live.com/meet` | `[data-tid="hangup-button"]`, `[data-tid="call-roster-button"]` | `[data-tid="roster-participant"]`, `[data-tid="calling-roster-name"]` | `[data-tid="call-ended-screen"]`, `.call-ended` |

---

## 3. Participant Metadata Schema & Ethical Boundary

### Metadata Schema
```typescript
interface ParticipantMetadata {
  participantId: string;       // Synthetic ID (e.g. gmeet-abc-0)
  meetingId: string;           // Canonical meeting code
  platform: MeetingPlatform;   // 'google-meet' | 'zoom' | 'teams'
  displayName: string;         // Cleaned name string
  platformUserId?: string;     // Platform ID if legitimately present
  isLocalUser: boolean;        // True if matches local user "(You)" / "(Me)"
  firstSeenAt: string;         // ISO timestamp
  lastSeenAt: string;          // ISO timestamp
  metadataSource: 'dom_selector' | 'mutation_observer';
  confidence: number;          // 0.0 to 1.0 confidence score
  mappingStatus: 'mapped' | 'unknown' | 'provisional';
}
```

### Ethical Boundary Mandates (Section 11)
- **Zero Guessed Diarization:** The extension NEVER attempts to identify which speaker is talking by guessing or using pseudo-acoustic heuristics on the client side.
- **Strict Role Separation:** The extension provides:
  1. The mixed remote audio stream from the tab.
  2. The isolated local microphone audio stream.
  3. The roster of detected participant names.
- The downstream SaaS backend alone possesses the heavy neural models (PyAnnote, Gemini 2.5/3.8 Flash) required for multi-speaker segmentation, cross-track cancellation, and voice-to-roster alignment.

