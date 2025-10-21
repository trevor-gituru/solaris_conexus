# /src/central_api/client.py
import requests
from sqlalchemy.orm import Session
from src.config import settings
from src.db.models import Device
from src.starknet.sct import sct_client
from src.utils.loggers import central_logger
from src.utils.redis import central_token_client
from src.utils.exception_handlers.request_handlers import CentralRequestsHandler
from src.utils.exception_handlers.function_handlers import central_fn_handler 
from src.utils.exception_handlers.function_handlers import starknet_fn_handler
from requests.exceptions import ConnectionError, Timeout, RequestException


class CentralAPIClient:
    """Handles HTTP communication with central backend."""

    def __init__(
        self, base_url: str = settings.BACKEND_URL, api_key: str = settings.BACKEND_KEY
    ):
        self.base_url = f"{base_url}/hubs"
        self.params = {"api_key": api_key}


    def connect(self):
        central_logger.info("Attempting to fetch access token")
        url = f"{self.base_url}/connect"
        token = CentralRequestsHandler.get_value(
            "access_token", requests.post, url, params=self.params, timeout=10
        )
        central_token_client.set(token)
        central_logger.info("Successfully retieved access token")

    async def sync_devices(self, db: Session):
        central_logger.info("Attempting to synchronize devices")
        url = f"{self.base_url}/sync_devices"
        token = central_token_client.get()
        headers = {
            "Authorization": f"Bearer {token}"
        }
        devices = CentralRequestsHandler.get_value(
            "data", requests.get, url, timeout=10, headers=headers
        )
        central_logger.info(f"Found {len(devices)} devices: {[d.get('device_id') for d in devices]}")
        addresses = [[d.get("account_address"), d.get("device_id")] for d in devices]
        balances = await sct_client.get_balances(addresses)

        for device in devices:
            device["token_balance"] = balances.get(device["account_address"])
            Device.sync(db, device)

        central_logger.info("Device synchronization completed.")
    
    def shutdown(self, db: Session):
        central_logger.info("Attempting to shutdown connection")
        url = f"{self.base_url}/shutdown"
        token = central_token_client.get()
        headers = {
            "Authorization": f"Bearer {token}"
        }
        message = CentralRequestsHandler.get_value(
            "message", requests.post, url, timeout=10, headers=headers
        )
        Device.set_all_inactive(db)
        central_logger.info(message)

    def activate_device(self, db: Session, device_id: str):
        central_logger.info(f"Attempting to activate device {device_id}")
        url = f"{self.base_url}/activate_device"
        token = central_token_client.get()
        headers = {
            "Authorization": f"Bearer {token}"
        }
        data = {"device_id": device_id}
        message = CentralRequestsHandler.get_value(
            "message", requests.post, url, json=data, timeout=10, headers=headers
        )
        device = Device.find(db, device_id=device_id)
        device.update(db, {"status": "active"})
        central_logger.info(message)

    def deactivate_device(self, db: Session, device_id: str):
        central_logger.info(f"Attempting to deactivate device {device_id}")
        url = f"{self.base_url}/deactivate_device"
        token = central_token_client.get()
        headers = {
            "Authorization": f"Bearer {token}"
        }
        data = {"device_id": device_id}
        message = CentralRequestsHandler.get_value(
            "message", requests.post, url, json=data, timeout=10, headers=headers
        )
        device = Device.find(db, device_id=device_id)
        device.update(db, {"status": "inactive"})
        central_logger.info(message)

    def consume_token(self, consumption_dict: str):
        central_logger.info(f"[Notification] - [Power consumption] - {consumption_dict.get("device_id")}")
        url = f"{self.base_url}/token_consumption"
        token = central_token_client.get()
        headers = {
            "Authorization": f"Bearer {token}"
        }
        message = CentralRequestsHandler.get_value(
            "message", requests.post, url, json=consumption_dict, timeout=10, headers=headers
        )
        central_logger.info(message)


central_client = CentralAPIClient()
if __name__ == "__main__":
    from src.db.database import get_db

    central_fn_handler.call(central_client.connect)
    with get_db() as db:
        # central_fn_handler.run(central_client.sync_devices, db)
        central_fn_handler.run(central_client.deactivate_device, db, "H001")
        # central_fn_handler.run(central_client.shutdown, db)
