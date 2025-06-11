use starknet::{
    ContractAddress, ClassHash
};
use solaris_conexus_token::SolarisConexusToken::ArrayData;

#[starknet::interface]
pub trait ISolarisConexusTokenState<TContractState> {
    fn addHub(ref self: TContractState, hub: ContractAddress);
    fn buy(ref self: TContractState, buyer: ContractAddress, amount: u256);
    fn consume(ref self: TContractState, account: ContractAddress, amount: u256);
    fn createTrade(ref self: TContractState, amount: u256);
    fn deleteTrade(ref self: TContractState, trade_id: u64);
    fn deleteHub(ref self: TContractState, hub_id: u64);
    fn mint(ref self: TContractState, account: ContractAddress, amount: u256);
    fn reclaimTrade(ref self: TContractState, trade_id: u64);
    fn payTrade(ref self: TContractState, trade_id: u64, amount: u256);
    fn signTrade(ref self: TContractState, buyer: ContractAddress, trade_id: u64);
    fn transfer(ref self: TContractState, reciepient: ContractAddress, amount: u256);
    fn upgrade(ref self: TContractState, new_class_hash: ClassHash);
}

// Viewer public functions
#[starknet::interface]
pub trait ISolarisConexusTokenView<TContractState> {
    fn balanceOf(self: @TContractState, account: ContractAddress) -> u256;
    fn collaterals(self: @TContractState) -> u256;
    fn decimals(self: @TContractState) -> u8;
    fn fetchTrade(self: @TContractState, trade_id: u64) -> Array<ArrayData>;
    fn fetchHub(self: @TContractState, hub_id: u64) -> ContractAddress;
    fn filterTrade(self: @TContractState, amount: u256) -> Array<u64>;
    fn get_owner(self: @TContractState) -> ContractAddress;
    fn name(self: @TContractState) -> felt252;
    fn symbol(self: @TContractState) -> felt252;
    fn totalSupply(self: @TContractState) -> u256;
}
