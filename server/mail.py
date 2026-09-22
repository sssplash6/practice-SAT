"""Sending the verification email.

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


def verify_url(token: str) -> str:
    return f"{BASE_URL}/api/verify?token={token}"


def build(to: str, first: str, token: str) -> EmailMessage:
    link = verify_url(token)
    m = EmailMessage()
    m["Subject"] = "Confirm your email"
    m["From"] = MAIL_FROM
    m["To"] = to
    m.set_content(
        f"Hi {first},\n\n"
        f"Confirm this address to keep your diagnostic results:\n\n"
        f"{link}\n\n"
        f"If you did not start a diagnostic, ignore this email.\n\n"
        f"SAT Freshman\n"
    )
    m.add_alternative(
        f"<p>Hi {first},</p>"
        f"<p>Confirm this address to keep your diagnostic results.</p>"
        f'<p><a href="{link}" style="background:#F18508;color:#3F3F3F;padding:11px 22px;'
        f'border-radius:999px;text-decoration:none;font-weight:700;'
        f'font-family:Helvetica,Arial,sans-serif">Confirm email</a></p>'
        f'<p style="color:#6b6b6b;font:13px Helvetica,Arial,sans-serif">'
        f"If you did not start a diagnostic, ignore this email.</p>",
        subtype="html",
    )
    return m


def send(to: str, first: str, token: str) -> str:
    """Returns 'sent' or 'outbox'. Never raises at the caller."""
    msg = build(to, first, token)
    host = os.environ.get("SATF_SMTP_HOST")

    if not host:
        OUTBOX.mkdir(exist_ok=True)
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S")
        path = OUTBOX / f"{stamp}-{to.replace('/', '_')}.eml"
        path.write_text(msg.as_string())
        log.warning("SATF_SMTP_HOST is unset, so no mail was sent. "
                    "Wrote %s -- the link is %s", path, verify_url(token))
        return "outbox"

    try:
        port = int(os.environ.get("SATF_SMTP_PORT", "587"))
        user = os.environ.get("SATF_SMTP_USER")
        password = os.environ.get("SATF_SMTP_PASS")
        with smtplib.SMTP(host, port, timeout=15) as s:
            s.starttls(context=ssl.create_default_context())
            if user:
                s.login(user, password or "")
            s.send_message(msg)
        log.info("verification sent to %s", to)
        return "sent"
    except Exception:
        log.exception("could not send verification to %s", to)
        return "failed"
