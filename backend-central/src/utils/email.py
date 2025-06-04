# src/utils/email.py
from nylas import Client
from src.config import settings

class EmailClient:
    def __init__(self, api_key=None, api_uri=None, grant_id=None):
        self.api_key = api_key or settings.NYLAS_API_KEY
        self.api_uri = api_uri or settings.NYLAS_API_URI
        self.grant_id = grant_id or settings.NYLAS_GRANT_ID
        self.client = Client(api_key=self.api_key, api_uri=self.api_uri)

    def send_email(self, subject: str, body: str, to_name: str, to_email: str):
        email_payload = {
            "subject": subject,
            "body": body,
            "to": [{"name": to_name, "email": to_email}]
        }
        try:
            message = self.client.messages.send(self.grant_id, request_body=email_payload).data
            return message
        except Exception as e:
            return str(e)

    def send_confirmation_email(self, to_name: str, to_email: str, confirmation_code: str):
        body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: auto; padding: 20px;">
              <h2 style="color: #4CAF50;">Email Confirmation</h2>
              <p>Hi {to_name},</p>
              <p>Thank you for signing up with Solaris Connexus!</p>
              <p>Please confirm your email address by copying and entering the following code:</p>
              <div style="text-align: center; margin: 30px 0;">
                <span style="font-size: 24px; font-weight: bold; color: #4CAF50;">{confirmation_code}</span>
              </div>
              <p>If you did not request this email, you can safely ignore it.</p>
              <p>Best regards,<br>The Solaris Connexus Team</p>
              <hr style="margin-top: 40px;">
              <p style="font-size: 12px; color: #999;">This is an automated message. Please do not reply directly to this email.</p>
            </div>
          </body>
        </html>
        """
        return self.send_email(
            subject="RE: Confirmation Email",
            body=body,
            to_name=to_name,
            to_email=to_email
        )

# Create a singleton instance if preferred
email_client = EmailClient()

