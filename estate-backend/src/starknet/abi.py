# /src/utils/starknet/abi.py

sct_abi = [
  {
    "type": "impl",
    "name": "SolarisConexusTokenStateImpl",
    "interface_name": "solaris_conexus_token::interfaces::ISolarisConexusTokenState"
  },
  {
    "type": "struct",
    "name": "core::integer::u256",
    "members": [
      {
        "name": "low",
        "type": "core::integer::u128"
      },
      {
        "name": "high",
        "type": "core::integer::u128"
      }
    ]
  },
  {
    "type": "interface",
    "name": "solaris_conexus_token::interfaces::ISolarisConexusTokenState",
    "items": [
      {
        "type": "function",
        "name": "addHub",
        "inputs": [
          {
            "name": "hub",
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "buy",
        "inputs": [
          {
            "name": "buyer",
            "type": "core::starknet::contract_address::ContractAddress"
          },
          {
            "name": "amount",
            "type": "core::integer::u256"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "consume",
        "inputs": [
          {
            "name": "account",
            "type": "core::starknet::contract_address::ContractAddress"
          },
          {
            "name": "amount",
            "type": "core::integer::u256"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "createTrade",
        "inputs": [
          {
            "name": "amount",
            "type": "core::integer::u256"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "deleteTrade",
        "inputs": [
          {
            "name": "trade_id",
            "type": "core::integer::u64"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "deleteHub",
        "inputs": [
          {
            "name": "hub_id",
            "type": "core::integer::u64"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "mint",
        "inputs": [
          {
            "name": "account",
            "type": "core::starknet::contract_address::ContractAddress"
          },
          {
            "name": "amount",
            "type": "core::integer::u256"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "reclaimTrade",
        "inputs": [
          {
            "name": "trade_id",
            "type": "core::integer::u64"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "payTrade",
        "inputs": [
          {
            "name": "trade_id",
            "type": "core::integer::u64"
          },
          {
            "name": "amount",
            "type": "core::integer::u256"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "signTrade",
        "inputs": [
          {
            "name": "buyer",
            "type": "core::starknet::contract_address::ContractAddress"
          },
          {
            "name": "trade_id",
            "type": "core::integer::u64"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "transfer",
        "inputs": [
          {
            "name": "reciepient",
            "type": "core::starknet::contract_address::ContractAddress"
          },
          {
            "name": "amount",
            "type": "core::integer::u256"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      },
      {
        "type": "function",
        "name": "upgrade",
        "inputs": [
          {
            "name": "new_class_hash",
            "type": "core::starknet::class_hash::ClassHash"
          }
        ],
        "outputs": [],
        "state_mutability": "external"
      }
    ]
  },
  {
    "type": "impl",
    "name": "SolarisConexusTokenViewImpl",
    "interface_name": "solaris_conexus_token::interfaces::ISolarisConexusTokenView"
  },
  {
    "type": "enum",
    "name": "solaris_conexus_token::SolarisConexusToken::ArrayData",
    "variants": [
      {
        "name": "U8",
        "type": "core::integer::u8"
      },
      {
        "name": "U64",
        "type": "core::integer::u64"
      },
      {
        "name": "U256",
        "type": "core::integer::u256"
      },
      {
        "name": "Felt",
        "type": "core::felt252"
      },
      {
        "name": "Address",
        "type": "core::starknet::contract_address::ContractAddress"
      }
    ]
  },
  {
    "type": "interface",
    "name": "solaris_conexus_token::interfaces::ISolarisConexusTokenView",
    "items": [
      {
        "type": "function",
        "name": "balanceOf",
        "inputs": [
          {
            "name": "account",
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "outputs": [
          {
            "type": "core::integer::u256"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "collaterals",
        "inputs": [],
        "outputs": [
          {
            "type": "core::integer::u256"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "decimals",
        "inputs": [],
        "outputs": [
          {
            "type": "core::integer::u8"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "fetchTrade",
        "inputs": [
          {
            "name": "trade_id",
            "type": "core::integer::u64"
          }
        ],
        "outputs": [
          {
            "type": "core::array::Array::<solaris_conexus_token::SolarisConexusToken::ArrayData>"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "fetchHub",
        "inputs": [
          {
            "name": "hub_id",
            "type": "core::integer::u64"
          }
        ],
        "outputs": [
          {
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "filterTrade",
        "inputs": [
          {
            "name": "amount",
            "type": "core::integer::u256"
          }
        ],
        "outputs": [
          {
            "type": "core::array::Array::<core::integer::u64>"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "get_owner",
        "inputs": [],
        "outputs": [
          {
            "type": "core::starknet::contract_address::ContractAddress"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "name",
        "inputs": [],
        "outputs": [
          {
            "type": "core::felt252"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "symbol",
        "inputs": [],
        "outputs": [
          {
            "type": "core::felt252"
          }
        ],
        "state_mutability": "view"
      },
      {
        "type": "function",
        "name": "totalSupply",
        "inputs": [],
        "outputs": [
          {
            "type": "core::integer::u256"
          }
        ],
        "state_mutability": "view"
      }
    ]
  },
  {
    "type": "constructor",
    "name": "constructor",
    "inputs": [
      {
        "name": "owner_account",
        "type": "core::starknet::contract_address::ContractAddress"
      }
    ]
  },
  {
    "type": "event",
    "name": "solaris_conexus_token::SolarisConexusToken::Consume",
    "kind": "struct",
    "members": [
      {
        "name": "account",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "key"
      },
      {
        "name": "amount",
        "type": "core::integer::u256",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "solaris_conexus_token::SolarisConexusToken::Mint",
    "kind": "struct",
    "members": [
      {
        "name": "account",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "key"
      },
      {
        "name": "amount",
        "type": "core::integer::u256",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "solaris_conexus_token::SolarisConexusToken::Transfer",
    "kind": "struct",
    "members": [
      {
        "name": "from",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "key"
      },
      {
        "name": "to",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "key"
      },
      {
        "name": "amount",
        "type": "core::integer::u256",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "solaris_conexus_token::SolarisConexusToken::TradeEvent",
    "kind": "struct",
    "members": [
      {
        "name": "global_id",
        "type": "core::integer::u64",
        "kind": "data"
      },
      {
        "name": "local_id",
        "type": "core::integer::u64",
        "kind": "data"
      },
      {
        "name": "lender",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "borrower",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      },
      {
        "name": "amount",
        "type": "core::integer::u256",
        "kind": "data"
      },
      {
        "name": "balance",
        "type": "core::integer::u256",
        "kind": "data"
      },
      {
        "name": "status",
        "type": "core::integer::u8",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "solaris_conexus_token::SolarisConexusToken::Upgrade",
    "kind": "struct",
    "members": [
      {
        "name": "by",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "solaris_conexus_token::SolarisConexusToken::Hub",
    "kind": "struct",
    "members": [
      {
        "name": "account_address",
        "type": "core::starknet::contract_address::ContractAddress",
        "kind": "key"
      },
      {
        "name": "id",
        "type": "core::integer::u64",
        "kind": "data"
      },
      {
        "name": "status",
        "type": "core::integer::u8",
        "kind": "data"
      }
    ]
  },
  {
    "type": "event",
    "name": "solaris_conexus_token::SolarisConexusToken::Event",
    "kind": "enum",
    "variants": [
      {
        "name": "Consume",
        "type": "solaris_conexus_token::SolarisConexusToken::Consume",
        "kind": "nested"
      },
      {
        "name": "Mint",
        "type": "solaris_conexus_token::SolarisConexusToken::Mint",
        "kind": "nested"
      },
      {
        "name": "Transfer",
        "type": "solaris_conexus_token::SolarisConexusToken::Transfer",
        "kind": "nested"
      },
      {
        "name": "Trade",
        "type": "solaris_conexus_token::SolarisConexusToken::TradeEvent",
        "kind": "nested"
      },
      {
        "name": "Upgrade",
        "type": "solaris_conexus_token::SolarisConexusToken::Upgrade",
        "kind": "nested"
      },
      {
        "name": "Hub",
        "type": "solaris_conexus_token::SolarisConexusToken::Hub",
        "kind": "nested"
      }
    ]
  }
]

