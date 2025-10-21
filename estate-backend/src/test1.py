import asyncio
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.hash.selector import get_selector_from_name

client = FullNodeClient("https://starknet-sepolia.public.blastapi.io/rpc/v0_8")

CONTRACT_ADDRESS = "0x0696e1ba36b1b46ccfda4a6ae963b12c932e36d1a1008d5d0a03033b12d86827"
EVENT_NAME = "Transfer"
EVENT_KEY = get_selector_from_name(EVENT_NAME)

def decode_uint256(data):
    """Decode uint256 from two felt values (low, high)"""
    return data[0] + (data[1] << 128)

async def poll_events():
    latest_block = await client.get_block(block_number="latest")
    last_checked_block = latest_block.block_number - 1

    while True:
        events_response = await client.get_events(
            address=CONTRACT_ADDRESS,
            keys=[[EVENT_KEY]],
            from_block_number=last_checked_block + 1,
            to_block_number="latest",
            follow_continuation_token=True,
            chunk_size=100
        )

        for event in events_response.events:
            # Extract addresses from keys (skip the first key, which is event selector)
            from_addr = hex(event.keys[1])
            to_addr = hex(event.keys[2])

            # Decode amount from data (two felts for uint256)
            amount = decode_uint256(event.data)

            print(f"📥 New Transfer event:")
            print(f"    From: {from_addr}")
            print(f"    To: {to_addr}")
            print(f"    Amount: {amount}")

        if events_response.events:
            last_checked_block = max(e.block_number for e in events_response.events)

        await asyncio.sleep(1)

asyncio.run(poll_events())
