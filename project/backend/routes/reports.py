"""
Report Routes — generate and email interview performance reports.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import smtplib
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import os

from database import execute_query

router = APIRouter(prefix="/reports", tags=["Reports"])


class EmailReportRequest(BaseModel):
    session_id: str
    recipient_email: str
    recipient_name: Optional[str] = None


class GenerateReportRequest(BaseModel):
    session_id: str


# ── Helpers ───────────────────────────────────────────────────────────

def _get_score_label(score: int) -> str:
    if score >= 85:
        return "Excellent"
    if score >= 70:
        return "Good"
    if score >= 50:
        return "Fair"
    return "Needs Improvement"


def _score_color(score: float) -> str:
    if score >= 85: return "#16A34A"
    if score >= 70: return "#2563EB"
    if score >= 50: return "#EA580C"
    return "#DC2626"


def _get_personality_name(personality: str) -> str:
    names = {
        "friendly": "Friendly HR",
        "technical": "Strict Technical",
        "stress": "Stress Interview",
        "panel": "Panel Interview",
    }
    return names.get(personality, personality.title())


# ── Fetch AI evaluation (per-question feedback + recommendations) ─────

def _fetch_ai_data(session_id: str):
    """Re-run AI evaluation to get per-question feedback and recommendations."""
    try:
        from services.ai_engine import evaluate_responses
        sess_rows = execute_query(
            "SELECT resume_text, personality FROM interview_sessions WHERE id=%s",
            (session_id,),
        )
        if not sess_rows:
            return [], []
        sess = sess_rows[0]
        rows = execute_query(
            "SELECT question, answer, input_mode, recording_duration "
            "FROM interview_responses WHERE session_id=%s ORDER BY question_index",
            (session_id,),
        )
        if not rows:
            return [], []
        responses = [
            {
                "question": r["question"],
                "answer": r["answer"],
                "input_mode": r.get("input_mode", "text") or "text",
                "recording_duration": float(r.get("recording_duration") or 0),
            }
            for r in rows
        ]
        ev = evaluate_responses(
            sess.get("resume_text", ""),
            sess.get("personality", "friendly"),
            responses,
        )
        return ev.get("per_question_feedback", []), ev.get("recommendations", [])
    except Exception as e:
        print(f"[reports] Could not fetch AI eval: {e}")
        return [], []


def _build_report_text(
    session: dict,
    responses: list,
    results: dict | None,
    per_q: list | None = None,
    recs: list | None = None,
) -> str:
    """Build a plain-text performance report."""
    personality = session.get("personality", "friendly")
    overall = results.get("overall_score", 0) if results else 0
    feedback = results.get("feedback", "") if results else ""

    lines = [
        "╔══════════════════════════════════════════════════════════════╗",
        "║          InterviewIQ — Performance Report                   ║",
        "╚══════════════════════════════════════════════════════════════╝",
        "",
        f"  Date:               {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        f"  Interview Type:     {_get_personality_name(personality)}",
        f"  Questions Answered: {len(responses)}",
        f"  Overall Score:      {overall}%  ({_get_score_label(overall)})",
        "",
    ]

    if results:
        lines += [
            "─────────────────────────────────────────────────────────────",
            "  PERFORMANCE METRICS",
            "─────────────────────────────────────────────────────────────",
            f"  Technical Accuracy  : {results.get('technical_accuracy', 0)}%",
            f"  Language Proficiency: {results.get('language_proficiency', 0)}%",
            f"  Confidence Level    : {results.get('confidence_level', 0)}%",
            f"  Sentiment Score     : {results.get('sentiment_score', 0)}%",
            f"  Emotional Stability : {results.get('emotional_stability', 0)}%",
            "",
        ]

    if responses:
        lines += [
            "─────────────────────────────────────────────────────────────",
            "  YOUR RESPONSES",
            "─────────────────────────────────────────────────────────────",
        ]
        for i, r in enumerate(responses):
            fb = next((f for f in (per_q or []) if f.get("question_index") == i), None)
            lines.append(f"\n  Q{i+1}: {r.get('question', 'N/A')}")
            lines.append(f"  A:   {r.get('answer', 'N/A')}")
            if fb:
                lines.append(f"  Score: {fb.get('score', 0)}/100")
                lines.append(f"  ✓ Strength:  {fb.get('strength', '')}")
                lines.append(f"  ↑ Improve:   {fb.get('improvement', '')}")

    if recs:
        lines += [
            "",
            "─────────────────────────────────────────────────────────────",
            "  KEY RECOMMENDATIONS",
            "─────────────────────────────────────────────────────────────",
        ]
        for r in recs:
            lines.append(f"  • {r}")

    if feedback:
        lines += [
            "",
            "─────────────────────────────────────────────────────────────",
            "  SUMMARY",
            "─────────────────────────────────────────────────────────────",
            f"  {feedback}",
        ]

    lines += [
        "",
        "─────────────────────────────────────────────────────────────",
        "  Generated by InterviewIQ — AI-Powered Interview Platform",
        "─────────────────────────────────────────────────────────────",
    ]
    return "\n".join(lines)


def _build_report_html(
    session: dict,
    responses: list,
    results: dict | None,
    per_q: list | None = None,
    recs: list | None = None,
    recipient_name: str = "Candidate",
) -> str:
    """Build a rich HTML performance report for email."""
    personality = session.get("personality", "friendly")
    overall = int(results.get("overall_score", 0)) if results else 0
    feedback = results.get("feedback", "") if results else ""
    sc = _score_color(overall)
    date_str = datetime.now().strftime("%B %d, %Y")

    # ── Metric bars ──────────────────────────────────────────────────
    metric_rows = ""
    if results:
        for label, key, color in [
            ("Technical Accuracy",   "technical_accuracy",   "#2563EB"),
            ("Language Proficiency", "language_proficiency", "#10B981"),
            ("Confidence Level",     "confidence_level",     "#F97316"),
            ("Sentiment Score",      "sentiment_score",      "#EC4899"),
            ("Emotional Stability",  "emotional_stability",  "#06B6D4"),
        ]:
            s = int(results.get(key, 0))
            metric_rows += f"""
              <tr>
                <td style="padding:10px 14px;color:#334155;font-weight:600;white-space:nowrap;font-size:13px">{label}</td>
                <td style="padding:10px 14px;width:100%">
                  <div style="background:#E2E8F0;border-radius:99px;height:10px;overflow:hidden">
                    <div style="background:{color};height:100%;width:{s}%;border-radius:99px"></div>
                  </div>
                </td>
                <td style="padding:10px 14px;font-weight:700;color:{color};white-space:nowrap;font-size:13px">{s}%</td>
              </tr>"""

    # ── Per-question blocks ──────────────────────────────────────────
    q_blocks = ""
    if responses:
        for i, r in enumerate(responses):
            fb  = next((f for f in (per_q or []) if f.get("question_index") == i), None)
            qsc = int(fb["score"]) if fb else None
            qc  = _score_color(qsc) if qsc is not None else "#64748B"
            ans = r.get("answer", "N/A")
            if ans.startswith("[") and "no speech" in ans.lower():
                ans_html = '<span style="color:#94A3B8;font-style:italic">No speech detected for this response.</span>'
            else:
                ans_html = ans.replace("<", "&lt;").replace(">", "&gt;")

            badge = (
                f'<span style="float:right;background:{qc};color:#fff;'
                f'font-size:11px;font-weight:700;padding:2px 9px;border-radius:99px">'
                f'{qsc}/100</span>'
            ) if qsc is not None else ""

            strength_html = improvement_html = ""
            if fb:
                strength_html = (
                    f'<div style="background:#F0FDF4;border-left:3px solid #16A34A;'
                    f'padding:8px 12px;margin-top:8px;border-radius:0 6px 6px 0;'
                    f'font-size:13px;color:#166534">'
                    f'<strong>✓ Strength:</strong> {fb.get("strength", "")}</div>'
                )
                improvement_html = (
                    f'<div style="background:#FFFBEB;border-left:3px solid #D97706;'
                    f'padding:8px 12px;margin-top:6px;border-radius:0 6px 6px 0;'
                    f'font-size:13px;color:#92400E">'
                    f'<strong>↑ Improve:</strong> {fb.get("improvement", "")}</div>'
                )

            q_blocks += f"""
            <div style="border:1px solid #E2E8F0;border-radius:10px;padding:16px;margin-bottom:14px">
              <div style="display:flex;align-items:flex-start;gap:12px">
                <div style="background:#2563EB;color:#fff;font-weight:700;min-width:26px;height:26px;
                            border-radius:50%;text-align:center;line-height:26px;font-size:12px;flex-shrink:0">{i+1}</div>
                <div style="flex:1">
                  <p style="font-weight:600;color:#0F172A;margin:0 0 6px">{badge}{r.get('question','N/A')}</p>
                  <p style="color:#475569;margin:0;font-size:14px;line-height:1.6">{ans_html}</p>
                  {strength_html}{improvement_html}
                </div>
              </div>
            </div>"""

    # ── Recommendations ──────────────────────────────────────────────
    rec_html = ""
    if recs:
        items = ""
        for idx, rec in enumerate(recs, 1):
            items += (
                f'<div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:10px">'
                f'<div style="background:#2563EB;color:#fff;font-weight:700;min-width:22px;height:22px;'
                f'border-radius:50%;text-align:center;line-height:22px;font-size:11px;flex-shrink:0">{idx}</div>'
                f'<p style="margin:0;color:#1E3A5F;font-size:14px;line-height:1.6">{rec}</p>'
                f'</div>'
            )
        rec_html = (
            f'<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:12px;'
            f'padding:22px;margin-top:28px">'
            f'<h2 style="color:#1E3A5F;font-size:17px;font-weight:700;margin:0 0 16px">🎯 Key Recommendations</h2>'
            f'{items}</div>'
        )

    feedback_block = ""
    if feedback:
        feedback_block = (
            f'<div style="background:#F0F9FF;border:1px solid #BAE6FD;border-radius:12px;'
            f'padding:20px;margin-top:28px">'
            f'<h3 style="color:#0F172A;margin:0 0 8px;font-size:16px">📋 Summary Assessment</h3>'
            f'<p style="color:#0C4A6E;margin:0;font-size:14px;line-height:1.7">{feedback}</p>'
            f'</div>'
        )

    metrics_section = (
        '<h2 style="color:#0F172A;font-size:17px;font-weight:700;margin:0 0 14px">📊 Performance Metrics</h2>'
        '<table style="width:100%;border-collapse:collapse">' + metric_rows + '</table>'
    ) if metric_rows else ""

    q_section = (
        '<h2 style="color:#0F172A;font-size:17px;font-weight:700;margin:28px 0 14px">💬 Question-by-Question Feedback</h2>'
        + q_blocks
    ) if q_blocks else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>InterviewIQ Report</title>
</head>
<body style="margin:0;padding:0;background:#F1F5F9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif">
  <div style="max-width:660px;margin:0 auto;padding:24px 12px">

    <!-- Header -->
    <div style="background:linear-gradient(135deg,#1D4ED8 0%,#0891B2 100%);border-radius:14px 14px 0 0;padding:32px 36px;text-align:center">
      <div style="font-size:28px;font-weight:800;color:#fff;letter-spacing:-0.5px">InterviewIQ</div>
      <div style="color:#BFDBFE;font-size:14px;margin-top:4px">AI-Powered Performance Report</div>
    </div>

    <!-- Card -->
    <div style="background:#fff;border-radius:0 0 14px 14px;box-shadow:0 4px 16px rgba(0,0,0,0.09);padding:32px 36px">

      <!-- Greeting -->
      <p style="color:#475569;margin:0 0 28px;font-size:15px">
        Hi <strong style="color:#0F172A">{recipient_name}</strong>, here is your detailed interview
        performance report from <strong>InterviewIQ</strong>.
      </p>

      <!-- Overall score -->
      <div style="background:linear-gradient(135deg,#EFF6FF,#E0F2FE);border-radius:12px;padding:24px;text-align:center;margin-bottom:28px">
        <div style="color:#64748B;font-size:13px;margin-bottom:4px">Overall Score</div>
        <div style="font-size:52px;font-weight:900;color:{sc};line-height:1">{overall}%</div>
        <div style="font-weight:600;color:{sc};margin-top:4px">{_get_score_label(overall)}</div>
      </div>

      <!-- Meta strip -->
      <table style="width:100%;border-collapse:collapse;margin-bottom:28px">
        <tr>
          <td style="padding:12px;text-align:center;background:#F8FAFC;border-radius:8px">
            <div style="color:#94A3B8;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.6px">Interview Type</div>
            <div style="font-weight:700;color:#0F172A;margin-top:5px;font-size:14px">{_get_personality_name(personality)}</div>
          </td>
          <td style="width:10px"></td>
          <td style="padding:12px;text-align:center;background:#F8FAFC;border-radius:8px">
            <div style="color:#94A3B8;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.6px">Questions</div>
            <div style="font-weight:700;color:#0F172A;margin-top:5px;font-size:14px">{len(responses)}</div>
          </td>
          <td style="width:10px"></td>
          <td style="padding:12px;text-align:center;background:#F8FAFC;border-radius:8px">
            <div style="color:#94A3B8;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.6px">Date</div>
            <div style="font-weight:700;color:#0F172A;margin-top:5px;font-size:14px">{date_str}</div>
          </td>
        </tr>
      </table>

      {metrics_section}
      {q_section}
      {rec_html}
      {feedback_block}

      <!-- Footer -->
      <div style="text-align:center;margin-top:36px;padding-top:22px;border-top:1px solid #F1F5F9">
        <p style="color:#94A3B8;font-size:12px;margin:0">Generated by <strong>InterviewIQ</strong> — AI-Powered Interview Practice Platform</p>
        <p style="color:#CBD5E1;font-size:11px;margin:4px 0 0">This report is for practice purposes only.</p>
      </div>
    </div>
  </div>
</body>
</html>"""


def _fetch_session_data(session_id: str):
    """Fetch session, responses, and results from DB."""
    sessions = execute_query(
        "SELECT * FROM interview_sessions WHERE id = %s", (session_id,)
    )
    if not sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    session = sessions[0]

    responses = execute_query(
        "SELECT * FROM interview_responses WHERE session_id = %s ORDER BY question_index",
        (session_id,),
    )

    results_rows = execute_query(
        "SELECT * FROM performance_results WHERE session_id = %s", (session_id,)
    )
    results = results_rows[0] if results_rows else None

    return session, responses, results


# ── Endpoints ────────────────────────────────────────────────────────

@router.post("/generate")
async def generate_report(req: GenerateReportRequest):
    """Generate a downloadable report for a session."""
    session, responses, results = _fetch_session_data(req.session_id)
    per_q, recs = _fetch_ai_data(req.session_id)
    text_report = _build_report_text(session, responses, results, per_q, recs)
    return {
        "success": True,
        "data": {
            "report_text": text_report,
            "session_id": req.session_id,
            "generated_at": datetime.now().isoformat(),
        },
    }


@router.post("/email")
async def email_report(req: EmailReportRequest):
    """Email the performance report to the user."""
    session, responses, results = _fetch_session_data(req.session_id)
    per_q, recs = _fetch_ai_data(req.session_id)

    recipient_name = (req.recipient_name or "").strip() or "Candidate"

    # Build reports
    text_report = _build_report_text(session, responses, results, per_q, recs)
    html_report = _build_report_html(session, responses, results, per_q, recs, recipient_name)

    # SMTP configuration
    smtp_host  = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port  = int(os.getenv("SMTP_PORT", "587"))
    smtp_user  = os.getenv("SMTP_USER", "")
    smtp_pass  = os.getenv("SMTP_PASS", "")
    from_email = os.getenv("SMTP_FROM", smtp_user)
    from_name  = os.getenv("SMTP_FROM_NAME", "InterviewIQ")

    if not smtp_user or not smtp_pass or smtp_pass == "your_16_char_app_password_here":
        # SMTP not configured — return report so frontend can offer PDF download
        return {
            "success": True,
            "data": {
                "delivered": False,
                "fallback": True,
                "report_text": text_report,
                "message": "Email service not configured. Please update SMTP_PASS in backend/.env. Offering PDF download instead.",
            },
        }

    overall_score = results.get("overall_score", 0) if results else 0

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Your InterviewIQ Report — {_get_score_label(overall_score)} ({overall_score}%)"
    msg["From"]    = f"{from_name} <{from_email}>"
    msg["To"]      = req.recipient_email
    msg["Reply-To"] = from_email

    msg.attach(MIMEText(text_report, "plain", "utf-8"))
    msg.attach(MIMEText(html_report, "html",  "utf-8"))

    # Attach plain-text report as file
    att = MIMEBase("text", "plain")
    att.set_payload(text_report.encode("utf-8"))
    encoders.encode_base64(att)
    att.add_header(
        "Content-Disposition",
        "attachment",
        filename=f"InterviewIQ_Report_{datetime.now().strftime('%Y-%m-%d')}.txt",
    )
    msg.attach(att)

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_pass)
            server.sendmail(from_email, [req.recipient_email], msg.as_string())

        return {
            "success": True,
            "data": {
                "delivered": True,
                "recipient": req.recipient_email,
                "message": f"Report sent successfully to {req.recipient_email}!",
            },
        }
    except smtplib.SMTPAuthenticationError:
        raise HTTPException(
            status_code=500,
            detail=(
                "Gmail authentication failed. "
                "Make sure you are using a 16-character App Password "
                "(not your regular Gmail password). "
                "Get one at: https://myaccount.google.com/apppasswords"
            ),
        )
    except smtplib.SMTPRecipientsRefused:
        raise HTTPException(status_code=400, detail=f"Invalid recipient address: {req.recipient_email}")
    except smtplib.SMTPConnectError:
        raise HTTPException(
            status_code=503,
            detail="Could not connect to mail server. Check SMTP_HOST and SMTP_PORT in .env.",
        )
    except smtplib.SMTPException as e:
        raise HTTPException(status_code=500, detail=f"SMTP error: {str(e)}")
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Email failed: {str(e)}")
