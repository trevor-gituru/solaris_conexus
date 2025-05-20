'use client';

import React, { useState } from 'react';
import { connect } from '@starknet-io/get-starknet';
import { WalletAccount, uint256 } from 'starknet';
import { getContract } from '@/lib/stcContract'; // adjust path if needed
import { cairo, type Uint256 } from 'starknet';


export default function ConnectAndTransfer() {
  const [walletAccount, setWalletAccount] = useState<WalletAccount | null>(null);
  const [txHash, setTxHash] = useState<string>('');
  const [error, setError] = useState<string>('');

  const handleConnectAndTransfer = async () => {
    setError('');
    setTxHash('');

    try {
      // 1. Connect to Braavos wallet
      const selectedSWO = await connect({
        modalMode: 'alwaysAsk',
        modalTheme: 'light',
        include: ['braavos'],
      });

      if (!selectedSWO || selectedSWO.id !== 'braavos') {
        throw new Error('Braavos wallet is required');
      }

      const account = await WalletAccount.connect(
        { nodeUrl: process.env.NEXT_PUBLIC_PROVIDER_URL! },
        selectedSWO
      );

      setWalletAccount(account);

      // 2. Get the contract and connect it to wallet account
      const contract = await getContract();
      contract.connect(account); // updates provider to wallet for execution

      // 3. Prepare transfer call
      const amount: Uint256  = cairo.uint256(1);

      const TO_ADDRESS = '0x74de4a707539c4d01dd3d0e92c7a56c6974d2b8d5626f17deca161a32def42e';
      const call = contract.populate('transfer', {
        reciepient: TO_ADDRESS,
        amount: amount,
      });

      // 4. Execute and show transaction hash
      const { transaction_hash } = await account.execute(call);
      setTxHash(transaction_hash);
    } catch (err: any) {
      console.error('Error:', err);
      setError(err.message || 'Unknown error occurred');
    }
  };

  return (
    <div className="p-4 space-y-4">
      <button
        onClick={handleConnectAndTransfer}
        className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded"
      >
        Connect & Transfer 1 STC
      </button>

      {txHash && (
        <p className="text-green-600 break-all">
          ✅ Transfer sent! Tx Hash: <span className="font-mono">{txHash}</span>
        </p>
      )}

      {error && <p className="text-red-500">❌ {error}</p>}
    </div>
  );
}

