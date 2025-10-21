# src/utils/starknet/sct.py
import asyncio
from starknet_py.net.account.account import Account, KeyPair
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models.chains import StarknetChainId
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.contract import Contract
from src.utils.loggers import starknet_logger

from src.config import settings
from src.db.models import Device
from src.db.database import get_db
from .abi import sct_abi

from src.utils.exception_handlers.function_handlers import starknet_fn_handler
from src.utils.helpers import addr_owner 

class StarknetSCT:
    def __init__(
        self,
        rpc_url: str = settings.STARKNET_RPC_URL,
        account_address: str = settings.STARKNET_ACCOUNT_ADDRESS,
        private_key: int = settings.STARKNET_PRIVATE_KEY,
        contract_address: str = settings.SCT_CONTRACT_ADDRESS,
        abi=sct_abi,
        chain_id=StarknetChainId.SEPOLIA,
        cairo_version=1,
    ):
        self.client = FullNodeClient(node_url=rpc_url)
        self.account = Account(
            client=self.client,
            address=account_address,
            key_pair=KeyPair.from_private_key(private_key),
            chain=chain_id,
        )
        self.contract = Contract(
            address=contract_address,
            abi=abi,
            provider=self.account,
            cairo_version=cairo_version,
        )
        self.running = False

    async def balanceOf(self, account_address: str, device_id: str) -> int:
        try:
            (saved,) = await self.contract.functions["balanceOf"].call(int(account_address, 16))
            starknet_logger.info(f"Fetched balance of [{device_id}]:  {saved} SCT")
            return saved
        except Exception as e:
            raise ValueError(f"Failed to fetch balance for [{device_id}]: {e}")

    async def get_balances(self, account_addresses: list[list[str, str]]) -> dict[str, int]:
        """
        Fetch balances for multiple account addresses concurrently.
        Returns a dictionary mapping address -> balance.
        """
        try:
            tasks = [
                self.balanceOf(address[0], address[1])
                for address in account_addresses
            ]
            balances = await asyncio.gather(*tasks)
            results = {}
            for address, balance in zip(account_addresses, balances):
                results[address[0]] = balance

            return results

        except Exception as e:
            raise ValueError(f"Failed to fetch multiple balances: {e}")

    

    async def consume(self, account: str, device_id: str) -> str:
        account_address = int(account, 16)
        try:
            invocation = await self.contract.functions["consume"].invoke_v3(
                account=account_address,
                amount=1,
                auto_estimate=True,
            )
            await invocation.wait_for_acceptance()
            result = hex(invocation.hash)
            starknet_logger.info(f"[{device_id}] - [Consumed] - 1 SCT - {result}")
            return result 
        except Exception as e:
            raise ValueError(f"Error during contract invocation: {e}")


    async def poll_transfer_events(self, interval: int = 1):
        """Poll Transfer events emitted by the contract."""
        event_name = "Transfer"
        event_key = get_selector_from_name(event_name)
        contract_address = self.contract.address

        try:
            self.running = True
            latest_block = await self.client.get_block(block_number="latest")
            last_checked_block = latest_block.block_number - 1
            starknet_logger.info("Started polling for Transfer events")
            while self.running:
                await asyncio.sleep(interval)
                try:
                    with get_db() as db:
                        events_response = await self.client.get_events(
                            address=contract_address,
                            keys=[[event_key]],
                            from_block_number=last_checked_block + 1,
                            to_block_number="latest",
                            follow_continuation_token=True,
                            chunk_size=5
                        )
                        for event in events_response.events:
                            from_addr = hex(event.keys[1])
                            to_addr = hex(event.keys[2])
                            amount = self.decode_uint256(event.data)
                            devices = Device.from_transfer_event(db, [from_addr, to_addr])
                            if devices == []:
                                continue
                            starknet_logger.info(
                                f"Transfer Event Deteced | From: {addr_owner(from_addr, devices)} | "
                                    f"To: {addr_owner(to_addr, devices)} | Amount: {amount} | Block: {event.block_number}"
                            )
                            addresses = [[d.account_address, d.device_id] for d in devices]
                            balances = await self.get_balances(addresses)
                            for dev in devices:
                                token_balance = balances.get(dev.account_address)
                                dev.update(db, {"token_balance": token_balance})
                            starknet_logger.info(
                                f"Updated Token Balances for {[d.device_id for d in devices]}"
                            )
                        if events_response.events:
                            last_checked_block = max(e.block_number for e in events_response.events)
                

                except Exception as e:
                    starknet_logger.error(f"Error polling events: {e}")
                    self.stop()
        except asyncio.CancelledError:
            starknet_logger.info("Polling task cancelled gracefully.")
            raise  # Important: re-raise to allow outer cleanup

    def decode_uint256(self, data: list[int]) -> int:
        """Decode StarkNet uint256 from felt array [low, high]"""
        if len(data) < 2:
            return 0
        return data[0] + (data[1] << 128)

    def stop(self):
        self.running = False


    

sct_client = StarknetSCT()

# At the end of sct.py
if __name__ == "__main__":
    import time
    from src.utils.exception_handlers.function_handlers import starknet_fn_handler
    from src.mqtt.client import mqtt_client

    try:
        mqtt_client.start()
        starknet_fn_handler.run(sct_client.poll_transfer_events)
    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected. Shutting down...")
        sct_client.stop()
        mqtt_client.stop()
        time.sleep(5)
        starknet_fn_handler.shutdown()
    finally:
        print("✅ Shutdown complete.")
                
