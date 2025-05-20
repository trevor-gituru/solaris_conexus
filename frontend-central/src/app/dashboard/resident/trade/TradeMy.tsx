'use client';

import React, { useEffect, useState } from 'react';
import Sidebar from '../../../../components/Sidebar';
import useAuth from '../../../../hooks/useAuth';
import { connect } from '@starknet-io/get-starknet';
import { WalletAccount, cairo } from 'starknet';
import { getContract } from '@/lib/stcContract';

import { RpcProvider, num, hash } from 'starknet';

const TradeMy = () => {
  useAuth();

  const [isLoading, setIsLoading] = useState(false);
  const [stcOffered, setStcOffered] = useState('');
  const [strkPrice, setStrkPrice] = useState('');
  const [txHash, setTxHash] = useState<string | null>(null);
  const [trades, setTrades] = useState<any[]>([]);
  const [isFetching, setIsFetching] = useState(true);

  const API_URL = process.env.NEXT_PUBLIC_API_URL;

  // Fetch trades
  useEffect(() => {
    const fetchTrades = async () => {
      try {
        const token = localStorage.getItem('token');
        const res = await fetch(`${API_URL}/get_user_trade`, {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (!res.ok) throw new Error('Failed to fetch trade history');
        const data = await res.json();
        setTrades(data.trades || []);
      } catch (err) {
        console.error('Fetch error:', err);
        setTrades([]);
      } finally {
        setIsFetching(false);
      }
    };

    fetchTrades();
  }, [API_URL]);

  const handleCreateTrade = async () => {
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

      // Calculate STC amount used
      const uintAmount = cairo.uint256(parseFloat(stcOffered));

      const call = contract.populate('createTrade', {
        amount: uintAmount,
      });

      const { transaction_hash } = await account.execute(call);
      setTxHash(transaction_hash);

      // Send trade details to backend
      const token = localStorage.getItem('token');
      await fetch(`${API_URL}/create_trade`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          stc_offered: parseFloat(stcOffered),
          strk_price: strkPrice,
          tx_hash: transaction_hash,
        }),
      });

      setStcOffered('');
      setStrkPrice('');

      // Refresh trade history
      const updatedRes = await fetch(`${API_URL}/get_user_trade`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      const updatedData = await updatedRes.json();
      setTrades(updatedData.trades || []);
    } catch (err: any) {
      console.error('Trade Error:', err);
    } finally {
      setIsLoading(false);
    }
  };


const handleDeleteTrade = async (tradeId: string, originalTxHash: string) => {
  setIsLoading(true);
  setTxHash(null);

  if (!window.confirm('Are you sure you want to delete this trade?')) {
    setIsLoading(false);
    return;
  }

  try {
    // 1. Fetch receipt to extract local_id of trade event
    const provider = new RpcProvider({ nodeUrl: process.env.NEXT_PUBLIC_PROVIDER_URL! });
    const receipt = await provider.getTransactionReceipt(originalTxHash);

    const TRADE_EVENT_KEY = num.toHex(hash.starknetKeccak('Trade'));
    const tradeEvent = receipt.events.find((e) => e.keys[0] === TRADE_EVENT_KEY);

    if (!tradeEvent) {
      throw new Error('Trade event not found in transaction receipt');
    }
    // Assuming local_id is first element in event data array (adjust if needed)
    const localIdHex = tradeEvent.data[1];
    const localId = Number(localIdHex);
    // 2. Connect wallet and contract
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

    // 3. Call deleteTrade with localId
    const call = contract.populate('deleteTrade', { trade_id: localId });

    const { transaction_hash } = await account.execute(call);
    setTxHash(transaction_hash);

    // 4. Send tradeId and delete tx hash to backend to update status
    const token = localStorage.getItem('token');
    await fetch(`${API_URL}/cancel_trade`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        trade_id: parseInt(tradeId, 10), 
        tx_hash: transaction_hash,
      }),
    });

    // 5. Refresh trade list
    const updatedRes = await fetch(`${API_URL}/get_user_trade`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    const updatedData = await updatedRes.json();
    setTrades(updatedData.trades || []);
  } catch (err: any) {
    console.error('Delete Trade Error:', err);
  } finally {
    setIsLoading(false);
  }
};


  return (
  <div className="flex flex-col w-full px-4 py-6  mt-20">
    {/* Header */}
    <div className="mb-8">
      <h1 className="text-3xl font-bold text-gray-800">My Trades</h1>
      <p className="mt-2 text-gray-600">Create a trade and view your trade history.</p>
    </div>

    {/* Create Trade Section */}
    <div className="bg-white shadow rounded-lg p-6 mb-10">
      <h2 className="text-xl font-semibold mb-4">Create New Trade</h2>
      <div className="flex flex-wrap gap-4">
        <input
          type="number"
          value={stcOffered}
          onChange={(e) => setStcOffered(e.target.value)}
          className="w-full sm:w-40 border border-gray-300 rounded px-3 py-2"
          placeholder="STC Offered"
        />
        <input
          type="number"
          value={strkPrice}
          onChange={(e) => setStrkPrice(e.target.value)}
          className="w-full sm:w-40 border border-gray-300 rounded px-3 py-2"
          placeholder="STRK Price"
        />
        <button
          onClick={handleCreateTrade}
          disabled={isLoading || !stcOffered || !strkPrice}
          className="bg-green-600 text-white px-5 py-2 rounded hover:bg-green-700 disabled:opacity-50"
        >
          {isLoading ? 'Submitting...' : 'Create Trade'}
        </button>
      </div>
      {txHash && (
        <p className="mt-4 text-sm text-blue-600 break-all">
          Tx Submitted: {txHash}
        </p>
      )}
    </div>

    {/* Trade History Table */}
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">Trade History</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm text-left border border-gray-200">
          <thead className="bg-gray-100 text-gray-700 font-semibold">
            <tr>
              <th className="px-4 py-2">Date</th>
              <th className="px-4 py-2">Tx Hash</th>
              <th className="px-4 py-2">STC Offered</th>
              <th className="px-4 py-2">STRK Price</th>
              <th className="px-4 py-2">Status</th>
              <th className="px-4 py-2">Buyer</th>
              <th className="px-4 py-2">Action</th>
            </tr>
          </thead>
          <tbody>
            {isFetching ? (
              <tr>
                <td colSpan={7} className="text-center py-4">Loading...</td>
              </tr>
            ) : trades.length === 0 ? (
              <tr>
                <td colSpan={7} className="text-center py-4 text-gray-500">No trades found.</td>
              </tr>
            ) : (
              trades.map((trade, i) => (
                <tr key={i} className="border-t hover:bg-gray-50">
                  <td className="px-4 py-2">{new Date(trade.date).toLocaleDateString()}</td>
                  <td className="px-4 py-2">
			  <a
			    href={`https://sepolia.starkscan.co/tx/${trade.tx_hash}`}
			    target="_blank"
			    rel="noopener noreferrer"
			    className="text-blue-600 hover:underline"
			    title={trade.tx_hash}
			  >
			    {trade.tx_hash.slice(0, 6)}...{trade.tx_hash.slice(-4)}
			  </a>
		</td>
                  <td className="px-4 py-2">{trade.stc_offered} STC</td>
                  <td className="px-4 py-2">{trade.strk_price} STRK</td>
                  <td className="px-4 py-2 capitalize">{trade.status}</td>
                  <td className="px-4 py-2">{trade.buyer || 'N/A'}</td>
                  <td className="px-4 py-2">
                    {trade.status === 'pending' && (
                      <button
                        onClick={() => handleDeleteTrade(trade.id, trade.tx_hash)}
                        className="text-red-600 hover:underline"
                      >
                        Delete
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  </div>
);
};

export default TradeMy;

