// components/ConnectWallet.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { connect } from '@starknet-io/get-starknet';     // v4+
import { WalletAccount } from 'starknet';               // v6+
import { useToast } from '@/components/providers/ToastProvider';
import { UserIcon, ClipboardIcon } from '@heroicons/react/24/outline'; // Import ClipboardIcon

const PROVIDER_URL = process.env.NEXT_PUBLIC_PROVIDER_URL; 
const ERC20_ADDRESS = process.env.NEXT_PUBLIC_STC_ADDRESS; 

export default function ConnectWallet() {
  const [walletAccount, setWalletAccount] = useState<WalletAccount | null>(null);
  const [address, setAddress] = useState<string>('');
  const [hasPromptedAdd, setHasPromptedAdd] = useState(false);
  const { showToast } = useToast();

  const handleConnect = async () => {
  try {
    if (!PROVIDER_URL || !ERC20_ADDRESS) {
      showToast('Missing configuration: PROVIDER_URL or STC_ADDRESS', 'error');
      return;
    }

    const selectedSWO = await connect({
      modalTheme: 'light',
      include: ['braavos'],
    });

    if (!selectedSWO) {
      showToast('No wallet selected', 'error');
      return;
    }

    const wa = await WalletAccount.connect(
      { nodeUrl: PROVIDER_URL },
      selectedSWO
    );

    // Defensive check for null or malformed wallet
    if (!wa?.address) {
      showToast('Failed to connect to wallet (missing address)', 'error');
      return;
    }

    setWalletAccount(wa);
    setAddress(wa.address);
    setHasPromptedAdd(false);
    showToast('Wallet connected successfully', 'success');

  } catch (err: any) {
    console.error('Connection Error:', err);

    // Convert object error to readable string
    const message =
      typeof err === 'string'
        ? err
        : err?.message
        || JSON.stringify(err)
        || 'Unknown error occurred during wallet connection';

    showToast(message, 'error');
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
        showToast('Failed to add token to wallet', 'error');
      } finally {
        setHasPromptedAdd(true);
      }
    })();
  }, [walletAccount, hasPromptedAdd]);

  const handleDisconnect = () => {
    setWalletAccount(null);
    setAddress('');
    setHasPromptedAdd(false);
    showToast('Wallet disconnected', 'info');
  };

  return (
    <div className="p-4">
      {walletAccount ? (
        <div className="space-y-4">
          <p className="text-green-600 flex items-center space-x-2">
            <span>Connected: {address.slice(0, 6)}...{address.slice(-4)}</span>

	    <button
	    type="button"
	      onClick={() => {
		  navigator.clipboard.writeText(address)
		    .then(() => showToast('Wallet address copied!', 'success'))
		    .catch(() => showToast('Failed to copy address', 'error'));
		}}
	      className="text-gray-400 hover:text-gray-600"
	      title="Copy wallet address"
	    >
	      <ClipboardIcon className="h-5 w-5" />
	    </button>

          </p>

          <button
	    type="button"
            onClick={handleDisconnect}
            className="bg-red-500 text-white py-1 px-3 rounded"
          >
            Disconnect
          </button>
        </div>
      ) : (
        <>
          <button
	    type="button"
            onClick={handleConnect}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded"
          >
            Connect Braavos Wallet
          </button>
        </>
      )}
    </div>
  );
}
