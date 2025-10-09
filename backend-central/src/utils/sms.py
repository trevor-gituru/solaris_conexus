# src/utils/sms.py
import africastalking
from datetime import datetime

from src.config import settings
from src.utils.logging import logger  # Import the logger


class SmsClient:
    def __init__(self):
        africastalking.initialize(settings.SMS_USERNAME, settings.SMS_API)
        self.sms = africastalking.SMS

    def sending(self, recipient, message):
        try:
            response = self.sms.send(message, recipient)
            recipients = response.get("SMSMessageData", {}).get("Recipients", [])

            if not recipients:
                logger.error("No recipients returned in SMS response.")
                return 1

            status = recipients[0].get("status")
            statusCode = recipients[0].get("statusCode")

            if statusCode == 100:
                logger.info(f"Successfully sent SMS to {recipient}: {status}")
                return 0

            logger.warning(
                f"Error sending SMS to {recipient}: {status} (Code: {statusCode})"
            )
            return 1

        except Exception as e:
            logger.exception(f"SMS server error while sending to {recipient}: {e}")
            return 2

    def send_trade_accept(self, trade):
        trade_dict = trade.to_dict()
        date_obj = datetime.fromisoformat(trade_dict["date"])
        formatted_date = date_obj.strftime("%B %d, %Y at %I:%M %p")  # e.g., June 09, 2025 at 09:49 PM

        # Extract fields
        sct_offered = trade_dict["sct_offered"]
        strk_price = trade_dict["strk_price"]
        buyer = trade_dict["buyer"]
        phone_number = trade.user.profile.phone2

        # Compose message
        message = (
            f"Your trade on {formatted_date} has been accepted by {buyer}. "
        f"You offered {sct_offered} SCT for {strk_price} STRK. Visit Solaris Conexus for details."
        )
        recipient = ["+254" + phone_number[1:]]
        return self.sending(recipient, message)

    def send_token_consumption(self, req):
        # Extract fields
        phone_number = req.get("phone")
        # Compose message
        message = (
            f"Youre device {req.get('device_id')} has consumed 1 SCT. New token balance is {req.get('balance')} SCT."
        f"Transaction is {req.get('tx_hash')}. Visit Solaris Conexus for details."
        )
        recipient = ["+254" + phone_number[1:]]
        return self.sending(recipient, message)


sms_client = SmsClient()
if __name__ == "__main__":
    from src.db.models import TradeRequest  # Import User model explicitly
    from src.db.database import get_db

    db = next(get_db())
    trade = TradeRequest.find(db, trade_id=52)

    if trade.user.profile.notification == 'sms':
        sms_client.send_trade_accept(trade)
