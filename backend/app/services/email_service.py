from __future__ import annotations

import smtplib
from email.message import EmailMessage
from pathlib import Path
from uuid import uuid4

from app.core.config import Settings
from app.core.logging import logger
from app.core.store import utcnow


class EmailService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def send_email(self, *, to_email: str, subject: str, body: str) -> str:
        message_id = str(uuid4())
        outbox_dir = Path(self.settings.outbox_dir)
        outbox_dir.mkdir(parents=True, exist_ok=True)
        (outbox_dir / f"{message_id}.txt").write_text(
            f"TO: {to_email}\nSUBJECT: {subject}\n\n{body}\n", encoding="utf-8"
        )
        if self.settings.email_transport == "capture":
            logger.info("email.captured to=%s subject=%s", to_email, subject)
            return message_id
        if self.settings.email_transport != "smtp":
            raise ValueError(f"Unsupported email transport: {self.settings.email_transport}")
        if not self.settings.smtp_host:
            raise RuntimeError("SMTP host is not configured")
        message = EmailMessage()
        message["Message-Id"] = message_id
        message["From"] = self.settings.email_sender
        message["To"] = to_email
        message["Subject"] = subject
        message["Date"] = utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
        message.set_content(body)
        if self.settings.smtp_use_ssl:
            with smtplib.SMTP_SSL(
                host=self.settings.smtp_host,
                port=self.settings.smtp_port,
                timeout=self.settings.smtp_timeout_seconds,
            ) as smtp:
                self._login_if_needed(smtp)
                smtp.send_message(message)
        else:
            with smtplib.SMTP(
                host=self.settings.smtp_host,
                port=self.settings.smtp_port,
                timeout=self.settings.smtp_timeout_seconds,
            ) as smtp:
                if self.settings.smtp_use_tls:
                    smtp.starttls()
                self._login_if_needed(smtp)
                smtp.send_message(message)
        logger.info("email.sent to=%s subject=%s", to_email, subject)
        return message_id

    def _login_if_needed(self, smtp: smtplib.SMTP) -> None:
        if self.settings.smtp_username:
            smtp.login(self.settings.smtp_username, self.settings.smtp_password or "")
