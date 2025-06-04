from starknet_py.net.account.account import Account, KeyPair
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models.chains import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner

from starknet_py.contract import Contract
from starknet_py.net.client_models import ResourceBounds, ResourceBoundsMapping
import asyncio

# Creates an instance of account which is already deployed
# Account using transaction version=1 (has __validate__ function)
client = FullNodeClient(node_url="https://starknet-sepolia.g.alchemy.com/starknet/version/rpc/v0_8/TZnwD5R59wzUZLADsAcjTBotxfzYN8dO")
account = Account(
    client=client,
    address="0x040dc3bb58168d641811d5a516760c9ba57ee7bf98c547fa3fb5fce71774d90b",
    key_pair=KeyPair.from_private_key(key="0x044a3fe666102135fd9ef67426d2ba01d8b8f252048b391b68042e93b14246bc"),
    chain=StarknetChainId.SEPOLIA,
)


contract_address = (
    "0x0696e1ba36b1b46ccfda4a6ae963b12c932e36d1a1008d5d0a03033b12d86827"
)
key = 1234
def felt_to_str(felt):
    result = ""
    while felt:
        result = chr(felt & 0xFF) + result
        felt >>= 8
    return result

 

async def main():
    # Create contract from contract's address - Contract will download contract's ABI to know its interface.
    contract = await Contract.from_address(address=contract_address, provider=account)
    
    # Calling contract's function doesn't create a new transaction, you get the function's result.
    (saved,) = await contract.functions["balanceOf"].call(int("0x40dc3bb58168d641811d5a516760c9ba57ee7bf98c547fa3fb5fce71774d90b", 16))
    # saved = 7 now
    print(saved)

 
    # Calling contract's function doesn't create a new transaction, you get the function's result.
    (saved,) = await contract.functions["totalSupply"].call()
    # saved = 7 now
    print(saved)

    # Calling contract's function doesn't create a new transaction, you get the function's result.
    (saved,) = await contract.functions["get_owner"].call()
    # saved = 7 now
    print(hex(saved))

    # Calling contract's function doesn't create a new transaction, you get the function's result.
    (saved,) = await contract.functions["decimals"].call()
    # saved = 7 now
    print(saved)

    # Calling contract's function doesn't create a new transaction, you get the function's result.
    (saved,) = await contract.functions["symbol"].call()
    # saved = 7 now
    print(felt_to_str(saved))
    


    # Calling contract's function doesn't create a new transaction, you get the function's result.
    (saved,) = await contract.functions["name"].call()
    # saved = 7 now
    print(felt_to_str(saved))


   
if __name__ == "__main__":
    asyncio.run(main())


