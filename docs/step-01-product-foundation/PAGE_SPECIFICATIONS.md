# Web Dashboard — Complete Page Specifications

**Product Name:** AI Meeting English Coach  
**Document ID:** SPEC-PAGES-V1.0  
**Status:** Approved Page-by-Page Specifications  
**Version:** 1.0.0  

---

## 1. Overview of Web Dashboard Architecture

The Web Dashboard comprises 12 primary pages. Each page adheres to the universal design tokens, layout hierarchy, and state contracts defined in `UI_UX_SPECIFICATION.md` and `DESIGN_SYSTEM.md`.

---

## Page 01 — Dashboard Overview

- **Route:** `/` or `/dashboard`
- **Purpose:** Immediate snapshot of recent meeting activity, overall spoken English health, and daily learning actions upon logging in.
- **Target Roles:** Individual User, Team Member, Team Manager, Org Admin.

### Layout & UI Sections
1. **Welcome Header:**
   - Personalized greeting: `"Good morning, {User.firstName}"`.
   - Current date formatted (`e.g., Thursday, Nov 6, 2026`).
   - Quick CTAs: `"Install Extension"` (if not paired) + `"View All Meetings"`.
2. **KPI Stat Cards (4-Column Grid):**
   - **Card 1: Total Meetings Analyzed** (e.g., `24 meetings`, `+4 this month`).
   - **Card 2: Total Speaking Time** (e.g., `4h 32m`, formatted in hours/mins).
   - **Card 3: Average English Score** (e.g., `81/100`, trend badge `+3.2% vs last 30d`).
   - **Card 4: Mastery Progress** (e.g., `18 mistakes resolved in practice`).
3. **English Performance Trend (Chart Card):**
   - Multi-line chart (Recharts/SVG) tracking Grammar, Vocabulary, Fluency, and Pronunciation over selectable timeframes (`7D`, `30D`, `90D`, `Custom`).
4. **Recent Meetings Table:**
   - Columns: Meeting Title, Platform Icon (Meet/Zoom/Teams), Date/Time, Duration, My Speaking Time, Overall Score, Action (`View Report`).
5. **Top Improvement Areas Card:**
   - Displays top 3 recurring linguistic issues (e.g., Preposition usage, Past tense consistency, Filler words).
6. **Recommended Daily Practice Card:**
   - One-click CTA: `"Start Today's 3-Minute Drill"` based on recent meeting errors.

### State Specifications
- **Loading:** Shimmer skeletons for 4 KPI cards, chart placeholder skeleton, and 4 table row skeletons.
- **Empty State (New User):**
  - **No Fake Data Allowed!**
  - Displays welcome illustration, copy: *"No meetings recorded yet. Pair your Chrome Extension and join your next Google Meet to receive your first English report."*
  - Primary Button: `"Download Chrome Extension"` | Secondary Link: `"Watch 1-Minute Demo"`.
- **Error State:** Banner with message *"Failed to load dashboard metrics. [Retry Connection]"*.

---

## Page 02 — All Meetings

- **Route:** `/meetings`
- **Purpose:** Comprehensive searchable, filterable archive of all recorded meeting sessions.
- **Target Roles:** All authenticated users.

### Layout & UI Sections
1. **Header & Control Bar:**
   - Title: `"Meetings Archive"` with counter badge (`Total: 48`).
   - Search input: Real-time search across meeting title and participant names.
   - Filters: Date Range Picker, Platform Filter (`All`, `Google Meet`, `Zoom`, `Teams`), Analysis Status Filter (`All`, `Completed`, `Processing`, `Failed`).
   - Action Button: `"Export CSV Summary"`.
2. **Meetings Data Table:**
   - Columns: Title & Platform Icon, Date & Time, Duration, Discovered Participants (Avatar stack), Analysis Status (Badge: Green `Completed`, Amber `Processing`, Red `Failed`), Actions Menu (`...`).
   - Actions Dropdown: `"View Details"`, `"View Transcript"`, `"View My Report"`, `"Delete Session"`.
3. **Pagination Bar:**
   - Items per page selector (`10`, `25`, `50`), page count indicator, Prev/Next pagination buttons.

### State Specifications
- **Empty State:** Graphic showing a calendar with copy *"No meetings match your search filter."* Button: `"Clear All Filters"`.

---

## Page 03 — Meeting Details

- **Route:** `/meetings/[id]`
- **Purpose:** Holistic breakdown of a specific meeting session: participants, speaking shares, executive summary, and access to reports.
- **Target Roles:** Session participants, Organization Admins.

### Layout & UI Sections
1. **Meeting Header:**
   - Meeting Title, Platform badge, Date/Time, Total Duration, Recorded by.
   - Processing Status Pill with live updates if processing.
2. **Navigation Tabs:**
   - `Overview` | `Transcript` | `Participants` | `English Analysis` | `Full Report`.
3. **Overview Tab Content:**
   - **Executive Summary Box:** AI-generated 3-bullet summary of topics discussed.
   - **Speaking Time Distribution Chart:** Donut chart showing percentage of time spoken by each participant.
   - **Participant Roster Cards:** List of participants with detected names, speaking durations, and links to their individual reports (if authorized).

---

## Page 04 — Interactive Transcript Viewer

- **Route:** `/meetings/[id]/transcript`
- **Purpose:** Synchronized audio-text exploration of the entire meeting dialogue with speaker isolation and mistake highlighting.
- **Target Roles:** All session participants.

### Layout & UI Sections
1. **Top Control Bar:**
   - Search transcript input with match counters (`3 of 12`).
   - Speaker filter dropdown (`All Speakers`, `Priya S.`, `Alex M.`, `Unknown Speaker`).
   - Mistake Toggle Filter: Checkboxes to highlight `Grammar`, `Vocabulary`, or `Pronunciation`.
2. **Three-Pane Layout (Desktop):**
   - **Left Pane (220px):** Speaker List with speaking time percentages and color-coded avatar pills.
   - **Center Pane (Flexible):** Chronological transcript feed. Each segment displays Speaker Name, Timestamp, Spoken Text, and interactive wavy underlines for linguistic mistakes.
   - **Right Pane (320px Collapsible):** Inspector Drawer. Clicking any wavy mistake in the transcript reveals the detailed explanation, corrected phrase, and "Practice" button.
3. **Sticky Bottom Audio Player:**
   - Persistent waveform player synced with transcript text. Scrubbing updates the active segment in real time.

---

## Page 05 — Individual English Report

- **Route:** `/meetings/[id]/report/[participantId]`
- **Purpose:** The core product value page: granular, evidence-backed evaluation of a specific speaker's English performance during the meeting.
- **Target Roles:** The individual speaker (Full private report); Team Manager (Summary metrics if permitted).

### Layout & UI Sections
1. **Report Header:**
   - Speaker Avatar, Name, Meeting Title, Date, Total Speaking Time (`14 mins 20 secs`).
   - Overall Spoken English Score Dial (0–100) with performance badge (`Proficient / C1 Equivalent`).
2. **Core Dimension Score Cards (4 Cards):**
   - **Grammar Accuracy** (e.g., `84/100`, 5 mistakes detected).
   - **Vocabulary Range** (e.g., `78/100`, 8 repetitive phrases, 3 professional upgrades).
   - **Fluency & Pacing** (e.g., `148 WPM`, 12 filler words, 3.2% filler ratio).
   - **Pronunciation & Clarity** (e.g., `82/100`, 2 phoneme hesitations).
3. **Detailed Mistake Breakdown Tabs:**
   - **Grammar Tab:** Card per mistake showing:
     - Spoken Sentence with highlighted error.
     - Recommended Native Alternative.
     - Rule Explanation & Mistake Category (e.g., "Preposition Error").
     - Audio Excerpt Playback Button (`[Play Clip 00:12:45]`).
     - Action: `"Add to Practice Deck"`.
   - **Vocabulary Tab:** Suggestions to elevate common expressions to executive English.
   - **Fluency Tab:** Graph of speaking pacing over time, filler word breakdown ("um", "like", "you know").
   - **Pronunciation Tab:** Target words, IPA phonetic transcriptions, detected distortion, and audio guide.

---

## Page 06 — My Performance (Long-Term Tracking)

- **Route:** `/my-performance`
- **Purpose:** Longitudinal self-improvement analytics tracking linguistic trajectory across weeks and months.
- **Target Roles:** Individual Users, Team Members.

### Layout & UI Sections
1. **Performance Timeline Filters:** `Last 30 Days`, `Last 90 Days`, `Past Year`, `All Time`.
2. **Overall Trajectory Chart:** Area chart showing overall English score progression compared to total meeting hours.
3. **Four Dimension Trend Breakdown:** Comparative multi-metric charts for Grammar, Vocabulary, Fluency, and Pronunciation.
4. **Resolved vs. Recurring Mistakes Matrix:**
   - Progress bar showing mistakes eliminated (e.g., *"Past tense consistency improved by 40%"*).
   - List of persistent weaknesses requiring focused practice.

---

## Page 07 — Learning Center

- **Route:** `/learning-center`
- **Purpose:** Gamified, personalized micro-learning drills generated dynamically from real meeting errors.
- **Target Roles:** Individual Users, Team Members.

### Layout & UI Sections
1. **Daily Streak & Progress Widget:**
   - Current Streak (`7 Days`), Total Drills Mastered (`42`), Minutes Practiced (`128m`).
2. **Today's Recommended Drills (3 Modules):**
   - **Module 1:** Fix Meeting Mistakes (Interactive sentence rephrasing).
   - **Module 2:** Professional Vocabulary Match (Multiple-choice business phrasing).
   - **Module 3:** Fluency & Filler Reduction (Speaking prompt with live audio pacing feedback).
3. **Saved Mistake Deck:**
   - Personal flashcard deck of phrases saved from past meeting reports.

---

## Page 08 — IELTS Practice & Benchmarking

- **Route:** `/ielts-practice`
- **Purpose:** Formats real meeting performance into estimated IELTS Speaking Band Scores (0.0–9.0).
- **Target Roles:** Users seeking standardized academic or professional English benchmarks.

### Layout & UI Sections
1. **Regulatory Disclaimer Banner:**
   - High-contrast info alert: *"This assessment is an AI-assisted estimate designed for self-study and is not an official IELTS™ score."*
2. **Overall Estimated Band Score:**
   - Large dial displaying estimated band (e.g., `Band 7.5 — Good User`).
3. **Four IELTS Criteria Cards:**
   - **Fluency & Coherence:** Band 7.5 with specific rationale and evidence.
   - **Lexical Resource:** Band 7.0 with academic vocabulary ratio.
   - **Grammatical Range & Accuracy:** Band 7.5 with complex sentence ratio.
   - **Pronunciation:** Band 8.0 with clarity and intonation assessment.

---

## Page 09 — Team Analytics

- **Route:** `/team-analytics`
- **Purpose:** Scoped communication insights for Team Managers and Organization Admins.
- **Target Roles:** Team Manager (Assigned Teams), Organization Admin (Entire Org).

### Layout & UI Sections
1. **Team Selector & Date Filter:** Dropdown to switch between departments/teams.
2. **Team Communication Health KPIs:**
   - Team Meeting Hours Analyzed, Average Team Pacing (WPM), Team Filler Density %, Most Frequent Team Mistake Category.
3. **Team Mistake Distribution Chart:** Horizontal bar chart highlighting systemic communication weaknesses (e.g., 34% of team mistakes involve conditional tenses).
4. **Anonymized Member Performance Distribution:**
   - Gaussian or bar distribution showing team cohort scores without exposing private individual names (preserving psychological safety).

---

## Page 10 — Integrations

- **Route:** `/integrations`
- **Purpose:** Manage connection status with Chrome Extension and supported web meeting platforms.
- **Target Roles:** All authenticated users.

### Layout & UI Sections
1. **Chrome Extension Card:**
   - Pairing status (Connected / Not Paired), Extension Version (`v1.0.2`), Last Sync Timestamp.
   - Actions: `"Pair Extension"`, `"Re-sync Token"`, `"Download from Chrome Store"`.
2. **Meeting Platform Integration Cards:**
   - **Google Meet Web:** Status: Active / Supported. Instructions on enabling extension on meet.google.com.
   - **Zoom Web:** Status: Compatibility Ready.
   - **Microsoft Teams Web:** Status: Compatibility Ready.

---

## Page 11 — Billing & Usage

- **Route:** `/billing`
- **Purpose:** Manage SaaS subscription, seat licenses, payment methods, and multi-dimensional usage quotas.
- **Target Roles:** Individual User (Personal tier), Organization Admin (Enterprise tier).

### Layout & UI Sections
1. **Current Plan Card:**
   - Plan Name (`Pro Tier` or `Enterprise Team - 25 Seats`), Renewal Date, Price (`$29/mo` or `$499/mo`).
   - Actions: `"Upgrade Plan"`, `"Change Payment Method"`, `"Cancel Subscription"`.
2. **Multi-Dimensional Usage Meters:**
   - **Meeting Minutes Ingested:** Progress bar (`320 / 1,000 mins used`).
   - **Audio Processing Minutes:** Progress bar (`280 / 1,000 mins`).
   - **AI Analysis Tokens:** Bar indicating tier capacity.
3. **Invoice History Table:**
   - Date, Invoice ID, Amount, Status (Paid/Pending), Download PDF receipt button.

---

## Page 12 — Settings

- **Route:** `/settings`
- **Purpose:** Account preferences, data privacy policies, audio retention settings, and security.
- **Target Roles:** All authenticated users (Scoped by role).

### Layout & UI Sections
- Sub-navigation Tabs: `Profile`, `Preferences`, `Privacy & Retention`, `Organization`, `Security`.
- **Privacy & Retention Tab (Critical):**
  - **Audio File Retention Selector:** Options (`Delete immediately after analysis`, `Store for 7 days`, `Store for 30 days`, `Keep indefinitely`).
  - **Data Export:** Button to download full user archive (Transcripts, Reports in JSON/PDF).
  - **Account Erasure:** Destructive action to permanently purge all user records and recordings.

