# /src/starknet/stark.py
from config import NODE_URL, WALLET_ADDRESS, WALLET_PUB, WALLET_PRIV, SCT_ADDRESS
from starknet_py.net.account.account import Account, KeyPair
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models.chains import StarknetChainId
from starknet_py.contract import Contract
import asyncio
from .abi import contract_abi

# Configure your StarkNet account
client = FullNodeClient(
    node_url=NODE_URL
)

account = Account(
    client=client,
    address=WALLET_ADDRESS,
    key_pair=KeyPair.from_private_key(
        key=WALLET_PRIV
    ),
    chain=StarknetChainId.SEPOLIA,
)

contract_address = SCT_ADDRESS

# When ABI is known statically just use the Contract constructor
contract = Contract(address=contract_address, abi=contract_abi, provider=account, cairo_version=1)

async def balanceOf(account_address: str) -> int:
     
    # Calling contract's function doesn't create a new transaction, you get the function's result.
    (saved,) = await contract.functions["balanceOf"].call(int(account_address, 16))
    return saved


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




async def signTrade(buyer_address: str, trade_id: int, amount: int) -> str:
    """
    Buys tokens using the provided StarkNet address and amount.
    Returns the transaction hash.
    """
    
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


