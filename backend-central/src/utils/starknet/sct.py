# src/utils/starknet/sct.py

from starknet_py.net.account.account import Account, KeyPair
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models.chains import StarknetChainId
from starknet_py.contract import Contract

from src.config import settings
from .abi import sct_abi


# Configure your StarkNet account
client = FullNodeClient(
    node_url=settings.STARKNET_RPC_URL
)

account = Account(
    client=client,
    address=settings.STARKNET_ACCOUNT_ADDRESS,
    key_pair=KeyPair.from_private_key(
        key=settings.STARKNET_PRIVATE_KEY
    ),
    chain=StarknetChainId.SEPOLIA,
)

contract_address = settings.SCT_CONTRACT_ADDRESS
contract = Contract(address=contract_address, abi=sct_abi, provider=account, cairo_version=1)


async def buy_tokens(buyer_address: str, amount: int) -> str:
    """
    Buys tokens using the provided StarkNet address and amount.
    Returns the transaction hash.
    """
    buyer_int = int(buyer_address, 16)

    try:
        invocation = await contract.functions["buy"].invoke_v3(
            buyer=buyer_int,
            amount=int(amount),
            auto_estimate=True,
        )
    except Exception as e:
        raise RuntimeError(f"Contract invocation failed: {e}")

    await invocation.wait_for_acceptance()
    return hex(invocation.hash)


async def balanceOf(account_address: str) -> int:
    """
    Returns the token balance of the given StarkNet address.
    """
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

        # # Pay Trade
        # invocation = await contract.functions["payTrade"].invoke_v3(
        #     trade_id=int(trade_id),
        #     amount=int(amount),
        #     auto_estimate=True,
        # )
        # # Wait for transaction to be accepted
        # await invocation.wait_for_acceptance()


        return hex(invocation.hash)

    except Exception as e:
        raise RuntimeError(f"{str(e)}")

async def transfer(buyer_address: str, amount: int) -> str:
    """
    Transfer tokens using the provided StarkNet address and amount.
    Returns the transaction hash.
    """
    # Load contract from address

    buyer_int = int(buyer_address, 16)
    
    try:
        # Call the contract's 'buy' method
        # Assuming amount is a Decimal like Decimal("10.5")
        invocation = await contract.functions["transfer"].invoke_v3(
            reciepient=buyer_int,   
            amount=int(amount),
            auto_estimate=True,
        )
        # Wait for transaction to be accepted
        await invocation.wait_for_acceptance()
        
        return hex(invocation.hash)

    except Exception as e:
        raise RuntimeError(f"{str(e)}")

