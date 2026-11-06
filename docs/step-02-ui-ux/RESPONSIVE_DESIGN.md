# Responsive Design & Multi-Device Specification

**Product Name:** AI Meeting English Coach  
**Document ID:** RESPONSIVE-SPEC-V1.0  
**Phase:** Step 02  
**Status:** Approved Multi-Device Baseline  

---

## 1. Breakpoint Architecture & Matrix

The user interface implements an adaptive layout system supporting viewports from 320px smartphones to 1600px+ ultra-wide desktop monitors:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Responsive Breakpoint Matrix                          │
├─────────────────┬───────────┬──────────────┬──────────────┬─────────────────┤
│ Viewport Tier   │ Width     │ Sidebar      │ Content Grid │ Audio Player    │
├─────────────────┼───────────┼──────────────┼──────────────┼─────────────────┤
│ Small Mobile    │ 320px     │ Drawer Menu  │ 1-Col Stack  │ Compact Dock    │
│ Mobile          │ 375px     │ Drawer Menu  │ 1-Col Stack  │ Compact Dock    │
│ Large Mobile    │ 430px     │ Drawer Menu  │ 1-Col Stack  │ Compact Dock    │
│ Tablet          │ 768px     │ 64px Icon    │ 2-Col Grid   │ Floating Bar    │
│ Small Desktop   │ 1024px    │ 240px Fixed  │ 3-Col Grid   │ Synced Split    │
│ Desktop         │ 1280px    │ 240px Fixed  │ 4-Col Grid   │ Synced Split    │
│ Large Desktop   │ 1440px    │ 240px Fixed  │ 4-Col Grid   │ 3-Pane Workspace│
│ Wide Desktop    │ 1600px+   │ 240px Fixed  │ Max-W 1600px │ 3-Pane Workspace│
└─────────────────┴───────────┴──────────────┴──────────────┴─────────────────┘
```

---

## 2. Layout Adaptations by Device Tier

### 2.1 Mobile Viewports (320px – 430px)
- **Navigation:** The left sidebar is removed from the DOM document flow and converted into an accessible slide-over drawer triggered by the topbar hamburger menu (`Menu`).
- **Dashboard Overview:** KPI stat cards stack into a single column (`grid-cols-1`). Secondary charts collapse into swipeable cards.
- **Data Tables:** Tables gain horizontal scrolling with sticky primary column headers, or collapse into compact card stacks.
- **Audio Player:** Fixed to the bottom viewport with minimal padding and simplified controls (Play/Pause, scrub slider, and current time).

### 2.2 Tablet Viewports (768px – 1023px)
- **Navigation:** Sidebar collapses to an unobtrusive 64px icon rail. Text labels are hidden; hover tooltips provide navigation labels.
- **Grid Layouts:** 4-column KPI rows transition into an even 2x2 grid (`grid-cols-2`).
- **Transcript Viewer:** The 3-pane transcript converts into a 2-pane view (Transcript on left, collapsible drawer for mistake inspector).

### 2.3 Desktop & Ultra-Wide Viewports (1024px – 1600px+)
- **Navigation:** Permanent 240px sidebar with full hierarchical navigation groups and organization context.
- **Three-Pane Workspace:**
  - Pane 1 (220px): Speaker list and speaking share metrics.
  - Pane 2 (Flexible): Chronological transcript feed with audio seek sync.
  - Pane 3 (320px): Mistake inspector with deep linguistic explanations and native audio comparisons.
- **Container Constancy:** Max container width capped at 1600px to prevent visual dispersion on ultra-wide 4K monitors.

---

## 3. Responsive Quality Validation Checklist

Every primary page has been validated across all standard device widths:

- [x] **320px (iPhone SE):** Zero horizontal overflow on the window body. Text wraps gracefully; touch targets maintain minimum 40x40px hit areas.
- [x] **375px (iPhone 13 mini):** Clean single-column layout with legible typography.
- [x] **430px (iPhone 14 Pro Max):** Optimal mobile card margins and balanced button padding.
- [x] **768px (iPad Mini / Portrait):** Two-column stat grid renders without overlapping numbers.
- [x] **1024px (iPad Pro / Small Laptop):** Collapsible sidebar functions smoothly; charts display complete horizontal axes.
- [x] **1280px (Standard Desktop):** Full 4-column KPI cards render without abbreviation.
- [x] **1440px (MacBook Pro / Monitor):** Three-pane transcript workspace displays all columns simultaneously without horizontal scrolling.

