# Spacing, Radius, Shadows & Layout System

**Product Name:** AI Meeting English Coach  
**Document ID:** LAYOUT-SYS-V1.0  
**Phase:** Step 02  
**Status:** Approved Layout Architecture  

---

## 1. 4px Base Spacing Scale

The entire spatial rhythm of the interface is governed by a strict 4px geometric increment:

```
┌─────────────────────────────────────────────────────────────┐
│                       4px Spacing Scale                     │
├────────────┬─────────────┬──────────────────────────────────┤
│ Token      │ Pixel Value │ Usage                            │
├────────────┼─────────────┼──────────────────────────────────┤
│ space-1    │ 4px         │ Micro gaps between icons & text  │
│ space-2    │ 8px         │ Input inner padding, badge gap   │
│ space-3    │ 12px        │ Button padding, small card gap   │
│ space-4    │ 16px        │ Standard container gap           │
│ space-5    │ 20px        │ Form group spacing               │
│ space-6    │ 24px        │ Standard Card Padding (Default)  │
│ space-8    │ 32px        │ Major section vertical spacing   │
│ space-10   │ 40px        │ Dashboard section dividers       │
│ space-12   │ 48px        │ Page header bottom margins       │
│ space-16   │ 64px        │ Global topbar height             │
└────────────┴─────────────┴──────────────────────────────────┘
```

---

## 2. Border Radius Scale

Border radii establish smooth visual contours while preserving crisp, professional edges:

- `radius-xs` (4px): Checkboxes, micro tooltips, small status chips.
- `radius-sm` (6px): Compact buttons, table action triggers.
- `radius-md` (8px): Form input fields, standard primary/secondary buttons, dropdown menus.
- `radius-lg` (12px): Standard cards, audio player enclosure, modal dialog corners.
- `radius-xl` (16px): Feature panels, side panel frame containers.
- `radius-2xl` (20px): Large onboarding callouts.
- `radius-full` (9999px): User avatars, status pills, circular play/pause buttons.

---

## 3. Shadows & Elevation System

Shadows define depth and z-index hierarchy without creating muddy visual artifacts:

- **Shadow XS:** `0 1px 2px 0 rgba(0, 0, 0, 0.05)` — Subtle input field resting state.
- **Shadow SM:** `0 1px 3px 0 rgba(0, 0, 0, 0.1)` — Standard cards, stat tiles.
- **Shadow MD:** `0 4px 6px -1px rgba(0, 0, 0, 0.1)` — Audio player, floating menus, popovers.
- **Shadow LG:** `0 10px 15px -3px rgba(0, 0, 0, 0.1)` — Modal dialogs, dropdown panels.
- **Shadow XL:** `0 20px 25px -5px rgba(0, 0, 0, 0.1)` — Heavy confirmation dialogs.
- **Dark Mode Shadows:** Uses increased opacity (`rgba(0, 0, 0, 0.6)`) to ensure separation against `#111827` surfaces.

---

## 4. Application Shell Layouts

### 4.1 Web Dashboard Shell
- **Topbar:** Fixed 64px height (`h-16`). Houses Org Switcher, Global Search, Theme Switcher, and User Profile.
- **Sidebar:** Fixed 240px width (`w-60` to `w-64`), collapsible to 64px icon-only rail on tablet viewports.
- **Content Area:** Flexible width up to 1600px max-width, with 24px (`p-6` to `p-8`) padding.

### 4.2 Chrome Extension Side Panel Shell
- **Width:** Locked to 360px – 400px (100% responsive down to 320px).
- **Height:** 100% browser viewport height (`h-screen` or `h-[640px]` in simulator).
- **Header & Footer:** Persistent top status bar and bottom connection indicator; scrollable central session area.

### 4.3 Super Admin Shell
- **Sidebar:** Dark slate (`bg-slate-950`) 240px navigation rail with red operational badges.
- **Main Deck:** High-density data tables and live infrastructure health meters.

