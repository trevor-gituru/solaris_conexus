// lib/stcContract
import { RpcProvider, Contract } from 'starknet';

// Load environment variables
const nodeUrl = process.env.NEXT_PUBLIC_PROVIDER_URL!;
const SCT_Address = process.env.NEXT_PUBLIC_STC_ADDRESS!;

// Create provider
const provider = new RpcProvider({ nodeUrl });

export const getContract = async () => {
  const { abi } = await provider.getClassAt(SCT_Address);
  if (!abi) throw new Error('No ABI found for the contract.');

  return new Contract(abi, SCT_Address, provider);
};

