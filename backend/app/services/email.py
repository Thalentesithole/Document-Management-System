import httpx
from abc import ABC, abstractmethod
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class EmailProvider(ABC):
    @abstractmethod
    async def send_email(self, to_email: str, subject: str, text_body: str, html_body: str) -> bool:
        pass

class ResendEmailProvider(EmailProvider):
    def __init__(self, api_key: str, from_email: str):
        self.api_key = api_key
        self.from_email = from_email
        self.api_url = "https://api.resend.com/emails"

    async def send_email(self, to_email: str, subject: str, text_body: str, html_body: str) -> bool:
        if not self.api_key:
            logger.warning(f"Resend API key missing. Mocking email to {to_email}")
            return True

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "from": self.from_email,
            "to": [to_email],
            "subject": subject,
            "text": text_body,
            "html": html_body
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.api_url, json=payload, headers=headers)
                response.raise_for_status()
                logger.info(f"Email sent successfully to {to_email}")
                return True
            except httpx.HTTPError as e:
                logger.error(f"Failed to send email to {to_email}: {str(e)}")
                return False

class MockEmailProvider(EmailProvider):
    async def send_email(self, to_email: str, subject: str, text_body: str, html_body: str) -> bool:
        logger.info(f"Mock email sent to {to_email} with subject: {subject}")
        # Intentionally NOT printing the link to logs to satisfy the security requirement
        return True

class EmailService:
    def __init__(self):
        if settings.EMAIL_PROVIDER.lower() == "resend" and settings.RESEND_API_KEY:
            self.provider = ResendEmailProvider(settings.RESEND_API_KEY, settings.SMTP_FROM_EMAIL)
        else:
            self.provider = MockEmailProvider()

    async def send_password_reset(self, to_email: str, reset_link: str) -> bool:
        subject = "Reset Your Password"
        
        text_body = f"""Hello,

We received a request to reset your password.

Click the link below to create a new password:

{reset_link}

This link expires in 30 minutes.

If you did not request this reset, you can safely ignore this email.

Regards,
Document Management System Team
"""
        
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>Reset Your Password</h2>
            <p>Hello,</p>
            <p>We received a request to reset your password.</p>
            <p>Click the button below to create a new password:</p>
            <p style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}" style="background-color: #4f46e5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">Reset Password</a>
            </p>
            <p>This link expires in 30 minutes.</p>
            <p>If you did not request this reset, you can safely ignore this email.</p>
            <br/>
            <p>Regards,<br/>Document Management System Team</p>
        </div>
        """
        
        return await self.provider.send_email(to_email, subject, text_body, html_body)

email_service = EmailService()
