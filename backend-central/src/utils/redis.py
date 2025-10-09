# utils/redis.py
import redis
import json
from decimal import Decimal
from src.config import settings

from decimal import Decimal
from datetime import datetime

def convert_json_safe(obj):
    if isinstance(obj, dict):
        return {k: convert_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_json_safe(i) for i in obj]
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    return obj

class RedisClient:
    def __init__(self):
        self.client = redis.from_url(settings.REDIS_URL, decode_responses=True)

    def store_mpesa(self, user_id: int, data: dict, expiry: int = 3600):
        """
        Stores M-PESA transaction data for a user.
        Key format: mpesa_user_{user_id}
        """
        key = f"mpesa_user_{user_id}"
        value = json.dumps(convert_json_safe(data))
        self.client.set(key, value, ex=expiry)

    def fetch_mpesa(self, user_id: int):
        """
        Retrieves M-PESA transaction data for a user.
        Returns dict or None.
        """
        key = f"mpesa_user_{user_id}"
        value = self.client.get(key)
        return json.loads(value) if value else None

    def delete_mpesa(self, user_id: int):
        """
        Deletes M-PESA transaction data for a user.
        Returns 1 existed or 0.
        """
        key = f"mpesa_user_{user_id}"
        self.client.delete(key)

redis_client = RedisClient()

# 🔹 Test connection when run directly
if __name__ == "__main__":
    try:
        print(settings.REDIS_URL)
        test_key = "test_key"
        test_value = {"msg": "Hello from Upstash Redis!"}

        # Set the key
        redis_client.client.set(test_key, json.dumps(test_value))
        print(f"✅ Successfully set key: {test_key}")

        # Get the key
        result = redis_client.client.get(test_key)
        print(f"🔹 Retrieved value: {result}")

        # Optional: delete it
        redis_client.client.delete(test_key)
        print("🧹 Test key deleted.")

    except Exception as e:
        print("❌ Redis connection failed:", e)
