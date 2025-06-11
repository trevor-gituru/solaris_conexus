# src/utils/email.py
from nylas import Client
from datetime import datetime
from src.config import settings
from src.utils.logging import logger


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
            "to": [{"name": to_name, "email": to_email}],
        }
        try:
            message = self.client.messages.send(
                self.grant_id, request_body=email_payload
            ).data
            logger.info(f"Email sent to {to_name} <{to_email}> with subject '{subject}'")
            return message
        except Exception as e:
            return str(e)

    def send_confirmation_email(
        self, to_name: str, to_email: str, confirmation_code: str
    ):
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
            to_email=to_email,
        )



    def send_trade_accept(self, trade):
        to_name = trade.user.username
        to_email = trade.user.email
        trade_dict = trade.to_dict()

        # Format trade date
        date_obj = datetime.fromisoformat(trade_dict["date"])
        formatted_date = date_obj.strftime("%B %d, %Y at %I:%M %p")  # e.g. June 09, 2025 at 09:49 PM

        sct_offered = trade_dict["sct_offered"]
        strk_price = trade_dict["strk_price"]
        buyer = trade_dict["buyer"]
        tx_data = trade_dict.get("tx_data", {})
        pay_accept_tx = tx_data.get("pay_accept")

        # Fallback in case tx is missing
        tx_link = f"https://sepolia.starkscan.co/tx/{pay_accept_tx}" if pay_accept_tx else "#"
        site_link = f"{settings.FRONTEND_URL}/auth/login"

        body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: auto; padding: 20px;">
              <h2 style="color: #4CAF50;">Trade Accepted</h2>
              <p>Hi {to_name},</p>
              <p>Your trade on <strong>{formatted_date}</strong> has been <strong>accepted</strong> by <strong>{buyer}</strong>.</p>
              <p>Details of the trade:</p>
              <ul>
                <li><strong>SCT Offered:</strong> {sct_offered}</li>
                <li><strong>STRK Price:</strong> {strk_price}</li>
                <li><strong>Payment Transaction:</strong> 
                  <a href="{tx_link}" style="color: #4CAF50; text-decoration: none;" target="_blank">
                    View on StarkScan
                  </a>
                </li>
              </ul>
              <p>You can <a href="{site_link}" style="color: #4CAF50; text-decoration: none;" target="_blank">log in</a> to your Solaris Conexus account for full trade details.</p>
              <p>Best regards,<br>The Solaris Conexus Team</p>
              <hr style="margin-top: 40px;">
              <p style="font-size: 12px; color: #999;">This is an automated message. Please do not reply directly to this email.</p>
            </div>
          </body>
        </html>
        """

        return self.send_email(
            subject="Your Trade Has Been Accepted",
            body=body,
            to_name=to_name,
            to_email=to_email
        )


# Create a singleton instance if preferred
email_client = EmailClient()

if __name__ == "__main__":
    from src.db.models import TradeRequest  # Import User model explicitly
    from src.db.database import get_db

    db = next(get_db())
    trade = TradeRequest.find(db, trade_id=52)

    if trade.user.profile.notification == "email":
        email_client.send_trade_accept(trade)
