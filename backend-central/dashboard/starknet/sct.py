# services/starknet/buy_tokens.py

from starknet_py.net.account.account import Account, KeyPair
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models.chains import StarknetChainId
from starknet_py.contract import Contract
import asyncio
from .abi import sct_abi


# Configure your StarkNet account
client = FullNodeClient(
    node_url="https://starknet-sepolia.g.alchemy.com/starknet/version/rpc/v0_8/TZnwD5R59wzUZLADsAcjTBotxfzYN8dO"
)

account = Account(
    client=client,
    address="0x040dc3bb58168d641811d5a516760c9ba57ee7bf98c547fa3fb5fce71774d90b",
    key_pair=KeyPair.from_private_key(
        key="0x044a3fe666102135fd9ef67426d2ba01d8b8f252048b391b68042e93b14246bc"
    ),
    chain=StarknetChainId.SEPOLIA,
)

contract_address = "0x0696e1ba36b1b46ccfda4a6ae963b12c932e36d1a1008d5d0a03033b12d86827"

contract = Contract(address=contract_address, abi=sct_abi, provider=account, cairo_version=1)

async def buy_tokens(buyer_address: str, amount: int) -> str:
    """
    Buys tokens using the provided StarkNet address and amount.
    Returns the transaction hash.
    """

    # Convert buyer_address to int if it's in hex
    buyer_int = int(buyer_address, 16)
    
    # # Call the contract's 'buy' method
    # invocation = await contract.functions["buy"].invoke_v3(
    #     buyer=buyer_int,
    #     amount=amount,
    #     auto_estimate=True,
    # )

    # print("hi")
    try:
        # Call the contract's 'buy' method
        # Assuming amount is a Decimal like Decimal("10.5")
        invocation = await contract.functions["buy"].invoke_v3(
            buyer=buyer_int,
            amount=int(amount),
            auto_estimate=True,
        )
    except Exception as e:
        print(f"Error during contract invocation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to invoke contract: {str(e)}"
        )


    # Wait for transaction to be accepted
    await invocation.wait_for_acceptance()

    return hex(invocation.hash)

async def balanceOf(account_address: str):
     # Create contract from contract's address - Contract will download contract's ABI to know its interface.
    
    # Calling contract's function doesn't create a new transaction, you get the function's result.
    (saved,) = await contract.functions["balanceOf"].call(int(account_address, 16))
    return saved


async def signTrade(buyer_address: str, trade_id: int, amount: int) -> str:
    """
    Buys tokens using the provided StarkNet address and amount.
    Returns the transaction hash.
    """
    # Load contract from address

    buyer_int = int(buyer_address, 16)
    
    try:
        # Call the contract's 'buy' method
        # Assuming amount is a Decimal like Decimal("10.5")
        invocation = await contract.functions["signTrade"].invoke_v3(
            buyer=buyer_int,
            trade_id=int(trade_id),
            auto_estimate=True,
        )
        # Wait for transaction to be accepted
        await invocation.wait_for_acceptance()

        # Pay Trade
        invocation = await contract.functions["payTrade"].invoke_v3(
            trade_id=int(trade_id),
            amount=int(amount),
            auto_estimate=True,
        )
        # Wait for transaction to be accepted
        await invocation.wait_for_acceptance()


        return hex(invocation.hash)

    except Exception as e:
        print(f"Error during contract invocation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to invoke contract: {str(e)}"
        )

