# src/utils/starknet/stark.py

from starknet_py.net.account.account import Account, KeyPair
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models.chains import StarknetChainId
from starknet_py.contract import Contract

from src.config import settings
from .abi import strk_abi


# Utility: Convert Felt to String
# def felt_to_str(felt: int) -> str:
#     result = ""
#     while felt:
#         result = chr(felt & 0xFF) + result
#         felt >>= 8
#     return result


# Configure StarkNet client and account
client = FullNodeClient(node_url=settings.STARKNET_RPC_URL)

account = Account(
    client=client,
    address=settings.STARKNET_ACCOUNT_ADDRESS,
    key_pair=KeyPair.from_private_key(
        key=settings.STARKNET_PRIVATE_KEY
    ),
    chain=StarknetChainId.SEPOLIA,
)

contract_address = settings.STRK_CONTRACT_ADDRESS
contract = Contract(address=contract_address, abi=strk_abi, provider=account, cairo_version=1)


async def balanceOf(account_address: str) -> float:
    """
    Returns the balance of STRK tokens for the given StarkNet address.
    Converts the raw integer balance to human-readable float format (18 decimals).
    """
    try:
        (saved,) = await contract.functions["balanceOf"].call(int(account_address, 16))
        balance = round(float(saved / 1e18), 4)
        return balance
    except Exception as e:
        raise RuntimeError(f"Failed to fetch STRK balance: {e}")

