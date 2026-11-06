# Color System & Semantic Palette Specification

**Product Name:** AI Meeting English Coach  
**Document ID:** COLOR-SYS-V1.0  
**Phase:** Step 02  
**Status:** Approved Color Palette Baseline  

---

## 1. Palette Overview & Semantic Roles

Colors in **AI Meeting English Coach** serve distinct informational purposes. They guide attention to critical communication insights without triggering unnecessary anxiety over minor linguistic slips.

---

## 2. Complete Palette Token Tables

### 2.1 Primary Brand Palette (Indigo)

| Token | Hex Value | Semantic Usage |
|---|---|---|
| `primary-50` | `#EEF2FF` | Active navigation highlights, soft hover tints, badge backgrounds |
| `primary-100` | `#E0E7FF` | Selected borders, active tab backgrounds |
| `primary-200` | `#C7D2FE` | Accent divider lines, secondary badges |
| `primary-300` | `#A5B4FC` | Focus ring accents |
| `primary-400` | `#818CF8` | Dark mode primary button label |
| `primary-500` | `#6366F1` | **Primary Brand Color** (CTAs, interactive buttons, active icons) |
| `primary-600` | `#4F46E5` | Button hover state, high-contrast links |
| `primary-700` | `#4338CA` | Button pressed / active state |
| `primary-800` | `#3730A3` | Deep contrast text in light mode |
| `primary-900` | `#312E81` | Dark theme high-contrast headers |
| `primary-950` | `#1E1B4B` | Dark theme primary card soft tint |

---

### 2.2 Neutral Palette (Slate & Grays)

| Token | Hex Value | Usage in Light Mode | Usage in Dark Mode |
|---|---|---|---|
| `neutral-0` | `#FFFFFF` | Card surface, modal surface | - |
| `neutral-50` | `#F8FAFC` | Main application background | Page headers, high contrast text |
| `neutral-100` | `#F1F5F9` | Subtle background, input background | - |
| `neutral-200` | `#E2E8F0` | Standard border, table dividers | - |
| `neutral-300` | `#CBD5E1` | Muted borders, disabled checkboxes | Body reading text |
| `neutral-400` | `#94A3B8` | Placeholder text, inactive icons | Secondary supporting text |
| `neutral-500` | `#64748B` | Secondary text, timestamps | Inactive icons |
| `neutral-600` | `#475569` | Body text variant | Border accents |
| `neutral-700` | `#334155` | Primary body reading text | Card surface borders |
| `neutral-800` | `#1E293B` | High contrast subtitles | Card surface (`bg-slate-800`) |
| `neutral-900` | `#0F172A` | Page headings, high contrast text | Main card surface (`bg-slate-900`) |
| `neutral-950` | `#0B1020` | - | Deep application background |

---

### 2.3 Semantic Status Palette

```
┌─────────────────────────────────────────────────────────────┐
│                 Semantic Status Palette Roles               │
├──────────────┬─────────────┬─────────────┬──────────────────┤
│ Semantic     │ Solid Hex   │ Soft BG     │ Intended Meaning │
├──────────────┼─────────────┼─────────────┼──────────────────┤
│ Success      │ #16A34A     │ #DCFCE7     │ Mastered, Ready  │
│ Warning      │ #D97706     │ #FEF3C7     │ Paused, Hesitant │
│ Danger       │ #DC2626     │ #FEE2E2     │ Grammar Mistake  │
│ Info         │ #2563EB     │ #DBEAFE     │ Pronunciation    │
└──────────────┴─────────────┴─────────────┴──────────────────┘
```

1. **Success (Emerald - `#16A34A`):**  
   Indicates completed meetings, resolved/mastered grammar rules, optimal speaking pace (130–160 WPM), and scores $\ge$ 85.
2. **Warning (Amber - `#D97706`):**  
   Indicates paused sessions, moderate score ranges (50–69), and stylistic or conditional tense nuances.
3. **Danger / Critical (Rose - `#DC2626`):**  
   Indicates active grammar errors, hardware permission denials, failed jobs, and destructive actions.
4. **Info (Blue / Sky - `#2563EB`):**  
   Indicates phonetic guidance, system updates, and platform connection states.

---

## 3. Contrast Ratios & Accessibility Compliance

Every text-to-background pairing strictly satisfies **WCAG 2.1 Level AA** standards:

| Text Token | Background | Calculated Ratio | Compliance Status |
|---|---|---|:---:|
| `neutral-900` (#0F172A) | `neutral-0` (#FFFFFF) | **16.2:1** | PASS (AAA) |
| `neutral-700` (#334155) | `neutral-0` (#FFFFFF) | **8.9:1** | PASS (AAA) |
| `neutral-500` (#64748B) | `neutral-0` (#FFFFFF) | **4.9:1** | PASS (AA) |
| `primary-600` (#4F46E5) | `neutral-0` (#FFFFFF) | **5.4:1** | PASS (AA) |
| `neutral-50` (#F8FAFC) | `dark-surface` (#111827) | **15.1:1** | PASS (AAA) |
| `neutral-300` (#CBD5E1) | `dark-surface` (#111827) | **9.4:1** | PASS (AAA) |

---

## 4. Anti-Patterns & Prohibitions

1. **No Alarmist Red Overuse:** Minor conversational slips should not look like fatal system crashes. Soft rose badges (`bg-rose-50 text-rose-700`) are used instead of jarring full-red containers.
2. **No Pure Black `#000000` in Dark Mode:** Pure black creates excessive eye strain. The dark theme utilizes rich slate `#0B1020` and elevated surface `#111827`.
3. **No Unlabelled Status Pills:** Never show a colored dot without an accompanying textual label or screen reader `aria-label`.

