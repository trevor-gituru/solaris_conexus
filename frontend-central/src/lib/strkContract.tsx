// lib/strkContract
import { RpcProvider, Contract } from 'starknet';

// Load environment variables
const nodeUrl = process.env.NEXT_PUBLIC_PROVIDER_URL!;
const testAddress = "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d" 

// Create provider
const provider = new RpcProvider({ nodeUrl });

export const getContract = async () => {
  const { abi } = await provider.getClassAt(testAddress);
  if (!abi) throw new Error('No ABI found for the contract.');

  return new Contract(abi, testAddress, provider);
};

