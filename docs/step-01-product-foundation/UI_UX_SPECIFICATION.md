# UI/UX Specification & Global Architecture

**Product Name:** AI Meeting English Coach  
**Document ID:** SPEC-UIUX-V1.0  
**Status:** Approved UI/UX Design Directive  
**Version:** 1.0.0  

---

## 1. Design Philosophy & Inspiration

The design language of **AI Meeting English Coach** reflects the calm, precise, and high-utility aesthetic of modern enterprise developer tools and financial software.

### 1.1 Core References
- **Linear:** Utilitarian speed, high information density without clutter, precise keyboard navigation, muted border-defined elevation.
- **Stripe Dashboard:** Crystal-clear data typography, robust tabular data presentation, sophisticated multi-state forms, and accessible contrast.
- **Notion:** Focused readability, clean typography hierarchy, non-intrusive metadata presentation.
- **Vercel Dashboard:** Monochromatic discipline accented with purposeful, high-contrast semantic color coding.

### 1.2 Design Tenets
1. **Calm Precision:** Language coaching can trigger user anxiety. The UI must avoid alarmist red alerts for minor grammatical flaws; corrections must feel constructive, scientific, and encouraging.
2. **Zero Mock/Fake Metrics:** When a user is new or data is insufficient, display clean, educational Empty States. Never invent synthetic scores or placeholder numbers.
3. **Synchronized Modalities:** Text transcripts and audio audio playback must be deeply linked. Selecting text immediately seeks audio; audio playback highlights the corresponding spoken text segment in real time.
4. **Information Density with Breathability:** Use standard 8px grid spacing and compact font scales to maximize desktop screen real estate without overwhelming the eye.

---

## 2. Global Application Shell & Layout System

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ Top Bar: Org Switcher │ Global Search (Cmd+K) │ Notifications │ User Avatar     │
├───────────────┬──────────────────────────────────────────────────────────────────┤
│ Sidebar       │ Breadcrumbs / Page Header                                        │
│ (240px)       ├──────────────────────────────────────────────────────────────────┤
│               │ Main Content Container                                           │
│ • Overview    │ (Max Width: 1600px, 24px Padding)                                │
│ • Meetings    │                                                                  │
│ • My English  │   ┌──────────────────────────┐   ┌──────────────────────────┐   │
│ • Learning    │   │ KPI Metric Card          │   │ Interactive Chart Card   │   │
│ • Team        │   └──────────────────────────┘   └──────────────────────────┘   │
│ • Settings    │                                                                  │
│               │   ┌──────────────────────────────────────────────────────────┐   │
│ ───────────── │   │ Data Table / Audio-Synced Transcript Viewer              │   │
│ [Collapse <]  │   └──────────────────────────────────────────────────────────┘   │
└───────────────┴──────────────────────────────────────────────────────────────────┘
```

### 2.1 Sidebar Navigation Specifications
- **Width:** 240px (Expanded), 64px (Collapsed icon-only mode).
- **Behavior:** Fixed positioning on desktop; slide-out drawer on mobile/tablet viewports (< 1024px).
- **Navigation Groups:**
  1. **Main:** Overview (`/`), Meetings (`/meetings`), Meeting Reports (`/meetings/reports`), Transcripts (`/meetings/transcripts`).
  2. **My English:** My Performance (`/my-performance`), Grammar (`/my-performance/grammar`), Vocabulary (`/my-performance/vocabulary`), Fluency (`/my-performance/fluency`), Pronunciation (`/my-performance/pronunciation`), IELTS Practice (`/ielts-practice`).
  3. **Learning:** Learning Center (`/learning-center`), Mistake History (`/learning-center/mistakes`), Daily Practice (`/learning-center/practice`).
  4. **Organization (Role-Gated):** Team Analytics (`/team-analytics`), Member Performance (`/team-analytics/members`).
  5. **System:** Integrations (`/integrations`), Billing & Usage (`/billing`), Settings (`/settings`).

### 2.2 Top Navigation Bar Specifications
- **Height:** 64px fixed.
- **Elements:**
  - **Organization Switcher:** Dropdown displaying current tenant with avatar badge and team switcher.
  - **Global Quick Search:** Keyboard trigger (`Cmd+K` / `Ctrl+K`) searching meetings, transcripts, and vocabulary terms.
  - **Notification Center:** Bell icon with unread badge indicating when background meeting analysis completes.
  - **User Profile Menu:** Quick access to Profile Settings, Theme Toggle (Light/Dark/System), and Sign Out.

---

## 3. Responsive Breakpoint Matrix

The application follows a mobile-first, desktop-optimized responsive grid built with Tailwind CSS:

| Breakpoint | Viewport Width | Sidebar Behavior | Content Grid | Audio Player Layout |
|---|---|---|---|---|
| **Mobile (`sm`)** | 320px – 767px | Hidden in slide-over drawer | 1-column stacked cards | Fixed bottom compact dock |
| **Tablet (`md`)** | 768px – 1023px | Collapsed to 64px icon rail | 2-column grid | Sticky bottom bar |
| **Desktop (`lg`)** | 1024px – 1439px| Expanded 240px fixed | 3-column / Multi-card grid | Synced side-by-side split |
| **Ultra-Wide (`xl`/`2xl`)**| $\ge$ 1440px | Expanded 240px fixed | 4-column KPI / 3-pane transcript | 3-pane (Speakers / Text / AI) |

---

## 4. Universal UI State Contract

Every screen, page section, and reusable card in the application must strictly account for the following four fundamental states:

```
┌─────────────────────────────────────────────────────────────┐
│                    Universal State Contract                 │
├─────────────────┬───────────────────────────────────────────┤
│ 1. Loading      │ Shimmer Skeletons matching exact layout.  │
│                 │ Never use blocking full-page spinners.    │
├─────────────────┼───────────────────────────────────────────┤
│ 2. Empty        │ Educational graphic, context description, │
│                 │ and prominent primary CTA. No fake data!  │
├─────────────────┼───────────────────────────────────────────┤
│ 3. Error        │ Inline alert banner with human-readable   │
│                 │ cause, error code, and "Retry" action.    │
├─────────────────┼───────────────────────────────────────────┤
│ 4. Success / Pop│ Data loaded with subtle 150ms fade-in.    │
│                 │ Stale-while-revalidate cache updates.     │
└─────────────────┴───────────────────────────────────────────┘
```

---

## 5. Accessibility (a11y) & WCAG 2.1 AA Compliance Standards

1. **Color Contrast Ratios:**
   - Text vs. Background: Minimum **4.5:1** for regular body text; **3:1** for large headings ($\ge$ 20px bold).
   - Interactive UI Elements (Buttons, Inputs, Focus Rings): Minimum **3:1** against adjacent backgrounds.
2. **Keyboard Navigation & Focus Management:**
   - Logical tab index flow across all interactive elements (`Tab` / `Shift+Tab`).
   - Visible, high-contrast focus rings: `focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2`.
   - Modals and drawers trap focus when open and restore focus to trigger buttons upon dismissal (`Escape` key closes).
3. **Screen Reader Optimization:**
   - ARIA landmarks (`nav`, `main`, `aside`, `header`, `role="region"`).
   - Audio play/pause controls, transcript segments, and score dials carry descriptive `aria-label` tags (e.g., `aria-label="Play spoken segment at 14 minutes 22 seconds"`).
4. **Motion Safety:**
   - Honor `prefers-reduced-motion: reduce` by disabling non-essential transitions and animations.

