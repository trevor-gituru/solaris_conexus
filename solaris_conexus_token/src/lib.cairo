mod interfaces;


/// Simple contract for managing balance.
#[starknet::contract]
mod SolarisConexusToken {
    use starknet::{
        ClassHash, ContractAddress,
        get_contract_address, get_caller_address, syscalls
    };
    use starknet::storage::{
        StoragePointerReadAccess, StoragePointerWriteAccess,
        StoragePathEntry, Map, Vec, VecTrait, MutableVecTrait
    };
    // use starknet::class_hash::class_hash_const;
    use core::num::traits::Zero;
    use core::starknet::{
        
    };
    use super::interfaces::{ISolarisConexusTokenState, ISolarisConexusTokenView};

// -------------------------
//       Constants Section
// -------------------------
// Define constant variables that are used throughout the contract.
    const DECIMALS: u8 = 0;
    const NAME: felt252 = 'SolarisConexusToken';
    const SYMBOL: felt252 = 'SCT';
// -------------------------
//       Data Types Section
// -------------------------
// Define custom data types used by the contract.
    #[allow(starknet::store_no_default_variant)]
    #[derive(Copy, Drop, Serde, starknet::Store)]
    pub enum ArrayData {
        U8: u8,
        U64: u64,
        U256: u256,
        Felt: felt252,
        Address: ContractAddress,
    }

    #[derive(Copy, Drop, Serde, starknet::Store)]
    pub struct Trade {
        id: u64,
        lender: ContractAddress,
        borrower: Option<ContractAddress>,
        amount: u256,
        balance: u256,
        status: TradeStatus
    }

    #[generate_trait]
    impl TradeImpl of TradeTrait {
        fn sign(ref self: Trade, borrower: ContractAddress){
            self.borrower = Option::Some(borrower);
            self.status = TradeStatus::Active;

        }

        fn toArray(trade: Trade) -> Array<ArrayData>{
            let mut trade_arr:Array<ArrayData> = ArrayTrait::new();
            let borrower: ContractAddress = trade.borrower
                                .unwrap_or(TryInto::try_into(0).unwrap());
            trade_arr.append(ArrayData::U64(trade.id));
            trade_arr.append(ArrayData::Address(trade.lender));
            trade_arr.append(ArrayData::Address(borrower));
            trade_arr.append(ArrayData::U256(trade.amount));
            trade_arr.append(ArrayData::U256(trade.balance));
            trade_arr.append(ArrayData::U8(trade.status.to_u8()));
            return trade_arr;
        }
    }
    #[allow(starknet::store_no_default_variant)]
    #[derive(Copy, Drop, Serde, starknet::Store)]
    pub enum HubStatus {
        Active,        // Hub is active and has been created by owner
        Closed,        // Hub has been closed or terminated by owner
    }

    #[generate_trait]
    impl HubStatusImpl of HubStatusTrait{
        fn to_u8(self: @HubStatus) -> u8{
            match self {
                HubStatus::Active => { 0_u8 },
                HubStatus::Closed => { 1_u8 },
            }
        }
    }

    #[allow(starknet::store_no_default_variant)]
    #[derive(Copy, Drop, Serde, starknet::Store)]
    pub enum TradeStatus {
        Pending,       // Trade has been offered but not yet accepted
        Active,        // Trade is active and has been accepted by the borrower
        Repaid,        // Trade has been fully repaid
        Defaulted,     // Trade has defaulted and collateral has been claimed
        Closed,        // Trade has been closed or terminated by lender
    }

    #[generate_trait]
    impl TradeStatusImpl of TradeStatusTrait{
        fn to_u8(self: @TradeStatus) -> u8{
            match self {
                TradeStatus::Pending => { 0_u8 },
                TradeStatus::Active => { 1_u8 },
                TradeStatus::Repaid => { 2_u8},
                TradeStatus::Defaulted => { 3_u8 },
                TradeStatus::Closed => { 4_u8 },
            }
        }
    }

// -------------------------
//       Events Section
// -------------------------
// Define events that will be emitted during contract execution.
    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        Consume: Consume,
        Mint: Mint,
        Transfer: Transfer,
        Trade: TradeEvent,
        Upgrade: Upgrade,
	Hub: Hub

    }
    /// @dev Represents a Consume action successfuly performed
    #[derive(Drop, starknet::Event)]
    struct Consume {
        #[key]
        account: ContractAddress,
        amount: u256
    }

    /// @dev Represents a Hub action successfuly performed
    #[derive(Drop, starknet::Event)]
    struct Hub {
        #[key]
        account_address: ContractAddress,
	id: u64,
        status: u8
    }


    /// @dev Represents a mint action successfuly performed
    #[derive(Drop, starknet::Event)]
    struct Mint {
        #[key]
        account: ContractAddress,
        amount: u256
    }

    #[derive(Drop, starknet::Event)]
    struct TradeEvent {
        global_id: u64,
        local_id: u64,
        lender: ContractAddress,
        borrower: ContractAddress,
        amount: u256,
        balance: u256,
        status: u8
    }

    #[generate_trait]
    impl TradeEventImpl of TradeEventTrait {
        fn new(trade: Trade, local_id: u64) -> TradeEvent{
            let borrower: ContractAddress = trade.borrower
                        .unwrap_or(TryInto::try_into(0).unwrap());
            TradeEvent {
                global_id: trade.id,
                local_id: local_id,
                lender: trade.lender,
                borrower: borrower,
                amount: trade.amount,
                balance: trade.balance,
                status: trade.status.to_u8()
            }
        }
    }

    /// @dev Represents a transfer action successfuly performed
    #[derive(Drop, starknet::Event)]
    struct Transfer {
        #[key]
        from: ContractAddress,
        #[key]
        to: ContractAddress,
        amount: u256
    }

    /// @dev Represents an Upgrade action successfuly performed
    #[derive(Drop, starknet::Event)]
    struct Upgrade {
        by: ContractAddress,
    }

// -------------------------
//       Storage Section
// -------------------------
// Define the storage variables here, which will be persistent across contract calls.
    #[storage]
    struct Storage {
        account_balances: Map<ContractAddress, u256>,
	hubs: Vec<Option<ContractAddress>>,
        trade: Vec<Option<Trade>>,
        trade_counter: u64,
        total_supply: u256,
        owner: ContractAddress,
    }

// -------------------------
//       Constructor Section
// -------------------------
// Constructor to initialize contract state (owner and initial balance).
    #[constructor]
    fn constructor(ref self: ContractState, owner_account: ContractAddress) {
        self.owner.write(owner_account);
        self.trade_counter.write(0_u64);
        self.emit(Upgrade{by: owner_account});

    }
// -------------------------
//       Implementation Section
// -------------------------
// Implement the contract functions and logic.
    #[generate_trait]
    impl InternalStateFunctions of InternalStateFunctionsTraits{
        fn _insertTrade(ref self: ContractState, new_trade: Trade) -> u64{
            // Check for an empty vec
            let next_global_id: u64 = self.trade_counter.read() + 1_u64;
            if self.trade.len() == 0{
                self.trade.push(Option::Some(new_trade));
                self.trade_counter.write(next_global_id);
                return 0_u64;
            }
            // Check for vec with empty slot
            let mut i: u64 = 0;
            let mut found_slot: bool = false;
            while i < self.trade.len(){
                let current_trade: Option<Trade> = self.trade.at(i).read();
                if current_trade.is_none(){
                    self.trade.at(i).write(Option::Some(new_trade));
                    found_slot = true;
                    break;
                }
                i = i + 1;
            };
            self.trade_counter.write(next_global_id);
            if found_slot{
                return i;
            }
            self.trade.push(Option::Some(new_trade));
            return (self.trade.len() - 1_u64);
        }


	fn _insertHub(ref self: ContractState, hub: ContractAddress) -> u64{
            // Check for an empty vec
            if self.hubs.len() == 0{
                self.hubs.push(Option::Some(hub));
                return 0_u64;
            }
            // Check for vec with empty slot
            let mut i: u64 = 0;
            let mut found_slot: bool = false;
            while i < self.hubs.len(){
                let current_hub: Option<ContractAddress> = self.hubs.at(i).read();
                if current_hub.is_none(){
                    self.hubs.at(i).write(Option::Some(hub));
                    found_slot = true;
                    break;
                }
                i = i + 1;
            };
            if found_slot{
                return i;
            }
            self.hubs.push(Option::Some(hub));
            return (self.hubs.len() - 1_u64);
        }

        fn _transferFromOwner(ref self: ContractState, borrower: ContractAddress, amount: u256){
            let owner_account: ContractAddress = self.owner.read();
            assert!(self._sufficientBalance(owner_account, amount), "INSUFFICIENT BALANCE");        
            let new_owner_token: u256 = self.account_balances.entry(owner_account).read() - amount;
            self.account_balances.entry(owner_account).write(new_owner_token);
            let new_borrower_token: u256 = self.account_balances.entry(borrower).read() + amount;
            self.account_balances.entry(borrower).write(new_borrower_token);
            self.emit(
                Transfer{
                from: owner_account, 
                to: borrower, 
                amount
                }
            );
            
        }
    }

    #[generate_trait]
    impl InternalViewFunctions of InternalViewFunctionsTraits{

    	fn _getHub(self: @ContractState, hub_id: u64) -> ContractAddress{
            assert!(hub_id < self.hubs.len(), "INVALID HUB ID");
            let hub: Option<ContractAddress> = self.hubs.at(hub_id).read();
            assert!(hub.is_some(), "HUB DOES NOT EXIST");
            let hub: ContractAddress = hub.unwrap();
            return hub;

        }

        fn _getTrade(self: @ContractState, trade_id: u64) -> Trade{
            assert!(trade_id < self.trade.len(), "INVALID trade ID");
            let trade: Option<Trade> = self.trade.at(trade_id).read();
            assert!(trade.is_some(), "TRADE DOES NOT EXIST");
            let trade: Trade = trade.unwrap();
            return trade;

        }

	fn _isAuth(self: @ContractState, account: ContractAddress) -> bool{
            let mut auth: bool = false;
            let owner: ContractAddress = self.owner.read();
	    // Check for an empty vec
            if owner == account{
                auth = true;
		return auth;
            }
            // Check for vec with empty slot
            let mut i: u64 = 0;
            while i < self.hubs.len(){
                let current_hub: Option<ContractAddress> = self.hubs.at(i).read();
                if current_hub.is_some(){
		    if current_hub.unwrap() == account{
		    	auth = true;
			return auth;
		    }
                }
                i = i + 1;
            };
	    return auth;
            
        }

        fn _isOwner(self: @ContractState, account: ContractAddress) -> bool{
            let owner: ContractAddress = self.owner.read();
            (owner == account)
        }

        fn _sufficientBalance(self: @ContractState, account: ContractAddress,
            transfer_amount: u256
        ) -> bool{
            let balance: u256 = self.balanceOf(account);
            (transfer_amount <= balance)
        }
    }
    
    #[abi(embed_v0)]
    impl SolarisConexusTokenStateImpl of ISolarisConexusTokenState<ContractState> {

       fn addHub(ref self: ContractState, hub: ContractAddress){
            let caller: ContractAddress = (get_caller_address());
            let owner: ContractAddress = self.owner.read();
            assert!(caller == owner, "INSUFFICIENT AUTHORITY");            
            let hub_id: u64 = self._insertHub(hub);
	    let hub_event: Hub = Hub {
                id: hub_id,
                account_address: hub,
                status: HubStatus::Active.to_u8()
            };
            self.emit(hub_event);
        }

        fn buy(ref self: ContractState, buyer: ContractAddress, amount: u256){
            let contract_account: ContractAddress = (get_contract_address());
            let owner: ContractAddress = (get_caller_address());
            assert!(self._isOwner(owner), "UNAUTHORIZED ACCOUNT");
            assert!(self._sufficientBalance(contract_account, amount), "INSUFFICIENT BALANCE");        
            let new_free_token: u256 = self.account_balances.entry(contract_account).read() - amount;
            self.account_balances.entry(contract_account).write(new_free_token);
            let new_buyer_token: u256 = self.account_balances.entry(buyer).read() + amount;
            self.account_balances.entry(buyer).write(new_buyer_token);
            self.emit(
                Transfer{
                from: contract_account, 
                to: buyer, 
                amount
                }
            );
        }

        fn createTrade(ref self: ContractState, amount: u256){
            let lender: ContractAddress = (get_caller_address());
            let owner: ContractAddress = self.owner.read();
            assert!(lender != owner, "INSUFFICIENT AUTHORITY");
            self.transfer(owner, amount);
            let trade_id: u64 = self.trade_counter.read();
            let trade: Trade = Trade {
                id: trade_id,
                lender,
                borrower: Option::None,
                amount,
                balance: amount,
                status: TradeStatus::Pending
            };
            let local_id: u64 = self._insertTrade(trade);
            let trade_event: TradeEvent = TradeEventImpl::new(trade, local_id);
            self.emit(trade_event);
        }

        fn consume(ref self: ContractState, account: ContractAddress, amount: u256){
            let call_account: ContractAddress = (get_caller_address());
            assert!(self._isAuth(call_account), "UNAUTHORIZED ACCOUNT");
            assert!(self._sufficientBalance(account, amount), "INSUFFICIENT BALANCE");        
            let new_free_token: u256 = self.account_balances.entry(account).read() - amount;
            let new_supply: u256 = self.total_supply.read() - amount; 
            self.total_supply.write(new_supply);
            self.account_balances.entry(account).write(new_free_token);
            self.emit(Consume{account, amount});
        }

	fn deleteHub(ref self: ContractState, hub_id: u64){
            let mut hub: ContractAddress = self._getHub(hub_id);
            let caller: ContractAddress = get_caller_address();
            assert!(self._isOwner(caller), "UNAUTHORIZED ACCOUNT");
            self.hubs.at(hub_id).write(Option::None);
            let hub_event: Hub = Hub {
                id: hub_id,
                account_address: hub,
                status: HubStatus::Closed.to_u8()
            };
            self.emit(hub_event);

        }

        fn deleteTrade(ref self: ContractState, trade_id: u64){
            let mut trade: Trade = self._getTrade(trade_id);
            let account: ContractAddress = get_caller_address();
            assert!(account == trade.lender, "NOT OWNER OF TRADE");
            assert!(trade.status.to_u8() == 0, "TRADE IS NOT PENDING");
            self._transferFromOwner(account, trade.amount);
            trade.status = TradeStatus::Closed;
            let trade_event: TradeEvent = TradeEventImpl::new(trade, trade_id);
            self.trade.at(trade_id).write(Option::None);
            self.emit(trade_event);
        }
        fn mint(ref self: ContractState, account: ContractAddress, amount: u256){
            let owner: ContractAddress = (get_caller_address());
            assert!(self._isOwner(owner), "UNAUTHORIZED ACCOUNT");
            
            let new_free_token: u256 = self.account_balances.entry(account).read() + amount;
            let new_supply: u256 = self.total_supply.read() + amount; 
            self.total_supply.write(new_supply);
            self.account_balances.entry(account).write(new_free_token);
            self.emit(Mint{account, amount});
        }

        fn reclaimTrade(ref self: ContractState, trade_id: u64){
            let mut trade: Trade = self._getTrade(trade_id);
            let owner: ContractAddress = get_caller_address();
            assert!(self._isOwner(owner), "UNAUTHORIZED ACCOUNT");
            assert!(trade.status.to_u8() == 1, "INACTIVE Trade");
            // Transfer balance to borrower, while rest to contract
            let buyer: ContractAddress = trade.borrower.unwrap();
            self._transferFromOwner(buyer, trade.balance);

            trade.status = TradeStatus::Defaulted;
            let trade_event: TradeEvent = TradeEventImpl::new(trade, trade_id);
            self.trade.at(trade_id).write(Option::None);
            self.emit(trade_event);
        }

        fn payTrade(ref self: ContractState, trade_id: u64, amount: u256){
            let owner: ContractAddress = get_caller_address();
            let mut trade: Trade = self._getTrade(trade_id);
            assert!(trade.status.to_u8() == 1, "INACTIVE TRADE");
            assert!(self._isAuth(owner), "UNAUTHORIZED ACCOUNT");
            let balance: u256 = trade.balance;
            assert!(amount <= balance, "INVALID REPAYMENT AMOUNT");
            let seller: ContractAddress = trade.lender;
            trade.balance = trade.balance - amount;
            if trade.balance == 0_u256{
                trade.status = TradeStatus::Repaid;
                self._transferFromOwner(seller, trade.amount);
                self.trade.at(trade_id).write(Option::None);
            } else {
                self.trade.at(trade_id).write(Option::Some(trade));
            }
            let Trade_event: TradeEvent = TradeEventImpl::new(trade, trade_id);
            self.emit(Trade_event);
            
        }

        fn signTrade(ref self: ContractState, buyer: ContractAddress,trade_id: u64) {
            let owner: ContractAddress = get_caller_address();
            let mut trade: Trade = self._getTrade(trade_id);
            assert!(self._isOwner(owner), "UNAUTHORIZED ACCOUNT");
            assert!(trade.status.to_u8() == 0, "TRADE IS ALREADY ACTIVE");
            trade.sign(buyer);
            self.trade.at(trade_id).write(Option::Some(trade));
            let Trade_event: TradeEvent = TradeEventImpl::new(trade, trade_id);
            self.emit(Trade_event);
            
        }

        fn transfer(ref self: ContractState, reciepient: ContractAddress, amount: u256){
            let sender: ContractAddress = (get_caller_address());

            assert!(self._sufficientBalance(sender, amount), "INSUFFICIENT BALANCE");
            let new_balance: u256 = self.account_balances.entry(sender).read() - amount;
            self.account_balances.entry(sender).write(new_balance);
            let new_balance: u256 = self.account_balances.entry(reciepient).read() + amount;
            self.account_balances.entry(reciepient).write(new_balance);
            self.emit(
                Transfer{
                from: sender, 
                to: reciepient, 
                amount
                }
            );
        }

        fn upgrade(ref self: ContractState, new_class_hash: ClassHash) {
            let caller: ContractAddress = get_caller_address();
            assert!(self._isOwner(caller), "INSUFFICIENT AUTHORITY");
            assert!(!(new_class_hash.is_zero()), "Class hash cannot be zero");
            syscalls::replace_class_syscall(new_class_hash).unwrap();
            self.emit(Upgrade{by: caller});
        }
    }

    #[abi(embed_v0)]
    impl SolarisConexusTokenViewImpl of ISolarisConexusTokenView<ContractState> {
        fn balanceOf(self: @ContractState, account: ContractAddress) -> u256 {
            self.account_balances.entry(account).read()
        }

        fn collaterals(self: @ContractState) -> u256 {
            let owner: ContractAddress = self.owner.read();
            self.account_balances.entry(owner).read()
        }

        fn decimals(self: @ContractState) -> u8 {
            (DECIMALS)
        }

        fn fetchTrade(self: @ContractState, trade_id: u64) -> Array<ArrayData> {
            assert!(trade_id < self.trade.len(), "INVALID TRADE ID");
            let trade: Option<Trade> = self.trade.at(trade_id).read();
            if trade.is_none(){
                return ArrayTrait::<ArrayData>::new();
            }
            let trade_arr = TradeImpl::toArray(trade.unwrap());
            trade_arr
        }

	fn fetchHub(self: @ContractState, hub_id: u64) -> ContractAddress {
            assert!(hub_id < self.hubs.len(), "INVALID HUB ID");
	    let hub: ContractAddress = self.hubs.at(hub_id).read()
                        .unwrap_or(TryInto::try_into(0).unwrap());
            hub
        }

        fn filterTrade(self: @ContractState, amount: u256) -> Array<u64> {
            let mut matching_trade: Array<u64> = array![];
            let mut i: u64 = 0;
            while i < self.trade.len(){
                let current_trade: Option<Trade> = self.trade.at(i).read();
                if current_trade.is_some(){
                    let current_trade: Trade = current_trade.unwrap();
                    if (amount <= current_trade.amount) && 
                            (current_trade.status.to_u8() == 0) {
                        matching_trade.append(i);
                    }
                }
                i = i + 1;
            };
            return matching_trade;
        }

        fn get_owner(self: @ContractState) -> ContractAddress {
            (self.owner.read())
        }

        fn name(self: @ContractState) -> felt252 {
            (NAME)
        }

        fn symbol(self: @ContractState) -> felt252 {
            (SYMBOL)
        }

        fn totalSupply(self: @ContractState) -> u256 {
            self.total_supply.read()
        }
    }
}
