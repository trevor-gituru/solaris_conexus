# src/utils/helpers.py
from src.config import settings
import threading

def normalize_addr(addr: str) -> str:
    if addr and addr.startswith("0x"):
        hex_part = addr[2:].rjust(64, "0")  # ensure 64 hex chars
        return "0x" + hex_part
    return addr

def addr_owner(account_address: str,  devices) -> str:
    addr = normalize_addr(account_address)
    for dev in devices:
        if addr == settings.SCT_CONTRACT_ADDRESS or addr == settings.SCT_OWNER:
            return "[Smart Contract]"
        if addr == dev.account_address:
            return f"[{dev.device_id}]"
    return account_address 

def short_address(addr: str, start=6, end=4) -> str:
    if addr.startswith("0x"):
        return f"{addr[:start+2]}...{addr[-end:]}"
    return f"{addr[:start]}...{addr[-end:]}"


def start_daemon_thread(target_fn, *args, **kwargs):
    """
    Helper to start a daemon thread for any target function with arguments.
    Returns the thread object.
    """
    t = threading.Thread(target=target_fn, args=args, kwargs=kwargs, daemon=True)
    t.start()
    return t
