# Step 10 — REST API Specification & Endpoint Contracts

**Module:** REST APIs  
**Routers:** `app.api.v1.reports`, `app.api.v1.dashboard`  

---

## 1. Reports Endpoints

| Method | Path | Description | Access Control |
|---|---|---|---|
| `POST` | `/api/v1/reports/generate` | Generates summary and participant report snapshots | Authenticated (Meeting access) |
| `GET` | `/api/v1/reports/meetings/{meeting_id}` | Retrieves latest meeting summary report snapshot | Authenticated (Meeting access) |
| `GET` | `/api/v1/reports/meetings/{meeting_id}/participants` | Retrieves participant snapshots for meeting | Authenticated (Meeting access) |
| `GET` | `/api/v1/reports/participants/{participant_id}` | Retrieves latest report snapshot for participant | Authenticated (Participant access) |
| `GET` | `/api/v1/reports/{report_id}` | Retrieves snapshot by unique report ID | Authenticated (Meeting access) |
| `GET` | `/api/v1/reports/{report_id}/status` | Polls report processing status | Authenticated (Meeting access) |
| `GET` | `/api/v1/reports/participants/{participant_id}/history` | Retrieves cross-meeting historical trajectory | Authenticated (Participant access) |
| `POST` | `/api/v1/reports/{report_id}/export/csv` | Generates and downloads sanitized CSV report | Authenticated (Meeting access) |
| `POST` | `/api/v1/reports/{report_id}/export/html` | Generates and displays styled print HTML report | Authenticated (Meeting access) |

## 2. Dashboard Endpoints

| Method | Path | Description | Access Control |
|---|---|---|---|
| `GET` | `/api/v1/dashboard/summary` | Returns high-level KPI cards | Authenticated User/Tenant |
| `GET` | `/api/v1/dashboard/trends` | Returns historical score trend series | Authenticated User/Tenant |
| `GET` | `/api/v1/dashboard/recent-meetings` | Returns recent meetings feed with scores | Authenticated User/Tenant |

## 3. Error Handling

- `400 Bad Request`: When required parameters are missing or speech evidence is empty.
- `403 Forbidden`: Cross-tenant or unauthorized access attempt.
- `404 Not Found`: When meeting or report snapshot does not exist.
- `500 Internal Server Error`: Unhandled failure (logged to structured log).
