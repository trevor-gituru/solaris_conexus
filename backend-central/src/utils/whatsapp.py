import requests
from datetime import datetime

class WhatsappClient:
    def __init__(self, token: str, phone_number_id: str):
        self.token = token
        self.phone_number_id = phone_number_id
        self.url = f'https://graph.facebook.com/v22.0/{phone_number_id}/messages'
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def send_trade_accepted(self, to: str, header_name: str, date: str, buyer: str, energy: str, price: str) -> int:
        """
        Sends a trade_accepted WhatsApp template message.
        Returns 1 if accepted, 0 otherwise.
        """
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": "trade_accepted",
                "language": { "code": "en" },
                "components": [
                    {
                        "type": "header",
                        "parameters": [
                            { "type": "text", "text": header_name }
                        ]
                    },
                    {
                        "type": "body",
                        "parameters": [
                            { "type": "text", "text": date },
                            { "type": "text", "text": buyer },
                            { "type": "text", "text": energy },
                            { "type": "text", "text": price }
                        ]
                    }
                ]
            }
        }

        response = requests.post(self.url, json=payload, headers=self.headers)
        data = response.json()

        try:
            message_status = data["messages"][0].get("message_status")
            return 1 if message_status == "accepted" else 0
        except (KeyError, IndexError, TypeError):
            return 0

    def send_trade_accept(self, trade) -> int:
        """
        Extracts trade details and sends a WhatsApp template message for trade acceptance.
        """
        trade_dict = trade.to_dict()
        date_obj = datetime.fromisoformat(trade_dict["date"])
        formatted_date = date_obj.strftime("%B %d, %Y")  # e.g., June 09, 2025

        # Extract fields
        sct_offered = trade_dict["sct_offered"]
        strk_price = trade_dict["strk_price"]
        buyer = trade_dict["buyer"]
        phone_number = trade.user.profile.phone2  # e.g., 0701342609

        # Format phone to international
        to = "254" + phone_number.lstrip("0")

        header_name = trade_dict["seller"] or "Trader"

        return self.send_trade_accepted(
            to=to,
            header_name=header_name,
            date=formatted_date,
            buyer=buyer,
            energy=str(sct_offered),
            price=str(strk_price)
        )

TOKEN = "EAAXQbgQVob0BO6tJ5MJFsuMFgkGL4rfiYjuZBZCLBAdLPJZCN9AnrmUKpWZC2AcbNnSZCwZBv7oIpY1YIwa80cgDwu2gEkXPsKOUk6uXhm0V2vyleZBqj2bQEZAibNYCe9P4TMAJBhnzyZAXybLMWhjk272qzIImNMGfTMS2SAxD44T5L2uhRVQkUeS95chzxlgZDZD"

PHONE_NUMBER_ID = "700727043121718"  # Replace with your actual phone number ID

# Example usage:
whatsapp_client = WhatsappClient(TOKEN, PHONE_NUMBER_ID)
if __name__ == "__main__":
    
    # result = client.send_trade_accepted(
    #     to="254701342609",
    #     header_name="gituru",
    #     date="12 July 2023",
    #     buyer="trevor",
    #     energy="2.00",
    #     price="1.00"
    # )
    # print(result)

    from src.db.models import TradeRequest  # Import User model explicitly
    from src.db.database import get_db

    db = next(get_db())
    trade = TradeRequest.find(db, trade_id=52)

    if trade.user.profile.notification == 'whatsapp':
        result = whatsapp_client.send_trade_accept(trade)
        print(result)
