"""Configurable SMTP delivery. No network work or configuration checks at import."""
import os
import smtplib
import ssl
from dataclasses import dataclass
from email.message import EmailMessage
from urllib.parse import urlsplit

from fastapi import HTTPException
from pydantic import TypeAdapter, EmailStr


@dataclass(frozen=True)
class EmailConfig:
    origin: str
    host: str
    port: int
    security: str
    username: str
    password: str
    sender: str
    timeout: float


def email_config() -> EmailConfig:
    try:
        origin = os.environ['PASSWORD_RESET_ORIGIN'].rstrip('/')
        url = urlsplit(origin)
        if (url.scheme != 'https' or not url.hostname or url.username or url.password
                or url.path or url.query or url.fragment or url.port not in (None, 443)):
            raise ValueError('Invalid origin')
        security = os.environ['SMTP_SECURITY']
        if security not in ('starttls', 'ssl'):
            raise ValueError('TLS is required')
        port = int(os.environ['SMTP_PORT'])
        timeout = float(os.getenv('SMTP_TIMEOUT_SECONDS', '10'))
        if not 1 <= port <= 65535 or not 1 <= timeout <= 30:
            raise ValueError('Invalid port or timeout')
        host, username, password, sender = [os.environ[key] for key in
            ('SMTP_HOST', 'SMTP_USERNAME', 'SMTP_PASSWORD', 'SMTP_FROM')]
        if not all((host, username, password, sender)) or any(c in host for c in '\r\n'):
            raise ValueError('Incomplete SMTP configuration')
        TypeAdapter(EmailStr).validate_python(sender)
        return EmailConfig(origin, host, port, security, username, password, sender, timeout)
    except (KeyError, ValueError):
        raise HTTPException(503, 'Password recovery is temporarily unavailable. Please try again later.') from None


def send_reset_email(config: EmailConfig, recipient: str, token: str):
    # Fragment is never sent in the frontend HTTP request or Referer header.
    link = f'{config.origin}/reset-password#token={token}'
    message = EmailMessage()
    message['Subject'] = 'Reset your Vernaculearn password'
    message['From'] = config.sender
    message['To'] = recipient
    message.set_content(
        f'Use this single-use link to reset your password within 30 minutes:\n\n{link}\n\n'
        'If you did not request this, ignore this email. Your password has not changed.\n'
        'After a successful reset you will need to sign in again on your devices.\n'
    )
    context = ssl.create_default_context()
    if config.security == 'ssl':
        smtp = smtplib.SMTP_SSL(config.host, config.port, timeout=config.timeout, context=context)
    else:
        smtp = smtplib.SMTP(config.host, config.port, timeout=config.timeout)
    with smtp:
        if config.security == 'starttls':
            smtp.ehlo()
            smtp.starttls(context=context)
            smtp.ehlo()
        smtp.login(config.username, config.password)
        if smtp.send_message(message):
            raise smtplib.SMTPException('Recipient refused')
