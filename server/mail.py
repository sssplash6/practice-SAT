"""Mail: sign-in codes (Shell §3.1.5), the diagnostic's confirmation, and the
report notices (R17).

With SMTP configured in the environment this sends. Without it, it writes the
message to server/outbox/ and says so in the log, rather than returning success
for a mail nobody sent -- a signup flow that silently swallows its own email is
the kind of thing you find out about from a student who never got one.

    SATF_SMTP_HOST  SATF_SMTP_PORT  SATF_SMTP_USER  SATF_SMTP_PASS
    SATF_MAIL_FROM  SATF_BASE_URL
"""

from __future__ import annotations

import datetime as dt
import logging
import os
import pathlib
import smtplib
import ssl
from email.message import EmailMessage

log = logging.getLogger("satf.mail")
OUTBOX = pathlib.Path(__file__).resolve().parent / "outbox"

BASE_URL = os.environ.get("SATF_BASE_URL", "http://localhost:8000")
MAIL_FROM = os.environ.get("SATF_MAIL_FROM", "SAT Freshman <no-reply@localhost>")


def mode() -> str:
    """'smtp' when mail really goes out, else 'outbox' (U19: /api/health and
    the admin header say which)."""
    return "smtp" if os.environ.get("SATF_SMTP_HOST") else "outbox"


def verify_url(token: str) -> str:
    return f"{BASE_URL}/api/verify?token={token}"


PILL = ("background:#F18508;color:#3F3F3F;padding:11px 22px;border-radius:999px;"
        "text-decoration:none;font-weight:700;font-family:Helvetica,Arial,sans-serif")
CODE_STYLE = ("font-family:'DM Mono',ui-monospace,Menlo,Consolas,monospace;font-size:32px;"
              "letter-spacing:.12em;color:#1E1E1E;margin:8px 0 18px")
QUIET = "color:#6b6b6b;font:13px Helvetica,Arial,sans-serif"
IGNORE = "If you didn't ask for this, ignore it. Nobody can sign in without this code."


def grouped(code: str) -> str:
    """482913 -> '482 913', as the subject and the code boxes show it."""
    return f"{code[:3]} {code[3:]}"


def signin_url(token: str) -> str:
    return f"{BASE_URL}/signin/?t={token}"


def build(to: str, first: str, token: str, code: str | None = None) -> EmailMessage:
    """The diagnostic's confirmation. With a code (and its sign-in link) it
    also saves the account on the device that sat the test (§3.1.5)."""
    link = verify_url(token)
    m = EmailMessage()
    m["Subject"] = f"Confirm your email · code {grouped(code)}" if code else "Confirm your email"
    m["From"] = MAIL_FROM
    m["To"] = to
    code_text = (f"Or type this code on the page that asked: {grouped(code)}\n"
                 f"(30 minutes, one use)\n\n") if code else ""
    m.set_content(
        f"Hi {first},\n\n"
        f"Confirm this address to keep your diagnostic results:\n\n"
        f"{link}\n\n"
        f"{code_text}"
        f"If you did not start a diagnostic, ignore this email.\n\n"
        f"SAT Freshman\n"
    )
    code_html = (f'<p style="{QUIET}">Or type this code on the page that asked (30 minutes, one use):</p>'
                 f'<p style="{CODE_STYLE}">{grouped(code)}</p>') if code else ""
    m.add_alternative(
        f"<p>Hi {first},</p>"
        f"<p>Confirm this address to keep your diagnostic results.</p>"
        f'<p><a href="{link}" style="{PILL}">Confirm email</a></p>'
        f"{code_html}"
        f'<p style="{QUIET}">'
        f"If you did not start a diagnostic, ignore this email.</p>",
        subtype="html",
    )
    return m


def build_login(to: str, code: str, token: str) -> EmailMessage:
    """Shell §3.1.5: the 6-digit code and a link, each good once for 30 minutes.
    Only the device that asked can finish with the code; the link signs in
    whichever browser opens it, never the one that asked (§3.1.3 item 11)."""
    link = signin_url(token)
    m = EmailMessage()
    m["Subject"] = f"Your SAT Freshman code: {grouped(code)}"
    m["From"] = MAIL_FROM
    m["To"] = to
    m.set_content(
        f"Your code: {grouped(code)}\n\n"
        f"Type it on the page that asked, or open this link on the device you want to use:\n\n"
        f"{link}\n\n"
        f"30 minutes, one use.\n\n"
        f"{IGNORE}\n\n"
        f"SAT Freshman\n"
    )
    m.add_alternative(
        f'<p style="font:15px Helvetica,Arial,sans-serif;color:#1E1E1E">Your code</p>'
        f'<p style="{CODE_STYLE}">{grouped(code)}</p>'
        f'<p style="font:15px Helvetica,Arial,sans-serif;color:#1E1E1E">Type it on the page that asked, '
        f"or open the link on the device you want to use.</p>"
        f'<p><a href="{link}" style="{PILL}">Sign in on this device</a></p>'
        f'<p style="{QUIET}">30 minutes, one use.</p>'
        f'<p style="{QUIET}">{IGNORE}</p>',
        subtype="html",
    )
    return m


def deliver(msg: EmailMessage, note: str = "") -> str:
    """'sent', 'outbox' or 'failed'. Never raises at the caller."""
    to = str(msg["To"])
    if mode() == "outbox":
        OUTBOX.mkdir(parents=True, exist_ok=True)
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%f")
        path = OUTBOX / f"{stamp}-{to.replace('/', '_')}.eml"
        path.write_text(msg.as_string())
        log.warning("SATF_SMTP_HOST is unset, so no mail was sent. Wrote %s%s", path,
                    f" -- {note}" if note else "")
        return "outbox"
    try:
        port = int(os.environ.get("SATF_SMTP_PORT", "587"))
        user = os.environ.get("SATF_SMTP_USER")
        password = os.environ.get("SATF_SMTP_PASS")
        with smtplib.SMTP(os.environ["SATF_SMTP_HOST"], port, timeout=15) as s:
            s.starttls(context=ssl.create_default_context())
            if user:
                s.login(user, password or "")
            s.send_message(msg)
        log.info("%r sent to %s", str(msg["Subject"]), to)
        return "sent"
    except Exception:
        log.exception("could not send %r to %s", str(msg["Subject"]), to)
        return "failed"


def send(to: str, first: str, token: str, code: str | None = None) -> str:
    """The verification email: 'sent', 'outbox' or 'failed'."""
    return deliver(build(to, first, token, code), f"the link is {verify_url(token)}")


def send_login(to: str, code: str, token: str) -> str:
    """The sign-in code: 'sent', 'outbox' or 'failed'."""
    return deliver(build_login(to, code, token), f"the code is {grouped(code)}, the link {signin_url(token)}")


def _one_line(text: str, n: int = 120) -> str:
    return " ".join(str(text or "").split())[:n]


def _plain(to: str, subject: str, body: str) -> EmailMessage:
    m = EmailMessage()
    m["Subject"] = _one_line(subject, 180)
    m["From"] = MAIL_FROM
    m["To"] = to
    m.set_content(body)
    return m


def send_report_notice(to: str, report: dict) -> str:
    """SATF_REPORTS_TO: a new report, with what it is about and the admin link."""
    ctx = report.get("context") or {}
    where = (f"{ctx.get('template')} · seed {ctx.get('seed')}" if ctx.get("template")
             else ctx.get("page") or ctx.get("word") or ctx.get("paper") or report.get("kind"))
    check = report.get("check") or {}
    lines = [f"Report #{report['id']} · {report.get('category_label') or report.get('category')}",
             f"About: {where}",
             f"Summary: {report.get('title') or ''}"]
    if check.get("outcome"):
        lines.append(f"Instant check: {check['outcome']}")
    if report.get("dispute"):
        lines.append("A dispute: the answer is not counted while it is open.")
    if report.get("details"):
        lines += ["", report["details"]]
    if report.get("files"):
        lines.append(f"\n{len(report['files'])} file(s) attached.")
    lines += ["", f"{BASE_URL}/admin/reports/?id={report['id']}"]
    return deliver(_plain(to, f"Report #{report['id']}: {_one_line(report.get('title'), 80)}", "\n".join(lines)))


def send_report_reply(to: str, report_id: int, title: str, reply: str) -> str:
    """The reply to a report, to the reply-to address the student gave."""
    body = (f"You reported: {_one_line(title, 200)}\n\n{reply}\n\n"
            f"Your reports: {BASE_URL}/me/settings/#reports\n\nSAT Freshman\n")
    return deliver(_plain(to, f"Report #{report_id} answered", body))
