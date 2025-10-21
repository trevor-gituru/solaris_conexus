# /src/utils/redis.py
import redis
from src.config import settings

class RedisClient:
    def __init__(self):
        self.client = redis.from_url(settings.REDIS_URL, decode_responses=True)

    def set(self, key: str, value: str, expires_in: int = 3600):
        """Set a key with expiration."""
        self.client.setex(key, expires_in, value)

    def get(self, key: str) -> str | None:
        """Get the value for a key."""
        return self.client.get(key)

    def delete(self, key: str):
        """Delete a key."""
        self.client.delete(key)


class CentralTokenClient(RedisClient):
    def __init__(self):
        super().__init__()
        self.key = "central_access_token"

    def set(self, token: str, expires_in: int = 3600):
        super().set(self.key, token, expires_in)

    def get(self) -> str:
        value = super().get(self.key)
        if value is None:
            raise ValueError("Access token is missing from Redis")
        return value

    def delete(self):
        super().delete(self.key)

class ArduinoPortClient(RedisClient):
    def __init__(self):
        super().__init__()
        self.key = "arduino_ports"

    def set(self, port: str):
        """Add a port to the set of active Arduino ports."""
        self.client.sadd(self.key, port)

    def delete(self, port: str):
        """Remove a port from the set of active Arduino ports."""
        self.client.srem(self.key, port)

    def get(self) -> list[str]:
        """Get all currently active Arduino ports."""
        return list(self.client.smembers(self.key))

    def clear(self):
        """Clear all tracked ports."""
        self.client.delete(self.key)

class PowerClient(RedisClient):
    def __init__(self, device_id):
        super().__init__()
        self.key = f"power_accumulated_{device_id}"

    def set(self, power):
        """Add a port to the set of active Arduino ports."""
        self.client.incrbyfloat(self.key, power)

    def delete(self, port: str):
        """Remove a port from the set of active Arduino ports."""
        super().delete(self.key)

    def get(self) -> list[str]:
        """Get all currently active Arduino ports."""
        return float(super().get(self.key) or 0)

    def reset(self, power):
        """Add a port to the set of active Arduino ports."""
        self.client.set(self.key, power)
    
# Singleton instance
central_token_client = CentralTokenClient()
arduino_port_client = ArduinoPortClient()
