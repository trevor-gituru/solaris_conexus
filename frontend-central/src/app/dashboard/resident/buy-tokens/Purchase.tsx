'use client';

import React, { useEffect, useState } from 'react';
import Sidebar from '../../../../components/Sidebar';
import useAuth from '../../../../hooks/useAuth';
import { Dialog } from '@headlessui/react';
import { connect } from '@starknet-io/get-starknet';

import { WalletAccount, cairo, type Uint256 } from 'starknet';
import { getContract } from '@/lib/strkContract'; // Adjust the path if necessary


const Purchase = () => {
  useAuth();

  const [isLoading, setIsLoading] = useState(false);
  const [amount, setAmount] = useState('');
  const [txHash, setTxHash] = useState<string | null>(null);
  const [transactions, setTransactions] = useState<any[]>([]);
  const [isFetching, setIsFetching] = useState(true);

  const API_URL = process.env.NEXT_PUBLIC_API_URL;

  // Fetch transactions from backend
  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        const token = localStorage.getItem('token');
        const res = await fetch(`${API_URL}/get_token_purchases`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (!res.ok) throw new Error('Failed to fetch transactions');
        const data = await res.json();
        setTransactions(data);
      } catch (err) {
        console.error('Fetch error:', err);
        setTransactions([]);
      } finally {
        setIsFetching(false);
      }
    };

    fetchTransactions();
  }, [API_URL]);

  // Actual purchase token request
  const handleBuy = async () => {
    setIsLoading(true);
    setTxHash(null);

    try {
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

      const contract = await getContract();
      contract.connect(account);

      // Convert STC to STRK (assuming 1 STC = 0.001 STRK)
      const strk_used = parseFloat(amount) / 1000; // 1 STC = 1000 STRK
      const uintAmount = cairo.uint256(strk_used * 10 ** 18); // STRK decimals

      const TO_ADDRESS = process.env.NEXT_PUBLIC_STC_ADDRESS!;
      const call = contract.populate('transfer', {
        recipient: TO_ADDRESS,
        amount: uintAmount,
      });

      const { transaction_hash } = await account.execute(call);
      setTxHash(transaction_hash);
      setAmount('');

      // Log to backend (optional)
      const token = localStorage.getItem('token');
      await fetch(`${API_URL}/add_token_purchase`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          amount_stc: parseFloat(amount),
          tx_hash: transaction_hash,
          strk_used: strk_used,
        }),
      });

      // Refresh transaction history
      const updatedRes = await fetch(`${API_URL}/get_token_purchases`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      const updatedData = await updatedRes.json();
      setTransactions(updatedData);
    } catch (err: any) {
      console.error('Buy Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

return (
  <div className="flex">
    <Sidebar />

    <div className="flex-1 p-6 transition-all duration-300 lg:ml-64 mt-16 lg:mt-0 ml-4 lg:ml-80">
      <h1 className="text-3xl font-bold text-gray-800">Purchase Tokens</h1>
      <p className="mt-4 text-gray-600">
        View your SCT token purchase history and buy more tokens.
      </p>

      {/* Purchase tokens card */}
      <div className="mt-10 bg-white border border-gray-200 rounded-lg shadow-sm p-6 max-w-md">
        <h2 className="text-2xl font-bold mb-4">SCT Token Purchase</h2>
        <div className="flex space-x-4">
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="flex-1 border border-gray-300 rounded px-3 py-2"
            placeholder="Enter amount"
          />
          <button
            onClick={handleBuy}
            disabled={isLoading || !amount}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? 'Processing...' : 'Buy Tokens'}
          </button>
        </div>
      </div>

      {/* Transactions table */}
      <table className="mt-10 min-w-full bg-white border border-gray-200 rounded-lg shadow-sm">
        <thead className="bg-gray-100">
          <tr>
            <th className="text-left px-4 py-2">Date</th>
            <th className="text-left px-4 py-2">Tx Hash</th>
            <th className="text-left px-4 py-2">Amount</th>
            <th className="text-left px-4 py-2">Status</th>
          </tr>
        </thead>
        <tbody>
          {isFetching ? (
            <tr>
              <td colSpan={4} className="text-center py-4">Loading...</td>
            </tr>
          ) : transactions.length === 0 ? (
            <tr>
              <td colSpan={4} className="text-center py-4 text-gray-500">
                No token purchases found.
              </td>
            </tr>
          ) : (
            transactions.map((tx, i) => (
              <tr key={i} className="border-t">
                <td className="px-4 py-2">{new Date(tx.date).toLocaleDateString()}</td>
                <td className="px-4 py-2">
		  <a
		    href={`https://sepolia.starkscan.co/tx/${tx.tx_hash}`}
		    target="_blank"
		    rel="noopener noreferrer"
		    className="text-blue-600 hover:underline break-all"
		    title={tx.tx_hash}
		  >
		    {tx.tx_hash.slice(0, 6)}...{tx.tx_hash.slice(-4)}
		  </a>
		</td>                
		<td className="px-4 py-2">{tx.amount_stc} STC</td>
                <td className="px-4 py-2">{tx.status || 'Confirmed'}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  </div>
);
};

export default Purchase;

