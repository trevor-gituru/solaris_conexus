# src/utils/exception_handlers/request_handlers.py
import requests
import json
from requests.exceptions import ConnectionError, Timeout, RequestException
from src.utils.loggers import central_logger


class CentralRequestsHandler:
    @staticmethod
    def handle(request_fn, *args, **kwargs):
        try:
            response = request_fn(*args, **kwargs)
            if response.status_code != 200:
                try:
                    error_msg = response.json().get("detail", response.text)
                except json.JSONDecodeError:
                    error_msg = response.text
                central_logger.error(f"Request failed: {error_msg}")
                return None

            try:
                return response.json()
            except json.JSONDecodeError:
                central_logger.error("Response is not valid JSON")
                return None

        except ConnectionError:
            central_logger.error("Connection refused — is central backend running?")
        except Timeout:
            central_logger.error("Connection timed out when trying to connect to central backend.")
        except RequestException as e:
            central_logger.error(f"Request failed: {e}")
        except Exception:
            central_logger.exception("Unexpected error during request")
        return None

    @staticmethod
    def get_value(key: str, request_fn, *args, **kwargs):
        """Call `handle()` and extract a specific key's value from the response."""
        response = CentralRequestsHandler.handle(request_fn, *args, **kwargs)
        if not response:
            raise ValueError("Request failed or returned no response")

        value = response.get(key)
        if value is None:
            raise ValueError(f"Key '{key}' not found in response")
        return value
