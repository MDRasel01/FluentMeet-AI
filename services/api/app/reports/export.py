"""
FluentMeet AI - Step 10: Report Export Service
Generates sanitized CSV and print-optimized HTML/PDF documents with strict formula injection defense and IELTS disclaimers.
"""

import io
import csv
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import ReportSnapshot, ReportExport, ReportAccessLog
from app.reports.builder import MANDATORY_IELTS_DISCLAIMER


def sanitize_csv_cell(val: Any) -> str:
    """
    Prevents CSV / Spreadsheet Formula Injection (CWE-1236).
    If cell begins with '=', '+', '-', '@', '\t', or '\r' (even after leading whitespace),
    prepend a single quote (') to neutralize execution in Excel / Google Sheets.
    """
    if val is None:
        return ""
    text = str(val)
    stripped = text.lstrip()
    if stripped and stripped[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + text
    return text


class ReportExportService:
    """
    Exports ReportSnapshot payloads into CSV and HTML formats.
    """

    @classmethod
    async def export_csv(
        cls,
        db: AsyncSession,
        snapshot: ReportSnapshot,
        user_id: Optional[str] = None,
    ) -> str:
        """
        Generates sanitized CSV string for a ReportSnapshot.
        """
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        payload = snapshot.report_payload or {}
        report_type = snapshot.report_type

        if report_type == "individual_participant":
            meta = payload.get("metadata", {})
            perf = payload.get("overall_performance", {})
            metrics = payload.get("speaking_metrics", {})
            ielts = payload.get("ielts_estimate") or {}

            # Metadata & Performance
            writer.writerow(["FluentMeet AI - Individual English Assessment Report"])
            writer.writerow(["Report ID", sanitize_csv_cell(snapshot.id)])
            writer.writerow(["Meeting ID", sanitize_csv_cell(snapshot.meeting_id)])
            writer.writerow(["Speaker Label", sanitize_csv_cell(meta.get("speaker_label"))])
            writer.writerow(["Display Name", sanitize_csv_cell(meta.get("display_name"))])
            writer.writerow(["Overall Score", sanitize_csv_cell(perf.get("overall_score"))])
            writer.writerow(["Status", sanitize_csv_cell(perf.get("status_label"))])
            writer.writerow(["Total Words", sanitize_csv_cell(metrics.get("total_words"))])
            writer.writerow(["Speaking Duration (s)", sanitize_csv_cell(metrics.get("speaking_duration_seconds"))])
            writer.writerow(["Words Per Minute", sanitize_csv_cell(metrics.get("words_per_minute"))])
            writer.writerow(["IELTS Band Estimate", sanitize_csv_cell(ielts.get("overall_band_estimate"))])
            writer.writerow(["CEFR Level", sanitize_csv_cell(ielts.get("cefr_level"))])
            writer.writerow([])

            # Grammar issues
            grammar = payload.get("grammar_analysis", {})
            writer.writerow(["--- GRAMMAR CORRECTIONS ---"])
            writer.writerow(["Rule Type", "Severity", "Offending Text", "Corrected Text", "Explanation"])
            for g in grammar.get("issues", []):
                writer.writerow([
                    sanitize_csv_cell(g.get("rule_type")),
                    sanitize_csv_cell(g.get("severity")),
                    sanitize_csv_cell(g.get("offending_text")),
                    sanitize_csv_cell(g.get("corrected_text")),
                    sanitize_csv_cell(g.get("explanation")),
                ])
            writer.writerow([])

            # Pronunciation
            pron = payload.get("pronunciation_analysis", {})
            writer.writerow(["--- PRONUNCIATION OBSERVATIONS ---"])
            writer.writerow(["Word", "Accuracy Score", "Expected Phonemes", "Produced Phonemes"])
            for w in pron.get("mispronounced_words", []):
                writer.writerow([
                    sanitize_csv_cell(w.get("word")),
                    sanitize_csv_cell(w.get("accuracy_score")),
                    sanitize_csv_cell(w.get("phonemes_expected")),
                    sanitize_csv_cell(w.get("phonemes_produced")),
                ])
            writer.writerow([])

            # Recommendations
            writer.writerow(["--- ACTIONABLE RECOMMENDATIONS ---"])
            writer.writerow(["Source", "Category", "Priority", "Recommendation", "Practice Text"])
            for r in payload.get("recommendations", []):
                writer.writerow([
                    sanitize_csv_cell(r.get("source")),
                    sanitize_csv_cell(r.get("category")),
                    sanitize_csv_cell(r.get("priority")),
                    sanitize_csv_cell(r.get("recommendation_text")),
                    sanitize_csv_cell(r.get("practice_text")),
                ])

        else:
            # Meeting Summary CSV
            meta = payload.get("metadata", {})
            sum_metrics = payload.get("summary_metrics", {})
            writer.writerow(["FluentMeet AI - Meeting Summary Report"])
            writer.writerow(["Meeting ID", sanitize_csv_cell(snapshot.meeting_id)])
            writer.writerow(["Title", sanitize_csv_cell(meta.get("title"))])
            writer.writerow(["Participants Count", sanitize_csv_cell(sum_metrics.get("participant_count"))])
            writer.writerow(["Total Duration (s)", sanitize_csv_cell(sum_metrics.get("total_duration_seconds"))])
            writer.writerow(["Total Words", sanitize_csv_cell(sum_metrics.get("total_words"))])
            writer.writerow(["Average Overall Score", sanitize_csv_cell(sum_metrics.get("average_overall_score"))])
            writer.writerow([])

            # Participants table
            writer.writerow(["--- PARTICIPANT BREAKDOWN ---"])
            writer.writerow(["Speaker Label", "Display Name", "Overall Score", "Status", "Duration (s)", "Words", "Talk Time %", "IELTS Band"])
            for p in payload.get("participants", []):
                writer.writerow([
                    sanitize_csv_cell(p.get("speaker_label")),
                    sanitize_csv_cell(p.get("display_name")),
                    sanitize_csv_cell(p.get("overall_score")),
                    sanitize_csv_cell(p.get("status_label")),
                    sanitize_csv_cell(p.get("duration_seconds")),
                    sanitize_csv_cell(p.get("word_count")),
                    sanitize_csv_cell(p.get("talk_time_percentage")),
                    sanitize_csv_cell(p.get("ielts_band")),
                ])

        csv_content = output.getvalue()
        await cls._record_export(db, snapshot, "csv", csv_content, user_id)
        return csv_content

    @classmethod
    async def export_html(
        cls,
        db: AsyncSession,
        snapshot: ReportSnapshot,
        user_id: Optional[str] = None,
    ) -> str:
        """
        Generates standalone, print-optimized HTML report with CSS styling and IELTS disclaimer.
        """
        payload = snapshot.report_payload or {}
        report_type = snapshot.report_type
        meta = payload.get("metadata", {})

        if report_type == "individual_participant":
            perf = payload.get("overall_performance", {})
            metrics = payload.get("speaking_metrics", {})
            grammar = payload.get("grammar_analysis", {})
            vocab = payload.get("vocabulary_analysis", {})
            fluency = payload.get("fluency_analysis", {})
            pron = payload.get("pronunciation_analysis", {})
            ielts = payload.get("ielts_estimate") or {}
            recs = payload.get("recommendations", [])

            grammar_rows = "".join([
                f"""<tr>
                    <td><span class="badge badge-warning">{g.get('rule_type', 'grammar')}</span></td>
                    <td><del class="text-danger">{g.get('offending_text', '')}</del></td>
                    <td><strong class="text-success">{g.get('corrected_text', '')}</strong></td>
                    <td>{g.get('explanation', '')}</td>
                </tr>"""
                for g in grammar.get("issues", [])
            ])

            pron_rows = "".join([
                f"""<tr>
                    <td><strong>{w.get('word', '')}</strong></td>
                    <td>{w.get('accuracy_score', 0):.1f}%</td>
                    <td><code>{w.get('phonemes_expected', '')}</code></td>
                    <td><code>{w.get('phonemes_produced', '')}</code></td>
                </tr>"""
                for w in pron.get("mispronounced_words", [])
            ])

            rec_cards = "".join([
                f"""<div class="rec-card priority-{r.get('priority', 'medium')}">
                    <div class="rec-header">
                        <span class="badge badge-info">{r.get('category', '')}</span>
                        <span class="priority-label">{r.get('priority', '').upper()}</span>
                    </div>
                    <p class="rec-text">{r.get('recommendation_text', '')}</p>
                    {f'<div class="practice-box"><strong>Practice Drill:</strong> {r.get("practice_text")}</div>' if r.get('practice_text') else ''}
                </div>"""
                for r in recs
            ])

            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>FluentMeet AI - Participant Report: {meta.get('display_name', 'Participant')}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.5; color: #1e293b; margin: 0; padding: 24px; background: #f8fafc; }}
  .container {{ max-width: 900px; margin: 0 auto; background: #ffffff; padding: 32px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
  .header {{ border-bottom: 2px solid #e2e8f0; padding-bottom: 16px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; }}
  .logo {{ font-size: 24px; font-weight: 800; color: #4338ca; }}
  .badge {{ display: inline-block; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; }}
  .badge-primary {{ background: #e0e7ff; color: #3730a3; }}
  .badge-warning {{ background: #fef3c7; color: #92400e; }}
  .badge-info {{ background: #e0f2fe; color: #0369a1; }}
  .scorecards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px; }}
  .card {{ background: #f1f5f9; padding: 16px; border-radius: 8px; text-align: center; border-left: 4px solid #6366f1; }}
  .card-val {{ font-size: 32px; font-weight: 700; color: #0f172a; margin: 4px 0; }}
  .card-label {{ font-size: 13px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 12px; margin-bottom: 24px; }}
  th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 14px; }}
  th {{ background: #f8fafc; color: #475569; font-weight: 600; }}
  .text-danger {{ color: #dc2626; }}
  .text-success {{ color: #16a34a; }}
  .rec-card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 12px; }}
  .priority-high {{ border-left: 4px solid #ef4444; }}
  .priority-medium {{ border-left: 4px solid #f59e0b; }}
  .priority-low {{ border-left: 4px solid #10b981; }}
  .practice-box {{ background: #eff6ff; padding: 10px; border-radius: 6px; margin-top: 8px; font-size: 13px; color: #1e40af; }}
  .disclaimer {{ background: #fffbeb; border: 1px solid #fef3c7; padding: 14px; border-radius: 8px; font-size: 13px; color: #92400e; margin-top: 32px; text-align: center; }}
  @media print {{
    body {{ background: #ffffff; padding: 0; }}
    .container {{ box-shadow: none; border-radius: 0; padding: 12px; }}
    .no-print {{ display: none; }}
  }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div>
      <div class="logo">FluentMeet AI</div>
      <h2 style="margin: 4px 0 0 0;">Participant Communication Assessment</h2>
      <p style="margin: 4px 0 0 0; color: #64748b; font-size: 14px;">Speaker: <strong>{meta.get('display_name')}</strong> ({meta.get('speaker_label')}) | Meeting: {snapshot.meeting_id}</p>
    </div>
    <div>
      <span class="badge badge-primary">{perf.get('status_label', 'Status')}</span>
    </div>
  </div>

  <div class="scorecards">
    <div class="card">
      <div class="card-label">Overall English Score</div>
      <div class="card-val">{perf.get('overall_score') if perf.get('overall_score') is not None else '--'}</div>
      <div style="font-size: 12px; color: #64748b;">Out of 100</div>
    </div>
    <div class="card">
      <div class="card-label">IELTS Practice Band</div>
      <div class="card-val">{ielts.get('overall_band_estimate', '--')}</div>
      <div style="font-size: 12px; color: #64748b;">CEFR: {ielts.get('cefr_level', '--')}</div>
    </div>
    <div class="card">
      <div class="card-label">Speaking Pace</div>
      <div class="card-val">{metrics.get('words_per_minute', 0)}</div>
      <div style="font-size: 12px; color: #64748b;">Words / Minute</div>
    </div>
    <div class="card">
      <div class="card-label">Spoken Volume</div>
      <div class="card-val">{metrics.get('total_words', 0)}</div>
      <div style="font-size: 12px; color: #64748b;">Words ({metrics.get('speaking_duration_seconds', 0)}s)</div>
    </div>
  </div>

  <h3>Grammar Accuracy Analysis</h3>
  <table>
    <thead>
      <tr><th>Rule Type</th><th>Observed Text</th><th>Suggested Form</th><th>Explanation</th></tr>
    </thead>
    <tbody>
      {grammar_rows or '<tr><td colspan="4" style="text-align: center; color: #64748b;">No grammatical issues detected.</td></tr>'}
    </tbody>
  </table>

  <h3>Pronunciation & Acoustic Clarity</h3>
  <table>
    <thead>
      <tr><th>Word</th><th>Accuracy</th><th>Expected Phonemes</th><th>Produced Phonemes</th></tr>
    </thead>
    <tbody>
      {pron_rows or '<tr><td colspan="4" style="text-align: center; color: #64748b;">All evaluated words pronounced clearly.</td></tr>'}
    </tbody>
  </table>

  <h3>Personalized Improvement Drills</h3>
  {rec_cards or '<p style="color: #64748b;">No corrective drills required for this meeting.</p>'}

  <div class="disclaimer">
    <strong>Educational Disclaimer:</strong> {MANDATORY_IELTS_DISCLAIMER}
  </div>
</div>
</body>
</html>"""

        else:
            # Meeting Summary HTML
            sum_metrics = payload.get("summary_metrics", {})
            parts = payload.get("participants", [])
            part_rows = "".join([
                f"""<tr>
                    <td><strong>{p.get('display_name')}</strong></td>
                    <td>{p.get('speaker_label')}</td>
                    <td><strong>{p.get('overall_score') if p.get('overall_score') is not None else '--'}</strong></td>
                    <td><span class="badge badge-info">{p.get('status_label')}</span></td>
                    <td>{p.get('word_count')} words ({p.get('duration_seconds')}s)</td>
                    <td>{p.get('talk_time_percentage')}%</td>
                    <td>{p.get('ielts_band', '--')}</td>
                </tr>"""
                for p in parts
            ])

            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>FluentMeet AI - Meeting Summary: {meta.get('title', 'Meeting')}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.5; color: #1e293b; margin: 0; padding: 24px; background: #f8fafc; }}
  .container {{ max-width: 900px; margin: 0 auto; background: #ffffff; padding: 32px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
  .header {{ border-bottom: 2px solid #e2e8f0; padding-bottom: 16px; margin-bottom: 24px; }}
  .logo {{ font-size: 24px; font-weight: 800; color: #4338ca; }}
  .badge {{ display: inline-block; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; }}
  .badge-info {{ background: #e0f2fe; color: #0369a1; }}
  .scorecards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px; }}
  .card {{ background: #f1f5f9; padding: 16px; border-radius: 8px; text-align: center; border-left: 4px solid #6366f1; }}
  .card-val {{ font-size: 32px; font-weight: 700; color: #0f172a; margin: 4px 0; }}
  .card-label {{ font-size: 13px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 12px; margin-bottom: 24px; }}
  th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 14px; }}
  th {{ background: #f8fafc; color: #475569; font-weight: 600; }}
  .disclaimer {{ background: #fffbeb; border: 1px solid #fef3c7; padding: 14px; border-radius: 8px; font-size: 13px; color: #92400e; margin-top: 32px; text-align: center; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="logo">FluentMeet AI</div>
    <h2 style="margin: 4px 0 0 0;">Meeting English Intelligence Summary</h2>
    <p style="margin: 4px 0 0 0; color: #64748b; font-size: 14px;">Meeting: <strong>{meta.get('title')}</strong> | ID: {snapshot.meeting_id}</p>
  </div>

  <div class="scorecards">
    <div class="card">
      <div class="card-label">Average Score</div>
      <div class="card-val">{sum_metrics.get('average_overall_score') if sum_metrics.get('average_overall_score') is not None else '--'}</div>
      <div style="font-size: 12px; color: #64748b;">Calibrated Participants</div>
    </div>
    <div class="card">
      <div class="card-label">Participants</div>
      <div class="card-val">{sum_metrics.get('participant_count', 0)}</div>
      <div style="font-size: 12px; color: #64748b;">Speakers Analyzed</div>
    </div>
    <div class="card">
      <div class="card-label">Total Duration</div>
      <div class="card-val">{sum_metrics.get('total_duration_seconds', 0)}s</div>
      <div style="font-size: 12px; color: #64748b;">Total Speech Time</div>
    </div>
    <div class="card">
      <div class="card-label">Total Spoken Words</div>
      <div class="card-val">{sum_metrics.get('total_words', 0)}</div>
      <div style="font-size: 12px; color: #64748b;">Words Captured</div>
    </div>
  </div>

  <h3>Participant Contributions & Scores</h3>
  <table>
    <thead>
      <tr><th>Participant</th><th>Speaker</th><th>Score</th><th>Status</th><th>Contribution</th><th>Talk Time</th><th>IELTS Band</th></tr>
    </thead>
    <tbody>
      {part_rows or '<tr><td colspan="7" style="text-align: center; color: #64748b;">No participants evaluated.</td></tr>'}
    </tbody>
  </table>

  <div class="disclaimer">
    <strong>Educational Disclaimer:</strong> {MANDATORY_IELTS_DISCLAIMER}
  </div>
</div>
</body>
</html>"""

        await cls._record_export(db, snapshot, "html", html, user_id)
        return html

    @classmethod
    async def _record_export(
        cls,
        db: AsyncSession,
        snapshot: ReportSnapshot,
        export_format: str,
        content: str,
        user_id: Optional[str],
    ) -> ReportExport:
        content_bytes = content.encode("utf-8")
        content_hash = hashlib.sha256(content_bytes).hexdigest()
        
        export_record = ReportExport(
            tenant_id=snapshot.tenant_id,
            user_id=user_id,
            report_snapshot_id=snapshot.id,
            export_format=export_format,
            storage_reference=f"memory://{snapshot.id}.{export_format}",
            export_status="completed",
            file_size_bytes=len(content_bytes),
            content_hash=content_hash,
        )
        db.add(export_record)
        
        # Access log
        log = ReportAccessLog(
            tenant_id=snapshot.tenant_id,
            report_snapshot_id=snapshot.id,
            actor_id=user_id,
            action=f"export_{export_format}",
            request_metadata={"file_size_bytes": len(content_bytes)},
        )
        db.add(log)
        await db.commit()
        await db.refresh(export_record)
        return export_record
