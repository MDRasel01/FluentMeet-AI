# Accessibility Specification & WCAG 2.1 AA Audit

**Product Name:** AI Meeting English Coach  
**Document ID:** A11Y-SPEC-V1.0  
**Phase:** Step 02  
**Target Standard:** WCAG 2.1 Level AA Conformance  
**Status:** Approved Accessibility Baseline  

---

## 1. Accessibility Policy & Target Conformance

Language learning software must be universally usable. **AI Meeting English Coach** adheres strictly to **WCAG 2.1 Level AA** standards across all Web Dashboard, Extension, and Admin interfaces.

---

## 2. Key Accessibility Pillars

### 2.1 Color Contrast Compliance (Criterion 1.4.3 & 1.4.11)
- **Normal Text:** All body copy, table cells, and button labels maintain a minimum contrast ratio of **4.5:1** against their background surfaces.
- **Large Text ($\ge$ 18px bold or $\ge$ 24px regular):** Headings and large metric numerals maintain a minimum contrast ratio of **3.0:1**.
- **Interactive UI Components & Focus Rings:** Buttons, input borders, and focus rings maintain at least **3.0:1** contrast against adjacent backgrounds.

| Text & Element Pair | Background | Contrast Ratio | Conformance |
|---|---|---|:---:|
| Heading Text (`#0F172A`) | White (`#FFFFFF`) | **16.2:1** | AAA |
| Body Text (`#334155`) | White (`#FFFFFF`) | **8.9:1** | AAA |
| Supporting Text (`#64748B`) | White (`#FFFFFF`) | **4.9:1** | AA |
| Primary Button (`#4F46E5`) | White Text (`#FFFFFF`) | **5.4:1** | AA |
| Dark Heading (`#F8FAFC`) | Dark Surface (`#111827`) | **15.1:1** | AAA |
| Dark Body (`#CBD5E1`) | Dark Surface (`#111827`) | **9.4:1** | AAA |

---

### 2.2 Complete Keyboard Operability (Criterion 2.1.1 & 2.1.2)
Every functional interaction in the product can be operated using only a keyboard:
- `Tab` / `Shift+Tab`: Moves focus sequentially through links, buttons, inputs, transcript play triggers, and mistake tags.
- `Enter` / `Spacebar`: Activates buttons, toggles checkboxes, and pauses/resumes audio playback.
- `Escape`: Closes active modals, dismisses tooltips, and closes mobile drawers.
- **No Keyboard Traps:** Focus is trapped safely within modal dialogs while open and restored to the triggering element upon dismissal.

### 2.3 High-Contrast Focus Visible Rings (Criterion 2.4.7)
The system eliminates default browser outline ambiguities by defining explicit high-contrast focus rings:
```css
focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2
```
In dark mode, the focus offset uses `--color-bg-app` (`#0B1020`) to guarantee visibility.

---

### 2.4 Semantic HTML & Screen Reader Landmarks (Criterion 1.3.1 & 4.1.2)
- **Semantic Structure:** The layout relies on `<header>`, `<nav>`, `<main>`, `<aside>`, and `<footer>` elements rather than generic `<div>` soup.
- **Explicit Form Labels:** All input components render `<label htmlFor={id}>` explicitly bound to input IDs. Error messages use `aria-describedby` and `aria-invalid="true"`.
- **Descriptive Action Labels:** Icon-only buttons (such as the audio play/pause toggle, theme switch, and modal close triggers) carry explicit `aria-label` tags (e.g., `aria-label="Play from sentence at 04 minutes 12 seconds"`).

---

### 2.5 Motion Sensitivity (Criterion 2.3.3)
All CSS transitions and animations observe the user's operating system preferences:
```css
@media (prefers-reduced-motion: reduce) {
  *, ::before, ::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```
Non-essential animations (such as pinging live dots and spinner rotations) are gracefully disabled.

