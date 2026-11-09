# Step 10 — Frontend Dashboard Feature Specification

**Module:** Web Dashboard  
**Directory:** `apps/dashboard/src/features/reports/`  
**Host Application:** `apps/dashboard/DashboardApp.tsx`  

---

## 1. Feature Architecture

The Next.js reports feature provides interactive visualization components:

| Component | File | Responsibilities |
|---|---|---|
| `ReportSummaryView` | `ReportSummaryView.tsx` | Displays meeting-level summary cards, talk-time distribution, team growth areas, and participant contribution table |
| `ParticipantReportDetail` | `ParticipantReportDetail.tsx` | In-depth participant report view showing 4 pillars, IELTS practice band + disclaimer, grammar table, pronunciation phonemes, drills |
| `HistoricalTrendView` | `HistoricalTrendView.tsx` | Chronological multi-meeting progress tracker with score deltas, recurring mistakes, and persistent strengths |
| `ExportActions` | `ExportActions.tsx` | Export to CSV (sanitized) and Print/HTML buttons with loading indicators |
| `useReports` | `useReports.ts` | React custom hook managing API requests, caching, export downloads, and state |
| `types` | `types.ts` | TypeScript interfaces matching backend Pydantic schemas |

## 2. Accessibility & Responsiveness

- Built with Tailwind CSS supporting responsive desktop, tablet, and mobile layouts.
- Screen reader-accessible semantic table markup and color-coded score status badges.
- Mandatory IELTS disclaimer rendered with prominent amber callout banner.

