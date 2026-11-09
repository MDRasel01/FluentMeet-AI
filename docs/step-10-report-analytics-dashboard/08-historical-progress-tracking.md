# Step 10 — Historical Performance & Longitudinal Progress Tracking

**Module:** Historical Analytics  
**Component:** `app.reports.history.HistoricalProgressService`  

---

## 1. Longitudinal Growth Objectives

Allows participants and coaches to track English improvement over time, detect chronic error patterns, and verify that personalized drills produce measurable gains.

## 2. Evaluation Rules & Thresholds

1. **Minimum Meeting Requirement:**
   - At least **2 meetings** are required to establish an active growth trajectory.
   - If fewer than 2 meetings are recorded, `trends.status = "baseline_only"`.
2. **Trajectory Classification:**
   - Score Delta = $\text{Score}_{\text{latest}} - \text{Score}_{\text{initial}}$
   - If $\Delta \ge +3.0 \text{ pts}$: `trajectory = "improving"`
   - If $\Delta \le -3.0 \text{ pts}$: `trajectory = "declining"`
   - Otherwise: `trajectory = "steady"`
3. **Recurring Mistakes Detection:**
   - Aggregates grammar errors across all past meetings.
   - Any rule type appearing across **2 or more distinct meetings** is flagged as a recurring mistake.
4. **Persistent Strengths Detection:**
   - Any core category consistently scoring **$\ge 80\%$** across at least 50% of meetings is highlighted as a persistent strength.
