from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, timezone

logger = logging.getLogger("email_service")

class BaseEmailProvider(ABC):
    @abstractmethod
    async def send_email(self, to_email: str, subject: str, html_body: str, text_body: str) -> bool:
        pass

class ConsoleEmailProvider(BaseEmailProvider):
    """
    Console/Memory email provider for local development, CI pipelines, and unit tests.
    Does not require external API credentials.
    """
    def __init__(self):
        self.sent_emails: List[Dict[str, Any]] = []

    async def send_email(self, to_email: str, subject: str, html_body: str, text_body: str) -> bool:
        email_record = {
            "to": to_email,
            "subject": subject,
            "text": text_body,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.sent_emails.append(email_record)
        logger.info(f"[EMAIL DISPATCH] To: {to_email} | Subject: '{subject}'")
        return True

class EmailService:
    def __init__(self, provider: Optional[BaseEmailProvider] = None):
        self.provider = provider or ConsoleEmailProvider()

    async def send_verification_email(self, to_email: str, full_name: str, raw_token: str) -> bool:
        verify_url = f"http://localhost:3000/verify-email?token={raw_token}"
        subject = "Verify your FluentMeet AI account"
        text_body = f"Hello {full_name},\n\nPlease verify your email address by clicking the link below (valid for 30 minutes):\n{verify_url}\n\nIf you didn't create an account, you can safely ignore this email."
        html_body = f"<p>Hello {full_name},</p><p>Please <a href='{verify_url}'>click here to verify your email address</a> (valid for 30 minutes).</p>"
        return await self.provider.send_email(to_email, subject, html_body, text_body)

    async def send_password_reset_email(self, to_email: str, full_name: str, raw_token: str) -> bool:
        reset_url = f"http://localhost:3000/reset-password?token={raw_token}"
        subject = "Reset your FluentMeet AI password"
        text_body = f"Hello {full_name},\n\nYou requested to reset your password. Click the link below to set a new password (valid for 30 minutes):\n{reset_url}\n\nIf you did not request this, please secure your account immediately."
        html_body = f"<p>Hello {full_name},</p><p>You requested to reset your password. <a href='{reset_url}'>Click here to set a new password</a>.</p>"
        return await self.provider.send_email(to_email, subject, html_body, text_body)

    async def send_password_changed_notification(self, to_email: str, full_name: str) -> bool:
        subject = "Security Alert: Your FluentMeet AI password was changed"
        text_body = f"Hello {full_name},\n\nYour account password was successfully changed. If this wasn't you, contact support immediately."
        html_body = f"<p>Hello {full_name},</p><p>Your account password was successfully changed.</p>"
        return await self.provider.send_email(to_email, subject, html_body, text_body)

    async def send_organization_invitation(
        self,
        to_email: str,
        org_name: str,
        inviter_name: str,
        role: str,
        raw_token: str
    ) -> bool:
        invite_url = f"http://localhost:3000/invite/accept?token={raw_token}"
        subject = f"You've been invited to join {org_name} on FluentMeet AI"
        text_body = f"Hello,\n\n{inviter_name} has invited you to join '{org_name}' as a {role.capitalize()}.\n\nClick below to accept (valid for 7 days):\n{invite_url}"
        html_body = f"<p>Hello,</p><p>{inviter_name} has invited you to join <strong>{org_name}</strong> as a <strong>{role.capitalize()}</strong>.</p><p><a href='{invite_url}'>Accept Invitation</a></p>"
        return await self.provider.send_email(to_email, subject, html_body, text_body)

    async def send_role_changed_notification(self, to_email: str, org_name: str, new_role: str) -> bool:
        subject = f"Your role in {org_name} has been updated"
        text_body = f"Hello,\n\nYour role in '{org_name}' has been updated to {new_role.capitalize()}."
        html_body = f"<p>Hello,</p><p>Your role in <strong>{org_name}</strong> has been updated to <strong>{new_role.capitalize()}</strong>.</p>"
        return await self.provider.send_email(to_email, subject, html_body, text_body)

    async def send_account_deactivated_notification(self, to_email: str, full_name: str) -> bool:
        subject = "Your FluentMeet AI account has been deactivated"
        text_body = f"Hello {full_name},\n\nYour FluentMeet AI account has been deactivated as requested. If this was a mistake, please contact support."
        html_body = f"<p>Hello {full_name},</p><p>Your FluentMeet AI account has been deactivated as requested.</p>"
        return await self.provider.send_email(to_email, subject, html_body, text_body)

# Default singleton instance
email_service = EmailService()
