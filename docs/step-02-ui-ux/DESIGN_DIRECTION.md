# Design Direction & Visual Philosophy

**Product Name:** AI Meeting English Coach  
**Document ID:** DESIGN-DIR-V1.0  
**Phase:** Step 02  
**Status:** Approved Design Baseline  

---

## 1. Visual Design Concept

The visual identity of **AI Meeting English Coach** embodies the refined, utilitarian precision of world-class enterprise SaaS products. Because language coaching directly impacts professional confidence, the interface is deliberately engineered to evoke calm focus, objective clarity, and psychological safety.

### 1.1 Core Aesthetic Traits
- **Modern & Minimal:** Eliminates gratuitous visual noise, unmotivated drop shadows, and ornamental gradients.
- **Enterprise-Ready:** Designed to feel native beside GitHub, Stripe, Linear, and Vercel.
- **Data-Driven & Scientific:** Metrics are presented with high-contrast tabular numerals and clean SVG trajectories.
- **AI-Focused with Transparency:** Every linguistic correction clearly displays the exact spoken quote, acoustic evidence, and rule explanation.

---

## 2. Design Inspiration & Reference Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                      Design Precedents                      │
├─────────────────┬───────────────────────────────────────────┤
│ Linear          │ High information density, keyboard focus, │
│                 │ subtle 1px border dividers, dark elegance.│
├─────────────────┼───────────────────────────────────────────┤
│ Stripe          │ Crystal-clear typographic scales, robust  │
│                 │ tabular data, accessible semantic colors. │
├─────────────────┼───────────────────────────────────────────┤
│ Vercel          │ Monochromatic discipline accented with    │
│                 │ purposeful status highlights.             │
├─────────────────┼───────────────────────────────────────────┤
│ Notion          │ Focused reading comfort, collapsible      │
│                 │ contextual drawers, clean typography.     │
└─────────────────┴───────────────────────────────────────────┘
```

> [!NOTE]
> These products serve as benchmarks for engineering rigor and interaction polish. The UI does not copy any single product's visual identity directly, maintaining a distinct, domain-specific personality tailored to conversational audio analysis.

---

## 3. Strict Visual Hierarchy

Every page, drawer, and card adheres to a 7-tier information hierarchy:

1. **Page Title:** Establishes instantaneous orientation (`type-h1`, 30px bold).
2. **Page Description & Context:** Concise subtitle orienting the user to recent metrics (`type-body-sm`, 12px text-slate-500).
3. **Primary Action:** Unambiguous call-to-action placed in the upper-right header area.
4. **Key Metric Indicators:** High-priority stat cards (`type-display` or `type-h2` tabular metrics).
5. **Main Content Container:** Primary data table, interactive transcript feed, or performance chart.
6. **Supporting Information:** Contextual tooltips, IPA transcriptions, and evidence cards.
7. **Secondary Actions:** Export CSV, filter resets, and settings configuration.

**The 3-Second Rule:** Within 3 seconds of loading any screen, a user must effortlessly comprehend:
- Exactly where they are located.
- The single most critical metric or insight.
- What action they should execute next.

---

## 4. The Six Core Design Principles

### Principle 01 — Absolute Consistency
Buttons, form controls, typography weights, and modal interactions must behave identically across the Web Dashboard, Chrome Extension, and Admin Panel. Component duplication with ad-hoc styling is strictly prohibited.

### Principle 02 — Information Clarity Over Decoration
Visual elements must justify their utility. No decorative background blurs or complex glassmorphism that impedes text legibility. Transcripts must be as readable as an editorial document.

### Principle 03 — Data-First Hierarchy
In analytics and reports, quantitative metrics (WPM, score dials, error counts) must precede qualitative commentary. Users should grasp their progress at a glance before diving into granular mistake breakdowns.

### Principle 04 — Progressive Disclosure
Avoid cognitive overload. Meeting overviews summarize key trends; clicking a transcript segment expands the full mistake popover; clicking "Inspect" in the Admin Panel reveals deep user telemetry.

### Principle 05 — Multi-Modal Accessibility
Never rely solely on color to convey linguistic severity or system status. Red/green pills must always be accompanied by text labels, icons, or numerical indicators.

### Principle 06 — Uncompromising Trust & Transparency
Given the sensitivity of capturing workplace speech, recording states, two-party consent checkboxes, and data retention windows must be prominently surfaced. No hidden background recording or ambiguous statuses are allowed.

