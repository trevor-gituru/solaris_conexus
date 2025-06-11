# src/utils/notifications.py

from src.utils.sms import sms_client
from src.utils.email import email_client
from src.utils.logging import logger


class NotificationManager:
    def __init__(self, sms_client=sms_client, email_client=email_client):
        self.sms_client = sms_client
        self.email_client = email_client

    def notify_trade_accepted(self, trade):
        user = trade.user
        method = user.profile.notification

        logger.info(f"Sending trade accepted notification to {user.username} via {method}")

        if method == "sms":
            phone = user.profile.phone2
            status = self.sms_client.send_trade_accept(trade)
            if status == 0:
                return
            else:
                return self.email_client.send_trade_accept(trade)

        elif method == "email":
            return self.email_client.send_trade_accept(trade)

        elif method == "":
            logger.info(f"User {user.username} has notifications disabled.")
            return None

        else:
            logger.warning(f"Unknown notification method '{method}' for user {user.username}")
            return None

# Singleton-style instance
notification_manager = NotificationManager()
if __name__ == "__main__":
    from src.db.models import TradeRequest  # Import User model explicitly
    from src.db.database import get_db

    db = next(get_db())
    trade = TradeRequest.find(db, trade_id=52)
    notification_manager.notify_trade_accepted(trade)



