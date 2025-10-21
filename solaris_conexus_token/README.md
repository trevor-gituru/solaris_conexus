# Solaris Conexus Token (SCT) - Starknet Smart Contract

This directory contains the Cairo smart contract for the Solaris Conexus Token (SCT), which is deployed on the Starknet network.

## Overview

The SCT is an ERC20-compliant token that forms the backbone of the Solaris Conexus ecosystem. It is used to:
-   Reward producers for surplus energy generation.
-   Enable peer-to-peer energy trading between consumers and producers.
-   Provide a transparent and immutable ledger for all energy transactions on the blockchain.

## Tech Stack

-   **Language:** Cairo
-   **Framework:** Starknet
-   **Build Tool:** Scarb

## Getting Started

### Prerequisites

-   [Scarb](https://docs.swmansion.com/scarb/download.html) toolchain installed.
-   [Starknet Foundry](https://foundry-rs.github.io/starknet-foundry/) for testing.
-   [Starkli](https://book.starkli.rs/) for deployment and interaction.

### Build

To compile the contract, run the following command from within this directory:

```bash
scarb build
```

### Test

To run the tests for the contract, use Starknet Foundry:

```bash
snforge test
```

## Contract Features

-   **Token Minting:** Allows the contract owner (the central backend) to mint new SCT tokens for energy producers.
-   **Token Transfer:** Standard ERC20 `transfer` and `transferFrom` functions for moving tokens between wallets.
-   **Trade Lifecycle:** Functions to create, accept, and manage energy trade requests.
-   **On-chain Accounting:** Provides a transparent and auditable record of all energy production and consumption.

---

## Deployment & Interaction Logs

*The following are logs from a previous deployment and interaction session for reference.*

- Setup starkli account
```bash
razaoul@trevor-HP-650-Notebook-PC:~/Documents/software_dev/solaris_conexus/solaris_conexus_token$ starkli account fetch 0x040dc3bb58168d641811d5a516760c9ba57ee7bf98c547fa3fb5fce71774d90b --output owner
WARNING: you're using neither --rpc (STARKNET_RPC) nor --network (STARKNET_NETWORK). The `sepolia` network is used by default. See https://book.starkli.rs/providers for more details.
Account contract type identified as: Braavos
Description: Braavos official account (as of v4.0.7)
Downloaded new account config file: /home/razaoul/Documents/software_dev/solaris_conexus/solaris_conexus_token/owner
razaoul@trevor-HP-650-Notebook-PC:~/Documents/software_dev/solaris_conexus/solaris_conexus_token$ cat owner 
{
  "version": 1,
  "variant": {
    "type": "braavos",
    "version": 1,
    "multisig": {
      "status": "off"
    },
    "signers": [
      {
        "type": "stark",
        "public_key": "0x320514f4b87a44e3725b2e32d57cf2d560691f29fb273a4b42775a3610bf1fc"
      }
    ]
  },
  "deployment": {
    "status": "deployed",
    "class_hash": "0x3957f9f5a1cbfe918cedc2015c85200ca51a5f7506ecb6de98a5207b759bf8a",
    "address": "0x40dc3bb58168d641811d5a516760c9ba57ee7bf98c547fa3fb5fce71774d90b"
  }
}
razaoul@trevor-HP-650-Notebook-PC:~/Documents/software_dev/solaris_conexus/solaris_conexus_token$ starkli signer keystore from-key owner_signer
Enter private key: 
Enter password: 
Created new encrypted keystore file: /home/razaoul/Documents/software_dev/solaris_conexus/solaris_conexus_token/owner_signer
Public key: 0x0320514f4b87a44e3725b2e32d57cf2d560691f29fb273a4b42775a3610bf1fc
```
- Declare contract
```bash
razaoul@trevor-HP-650-Notebook-PC:~/Documents/software_dev/solaris_conexus/solaris_conexus_token$ starkli declare --account owner --keystore owner_signer --keystore-password '' --network sepolia ./target/dev/solaris_conexus_token_SolarisConexusToken.contract_class.json
WARNING: setting keystore passwords via --password or env var is generally considered insecure, as they might be stored in your shell history or other log files.
Declaring Cairo 1 class: 0x013491a662b3d34c29ac324735aa7ffebfc6f70bb5d54e71cb89d563a87259c7
Compiling Sierra class to CASM with compiler version 2.11.4...
CASM class hash: 0x07cbfb2b51ccef0ebdc7cbac4f861b6b2c4d98946caac457bb8a2120d91d18f2
Contract declaration transaction: 0x01a31e95d837aa13164c40b302ebed3c4054b39f847bddb4c960ae591784873d
Class hash declared:
0x013491a662b3d34c29ac324735aa7ffebfc6f70bb5d54e71cb89d563a87259c7
razaoul@trevor-HP-650-Notebook-PC:~/Documents/software_dev/solaris_conexus/solaris_conexus_token$ starkli deploy --account owner --keystore owner_signer --keystore-password '' --network sepolia 0x013491a662b3d34c29ac324735aa7ffebfc6f70bb5d54e71cb89d563a87259c7 0x040dc3bb58168d641811d5a516760c9ba57ee7bf98c547fa3fb5fce71774d90b
WARNING: setting keystore passwords via --password or env var is generally considered insecure, as they might be stored in your shell history or other log files.
Deploying class 0x013491a662b3d34c29ac324735aa7ffebfc6f70bb5d54e71cb89d563a87259c7 with salt 0x01542db70e46e1502ee5e5aef05c61aec8aec982908eeae0da1537935056923e...
The contract will be deployed at address 0x0696e1ba36b1b46ccfda4a6ae963b12c932e36d1a1008d5d0a03033b12d86827
Contract deployment transaction: 0x00b51886f90bdb09cf730baad7301044035f91346d213a3f9b60eb042e86933b
Contract deployed:
0x0696e1ba36b1b46ccfda4a6ae963b12c932e36d1a1008d5d0a03033b12d86827
```


- Call viewer fn
```bash
razaoul@trevor-HP-650-Notebook-PC:~/Documents/software_dev/solaris_conexus/solaris_conexus_token$ starkli call --network sepolia 0x0696e1ba36b1b46ccfda4a6ae963b12c932e36d1a1008d5d0a03033b12d86827 get_owner
[
    "0x040dc3bb58168d641811d5a516760c9ba57ee7bf98c547fa3fb5fce71774d90b"
]
razaoul@trevor-HP-650-Notebook-PC:~/Documents/software_dev/solaris_conexus/solaris_conexus_token$ starkli call --network sepolia 0x0696e1ba36b1b46ccfda4a6ae963b12c932e36d1a1008d5d0a03033b12d86827 totalSupply
[
    "0x0000000000000000000000000000000000000000000000000000000000000000",
    "0x0000000000000000000000000000000000000000000000000000000000000000"
]
```

- Call invoker fn
```bash
razaoul@trevor-HP-650-Notebook-PC:~/Documents/software_dev/solaris_conexus/solaris_conexus_token$ starkli invoke --account owner --keystore owner_signer --keystore-password '' --network sepolia 0x0696e1ba36b1b46ccfda4a6ae963b12c932e36d1a1008d5d0a03033b12d86827 mint 0x0696e1ba36b1b46ccfda4a6ae963b12c932e36d1a1008d5d0a03033b12d86827 10000 0
WARNING: setting keystore passwords via --password or env var is generally considered insecure, as they might be stored in your shell history or other log files.
Invoke transaction: 0x0224e18d8d781b52cbe9de5e22d6ded87879230e6396b8d10bd62b4826c7ae0d
razaoul@trevor-HP-650-Notebook-PC:~/Documents/software_dev/solaris_conexus/solaris_conexus_token$ starkli call --network sepolia 0x0696e1ba36b1b46ccfda4a6ae963b12c932e36d1a1008d5d0a03033b12d86827 totalSupply
[
    "0x0000000000000000000000000000000000000000000000000000000000002710",
    "0x0000000000000000000000000000000000000000000000000000000000000000"
]
razaoul@trevor-HP-650-Notebook-PC:~/Documents/software_dev/solaris_conexus/solaris_conexus_token$ starkli call --network sepolia 0x0696e1ba36b1b46ccfda4a6ae963b12c932e36d1a1008d5d0a03033b12d86827 balanceOf 0x0696e1ba36b1b46ccfda4a6ae963b12c932e36d1a1008d5d0a03033b12d86827
[
    "0x0000000000000000000000000000000000000000000000000000000000002710",
    "0x0000000000000000000000000000000000000000000000000000000000000000"
]
```