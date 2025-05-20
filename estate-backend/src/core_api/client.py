# /src/core_api/client.py
import requests
from db.database import SessionLocal
from db.models import Device
from config import BACKEND_URL, BACKEND_KEY

import asyncio
from starknet.stark import balanceOf  # your async balance checker

def fetch_and_store_devices():
    url = f"{BACKEND_URL}/hubs/devices"
    params = {"api_key": BACKEND_KEY}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("Failed to fetch devices:", response.text)
        return

    devices = response.json().get("devices", [])
    db = SessionLocal()

    # Prepare map for devices with account_address
    address_to_device = {}
    for d in devices:
        acct_addr = d.get("account_address")
        if acct_addr:
            address_to_device[acct_addr] = d

    # Batch get balances using asyncio
    async def fetch_balances(addresses):
        tasks = [balanceOf(addr) for addr in addresses]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return dict(zip(addresses, results))

    balances = asyncio.run(fetch_balances(list(address_to_device.keys())))

    try:
        for d in devices:
            device_id = d["device_id"]
            acct_addr = d.get("account_address", "")
            token_balance = balances.get(acct_addr) if acct_addr else None
            if isinstance(token_balance, Exception):
                print(f"Error fetching balance for {acct_addr}:", token_balance)
                token_balance = None

            # Check if device exists
            existing = db.query(Device).filter(Device.device_id == device_id).first()
            if existing:
                existing.id = d["id"]
                existing.device_type = d["device_type"]
                existing.connection_type = d["connection_type"]
                existing.status = d["status"]
                existing.pin_loads = d["pin_loads"]
                existing.account_address = acct_addr
                if token_balance is not None:
                    existing.token_balance = token_balance
            else:
                new_device = Device(
                    id=d['id'],
                    device_type=d["device_type"],
                    device_id=device_id,
                    connection_type=d["connection_type"],
                    status=d["status"],
                    pin_loads=d["pin_loads"],
                    account_address=acct_addr,
                    token_balance=token_balance or 0
                )
                db.add(new_device)

        db.commit()
        print(f"Fetched and stored {len(devices)} devices.")
    except Exception as e:
        print("Error saving devices:", e)
        db.rollback()
    finally:
        db.close()

