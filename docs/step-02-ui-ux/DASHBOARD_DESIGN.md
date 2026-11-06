# Web Dashboard High-Fidelity Design Specifications

**Product Name:** AI Meeting English Coach  
**Document ID:** DASHBOARD-DESIGN-V1.0  
**Phase:** Step 02  
**Implemented Screens:** 21 / 21 Screens (100%)  
**Status:** Approved Web Dashboard Baseline  

---

## 1. Overview & Navigation Architecture

The Web Dashboard serves as the central platform hub for review, skill benchmarking, and continuous micro-learning. It is structured into five cohesive navigation groups:

```
┌─────────────────────────────────────────────────────────────┐
│                   Web Dashboard Screen Map                  │
├─────────────────┬───────────────────────────────────────────┤
│ Workspace       │ 01. Overview, 02. All Meetings,           │
│                 │ 03. Meeting Details, 04. Transcript Viewer│
├─────────────────┼───────────────────────────────────────────┤
│ My English      │ 05. Individual Report, 06. My Performance,│
│                 │ 07. Grammar, 08. Vocabulary, 09. Fluency, │
│                 │ 10. Pronunciation, 11. IELTS Practice     │
├─────────────────┼───────────────────────────────────────────┤
│ Learning        │ 12. Learning Center, 13. Mistake History, │
│                 │ 14. Improvement Plan                      │
├─────────────────┼───────────────────────────────────────────┤
│ Organization    │ 15. Team Analytics                        │
├─────────────────┼───────────────────────────────────────────┤
│ System/Settings │ 16. Integrations, 17. Billing & Usage,    │
│                 │ 18. Profile, 19. Privacy, 20. Security,   │
│                 │ 21. Notifications                         │
└─────────────────┴───────────────────────────────────────────┘
```

---

## 2. Page-by-Page High-Fidelity Specifications

### Screen 01: Dashboard Overview (`/` or `/dashboard`)
- **Objective:** Instantaneous orientation on recent meeting activity and spoken English mastery.
- **UI Sections:**
  - Personalized Greeting Header with date and quick action triggers.
  - 4 KPI Stat Cards: Total Meetings Analyzed (24), Total Speaking Time (4h 32m), Average English Score (81/100, C1), and Resolved Mistakes (18).
  - Multi-line Linguistic Performance Trajectory Chart with 30-day time filters.
  - Top Improvement Focus card highlighting Prepositions, Conditionals, and Filler words.
  - Recent Meetings Table with direct links to transcripts and coaching reports.

### Screen 02: All Meetings Archive (`/meetings`)
- **Objective:** Comprehensive searchable archive of all past browser meeting calls.
- **UI Sections:**
  - Filter bar supporting text search, platform filtering (`All`, `Google Meet`, `Zoom`, `Teams`), and status filters.
  - Data table displaying meeting title, platform pill, date, duration, participant avatar stack, score badge, and quick action buttons.

### Screen 03: Meeting Details (`/meetings/:id`)
- **Objective:** Executive summary and participation analysis for a specific meeting session.
- **UI Sections:**
  - Header with title, date, duration, and one-click report triggers.
  - Tabbed interface: `Overview` (Executive 3-bullet summary and speaking share distribution bars), `Participants` (Diarization confidence and role roster), and `Analysis` (Direct mistake cards).

### Screen 04: Interactive Transcript Viewer (`/meetings/:id/transcript`)
- **Objective:** Full three-pane audio-synced exploration of the meeting dialogue.
- **UI Sections:**
  - Left Pane (220px): Speaker list with speaking share percentages.
  - Center Pane: Chronological transcript feed with speaker avatar pills, timestamp links, and wavy mistake underlines.
  - Right Pane (320px): Mistake Inspector Drawer showing side-by-side original vs. native rephrase and grammar rules.
  - Sticky Bottom Audio Player: Interactive timeline scrubber, skip buttons, and speed controls synced bidirectionally with transcript speech.

### Screen 05: Individual English Report (`/meetings/:id/report/:participantId`)
- **Objective:** In-depth, evidence-backed evaluation of a specific speaker's language proficiency.
- **UI Sections:**
  - 4 Score Dials: Grammar (84), Vocabulary (82), Fluency (78), Pronunciation (80).
  - Detailed Mistake Breakdown: Filterable `GrammarErrorCard` components showing original sentence, native alternative, rule explanation, audio clip playback trigger, and "Add to Practice Deck" toggle.
  - Executive Vocabulary Upgrades grid replacing informal colloquial phrases with polished business phrasing.

### Screen 06: My Performance (`/my-performance`)
- **Objective:** Longitudinal 30/60/90-day trajectory tracking across multiple meetings.
- **UI Sections:**
  - Multi-metric trend charts tracking grammar error reduction and vocabulary expansion over time.
  - Resolved vs. Recurring Mistakes progress indicators.

### Screen 07: Grammar Analysis Engine (`/my-performance/grammar`)
- **Objective:** Dedicated diagnostic view of all grammatical patterns (Prepositions, Conditionals, Subject-Verb Agreement, and Tense Shifts).

### Screen 08: Vocabulary Precision (`/my-performance/vocabulary`)
- **Objective:** Lexical richness analysis, overused repetitive modifier detection, and domain-specific terminology recommendations.

### Screen 09: Fluency & Rhythm (`/my-performance/fluency`)
- **Objective:** Quantitative dynamics: Words Per Minute (WPM) gauge, pause duration histograms, and filler disfluency density ("um", "actually").

### Screen 10: Pronunciation Clarity (`/my-performance/pronunciation`)
- **Objective:** Acoustic spectrogram evaluation, phonetic IPA notations, word syllable stress guidance, and accent neutrality guarantees.

### Screen 11: IELTS-Style Practice (`/ielts-practice`)
- **Objective:** Benchmarking real meeting speech against IELTS Speaking Band criteria (0.0 to 9.0).
- **UI Sections:**
  - High-visibility regulatory disclaimer banner.
  - Large band score dial (e.g., `Band 7.5 — Good User`).
  - 4 Criteria Cards: Fluency & Coherence (7.5), Lexical Resource (7.0), Grammatical Range (7.5), Pronunciation (8.0).

### Screen 12: Personalized Learning Center (`/learning-center`)
- **Objective:** Daily 3-minute adaptive practice challenges generated dynamically from past meeting errors.
- **UI Sections:**
  - Streak widget (7 Days 🔥).
  - Interactive multiple-choice drill cards with instant answer feedback and grammar rule explanations.

### Screen 13: Mistake History (`/learning-center/mistakes`)
- **Objective:** Personal flashcard deck of saved phrases from meeting reports with filterable mastery tags.

### Screen 14: 4-Week Improvement Plan (`/learning-center/plan`)
- **Objective:** Milestone roadmap guiding the user through targeted weekly focus areas.

### Screen 15: Team Communication Analytics (`/team-analytics`)
- **Objective:** Privacy-preserved, aggregate communication benchmarks for Team Managers.
- **UI Sections:**
  - Team meeting hours, average team pacing (142 WPM), and team filler word rate (3.8%).
  - Horizontal distribution chart of widespread team linguistic bottlenecks.
  - Anonymized member comparison table.

### Screen 16: Integrations (`/integrations`)
- **Objective:** Connection management with Chrome Extension, Google Meet, Zoom Web, and Microsoft Teams.

### Screen 17: Billing & Multi-Dimensional Usage (`/billing`)
- **Objective:** Subscription plan management, provisioned seat counts, meeting minute meters, and AI token capacity meters.

### Screen 18: Profile Settings (`/settings/profile`)
- **Objective:** User credentials, profile avatar, and primary native language calibration.

### Screen 19: Privacy & Audio Retention (`/settings/privacy`)
- **Objective:** Ephemeral vs. 7-day vs. 30-day audio retention selectors and GDPR account data erasure modal.

### Screen 20: Security Settings (`/settings/security`)
- **Objective:** Active browser sessions, Chrome extension token revocation, and password management.

### Screen 21: Notification Settings (`/settings/notifications`)
- **Objective:** Post-meeting email report triggers and daily practice push reminder toggles.

