# utils/redis.py
import redis
import json
from decimal import Decimal

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
        self.client = redis.Redis(
            host="localhost",   # default
            port=6379,          # default
            db=0,               # default
            decode_responses=True  # so it returns strings, not bytes
        )

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
