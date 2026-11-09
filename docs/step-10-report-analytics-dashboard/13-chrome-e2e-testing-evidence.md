# Step 10 — Google Chrome Automated E2E Browser Testing & Evidence

**Module:** Automated Chrome Browser Verification  
**Runner:** `scripts/test_chrome_dashboard_reports.py`  
**Browser Binary:** `C:\Program Files\Google\Chrome\Application\chrome.exe`  

---

## 1. Test Methodology

To ensure real-world browser rendering compliance, automated E2E tests are executed directly against the installed Google Chrome binary in headless mode (`--headless=new`).

## 2. Chrome Execution Flags
```bash
chrome.exe \
  --headless=new \
  --disable-gpu \
  --no-sandbox \
  --user-data-dir=<isolated_temp_profile> \
  --screenshot=<output_path.png> \
  --dump-dom \
  file:///path/to/report.html
```

## 3. Verified Assertions

1. **DOM Structure:** Validates presence of `Participant Communication Assessment` header.
2. **Scorecard Calibration:** Validates calibrated score values (`85/100`) and status badges (`Calibrated`).
3. **IELTS Practice Estimate:** Validates presence of practice band score (`Band 7.5`, CEFR `C1`).
4. **Mandatory Educational Disclaimer:** Validates presence of statutory disclaimer text:
   > *"Educational practice estimate only. This is not an official IELTS score, certified assessment, or substitute for an IELTS examiner."*
5. **Visual Capture:** Captures high-resolution PNG screenshot evidence verifying font loading, layout integrity, and badge styling.

