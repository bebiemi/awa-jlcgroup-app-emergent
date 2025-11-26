"""Email provider abstraction"""
from abc import ABC, abstractmethod
from typing import List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

from src.infrastructure.config import get_settings

logger = logging.getLogger(__name__)


class EmailProvider(ABC):
    """Abstract email provider interface"""

    @abstractmethod
    async def send_email(
        self,
        to: List[str],
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """Send an email"""
        pass


class SMTPEmailProvider(EmailProvider):
    """SMTP email provider (Mailhog for dev, production SMTP for prod)"""

    def __init__(self):
        settings = get_settings()
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.from_email = settings.from_email
        self.from_name = settings.from_name

    async def send_email(
        self,
        to: List[str],
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """Send an email via SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = ', '.join(to)

            # Add text and HTML parts
            if text_body:
                part1 = MIMEText(text_body, 'plain')
                msg.attach(part1)

            part2 = MIMEText(html_body, 'html')
            msg.attach(part2)

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to, msg.as_string())

            logger.info(f"Email sent to {to}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to}: {e}")
            return False


class MockEmailProvider(EmailProvider):
    """Mock email provider for testing"""

    async def send_email(
        self,
        to: List[str],
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """Mock send email - just log"""
        logger.info(f"MOCK EMAIL to {to}: {subject}")
        logger.debug(f"Body: {html_body[:100]}...")
        return True


def get_email_provider() -> EmailProvider:
    """Get configured email provider"""
    env = get_settings().environment
    if env == 'test':
        return MockEmailProvider()
    return SMTPEmailProvider()
