// components/ConnectWallet.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { connect } from '@starknet-io/get-starknet';     // v4+
import { WalletAccount } from 'starknet';               // v6+

const PROVIDER_URL = process.env.NEXT_PUBLIC_PROVIDER_URL; 
const ERC20_ADDRESS = process.env.NEXT_PUBLIC_STC_ADDRESS; 
export default function ConnectWallet() {
  const [walletAccount, setWalletAccount] = useState<WalletAccount | null>(null);
  const [address, setAddress] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [hasPromptedAdd, setHasPromptedAdd] = useState(false);

  const handleConnect = async () => {
   // setError(''); // Reset error before attempting to connect
    try {
      const selectedSWO = await connect({
        modalMode: 'alwaysAsk',
        modalTheme: 'light',
        include: ['braavos'],
      });

      if (!selectedSWO) {
        setError('No wallet selected');
        return;
      }
      if (selectedSWO.id !== 'braavos') {
        setError(`Please select Braavos; you chose "${selectedSWO.id}"`);
        return;
      }

      const wa = await WalletAccount.connect(
        { nodeUrl: PROVIDER_URL },
        selectedSWO
      );

      setWalletAccount(wa);
      setAddress(wa.address);
      setHasPromptedAdd(false);
    } catch (err: any) {
      console.error('connect error ➡️', err);
      setError(err.message || 'Unknown error');
    }
  };

  useEffect(() => {
    if (!walletAccount || hasPromptedAdd) return;

    (async () => {
      try {
        await walletAccount.watchAsset({
          type: 'ERC20',
          options: { address: ERC20_ADDRESS },
        });
      } catch (e) {
        console.error('watchAsset failed:', e);
      } finally {
        setHasPromptedAdd(true);
      }
    })();
  }, [walletAccount, hasPromptedAdd]);

  const handleDisconnect = () => {
    setWalletAccount(null);
    setAddress('');
    setHasPromptedAdd(false);
  };

  return (
    <div className="p-4">
      {walletAccount ? (
        <div className="space-y-4">
          <p className="text-green-600 flex items-center space-x-2">
            <span>Connected: {address.slice(0, 6)}...{address.slice(-4)}</span>
            <button
              onClick={() => {
                navigator.clipboard.writeText(address);
                alert('Wallet address copied!');
              }}
              className="text-sm text-blue-500 hover:underline"
            >
              Copy
            </button>
          </p>

          <button
            onClick={handleDisconnect}
            className="bg-red-500 text-white py-1 px-3 rounded"
          >
            Disconnect
          </button>
        </div>
      ) : (
        <>
          <button
            onClick={handleConnect}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded"
          >
            Connect Braavos Wallet
          </button>
          {error && <p className="mt-2 text-red-500">{error}</p>} {/* Display error here */}
        </>
      )}
    </div>
  );
}

