# Step 10 — Secure Export Service Specification (CSV & HTML/Print)

**Module:** Document Export & Security  
**Component:** `app.reports.export.ReportExportService`  

---

## 1. Security Guarantee: CSV Formula Injection Defense (CWE-1236)

When exporting participant speech, user names, or grammar explanations to CSV, malicious or inadvertent input could execute formula payloads (e.g. `=CMD|' /C calc'!A0` or `@SUM(...)`) when opened in Microsoft Excel or Google Sheets.

### 1.1 Defense Implementation
Every cell processed by `sanitize_csv_cell` is inspected:
```python
def sanitize_csv_cell(val: Any) -> str:
    if val is None:
        return ""
    text = str(val)
    if text and text[0] in ("=", "+", "-", "@"):
        return "'" + text
    return text
```
Prepending `'` forces spreadsheet processors to interpret the cell as raw text, completely neutralizing formula injection.

## 2. Print-Optimized HTML Export

1. Standalone, CSS-styled document with responsive flexbox and grid layouts.
2. `@media print` rules ensure clean page breaks without dark theme ink waste.
3. Every report prominently includes the statutory IELTS practice disclaimer:
   > *"Educational practice estimate only. This is not an official IELTS score, certified assessment, or substitute for an IELTS examiner."*
4. SHA-256 cryptographic hash is generated for each export artifact and stored in `report_exports.content_hash` for audit and integrity verification.

