'use client';

import React, { useState } from 'react';
import { connect } from '@starknet-io/get-starknet';
import { WalletAccount, cairo, type Uint256 } from 'starknet';
import { getContract } from '@/lib/strkContract'; // adjust path if needed

export default function ConnectAndTransfer() {
  const [walletAccount, setWalletAccount] = useState<WalletAccount | null>(null);
  const [txHash, setTxHash] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [amountInput, setAmountInput] = useState<string>(''); // For user input

  const handleConnectAndTransfer = async () => {
    setError('');
    setTxHash('');

    try {
      if (!amountInput || isNaN(Number(amountInput))) {
        throw new Error('Please enter a valid amount.');
      }

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
      contract.connect(account);

      // 3. Prepare transfer call
      const parsedAmount = parseFloat(amountInput);
      const tokenAmount = BigInt(parsedAmount * 10 ** 18); // Assuming 18 decimals
      const uintAmount: Uint256 = cairo.uint256(tokenAmount);

      const TO_ADDRESS = process.env.NEXT_PUBLIC_STC_ADDRESS!;
      const call = contract.populate('transfer', {
        recipient: TO_ADDRESS,
        amount: uintAmount,
      });

      // 4. Execute transfer
      const { transaction_hash } = await account.execute(call);
      setTxHash(transaction_hash);
    } catch (err: any) {
      console.error('Error:', err);
      setError(err.message || 'Unknown error occurred');
    }
  };

  return (
    <div className="p-4 space-y-4 max-w-md mx-auto">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Amount (STC)
        </label>
        <input
          type="number"
          min="0"
          step="any"
          placeholder="Enter amount e.g. 1.5"
          value={amountInput}
          onChange={(e) => setAmountInput(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded"
        />
      </div>

      <button
        onClick={handleConnectAndTransfer}
        className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded"
      >
        Connect & Transfer
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

