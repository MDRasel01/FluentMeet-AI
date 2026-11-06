# Component States & Page-Level State Contract

**Product Name:** AI Meeting English Coach  
**Document ID:** COMP-STATES-V1.0  
**Phase:** Step 02  
**Status:** Approved State Contract  

---

## 1. The Universal Six-State Component Lifecycle

Every interactive element in the design system implements an explicit state machine:

```
[ Default ] ──► [ Hover ] ──► [ Focus-Visible ] ──► [ Active/Pressed ]
     │               │                                      │
     ▼               ▼                                      ▼
[ Disabled ] ◄── [ Loading ]                          [ Released ]
```

---

## 2. Component State Specifications

### 2.1 Button State Matrix

| State | Visual Treatment | CSS Classes |
|---|---|---|
| **Default** | Solid brand color, 1px subtle elevation | `bg-indigo-600 text-white shadow-xs` |
| **Hover** | 8% darker shade, smooth 150ms transition | `hover:bg-indigo-700` |
| **Focus-Visible** | 2px high-contrast offset focus ring | `focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2` |
| **Active / Pressed**| Subtle 0.98 scale transform, darkened shade | `active:scale-[0.98] active:bg-indigo-800` |
| **Disabled** | 50% opacity, cursor not-allowed | `disabled:opacity-50 disabled:pointer-events-none` |
| **Loading** | Label hidden or shifted, inline spinning SVG | `animate-spin w-4 h-4` |

---

### 2.2 Form Input State Matrix

| State | Visual Treatment | CSS Classes |
|---|---|---|
| **Default** | 1px slate-300 border, slate-900 text | `border-slate-300 bg-white dark:bg-slate-900` |
| **Hover** | Slate-400 border | `hover:border-slate-400` |
| **Focus** | Indigo-500 border + 2px soft ring | `focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500` |
| **Error** | Rose-500 border, rose helper text | `border-rose-500 text-rose-900 focus:ring-rose-500` |
| **Disabled** | Slate-100 fill, slate-400 text | `bg-slate-100 cursor-not-allowed opacity-60` |

---

## 3. Page-Level Universal State Contract

Every screen across the Web Dashboard, Extension, and Admin Panel must handle the following five structural page-level states:

### 3.1 Loading State (Shimmer Skeletons)
- **Rule:** Never use full-screen blocking spinners.
- **Implementation:** Shimmer placeholders (`SkeletonLoader`) mirroring the exact geometry of KPI cards, data tables, and transcript segment bubbles.

### 3.2 Empty State (Educational Guidance)
- **Strict Rule:** **Zero Mock / Fake Performance Data!**
- **Implementation:** Display an illustrated icon, an encouraging heading (e.g., *"No Meetings Recorded Yet"*), a concise explanation, and a primary CTA (e.g., *"Download Chrome Extension"* or *"Watch 1-Minute Walkthrough"*).

### 3.3 Error State (Actionable Recovery)
- **Rule:** Errors must never be dead-ends.
- **Implementation:** High-visibility banner explaining the technical cause in plain English with an immediate action trigger (e.g., *"Failed to load meeting transcript. [Retry Connection]"*).

### 3.4 Success State (Subtle Feedback)
- **Implementation:** Toast notification floating top-right (auto-dismiss 4000ms) or inline green badge (e.g., *"Saved to Practice Deck"*).

### 3.5 Disabled / Gated State
- **Rule:** Never leave users wondering why an action is unavailable.
- **Implementation:** Disabled buttons must provide a tooltip explaining the requirement (e.g., the Extension "Start Analysis" button displays: *"Requires participant consent confirmation"*).

