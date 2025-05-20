'use client';

import React, { useEffect, useState } from 'react';
import Sidebar from '../../../../components/Sidebar';
import useAuth from '../../../../hooks/useAuth';
import { connect } from '@starknet-io/get-starknet';
import { WalletAccount, cairo } from 'starknet';
import { getContract } from '@/lib/strkContract';


import { RpcProvider, num, hash } from 'starknet';

const TradeAvailable = () => {
  useAuth();

  const [isLoading, setIsLoading] = useState(false);
  const [txHash, setTxHash] = useState<string | null>(null);
  const [trades, setTrades] = useState<any[]>([]);
  const [isFetching, setIsFetching] = useState(true);

  const API_URL = process.env.NEXT_PUBLIC_API_URL;
  const PROVIDER_URL = process.env.NEXT_PUBLIC_PROVIDER_URL!;

  // Fetch available trades
  useEffect(() => {
    const fetchAvailable = async () => {
      try {
        const token = localStorage.getItem('token');
        const res = await fetch(`${API_URL}/get_free_trade`, {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
        if (!res.ok) throw new Error('Failed to fetch available trades');
        const data = await res.json();
        setTrades(data.trades || []);
      } catch (err) {
        console.error('Fetch error:', err);
        setTrades([]);
      } finally {
        setIsFetching(false);
      }
    };

    fetchAvailable();
  }, [API_URL]);

 const handleAcceptTrade = async (tradeId: number, originalTxHash: string, strk_price: number, stc_offered: number) => {
  setIsLoading(true);
  setTxHash(null);

  try {
    // 0. Fetch receipt to extract local_id and lender address
    const provider = new RpcProvider({ nodeUrl: PROVIDER_URL });
    const receipt = await provider.getTransactionReceipt(originalTxHash);

    const TRADE_EVENT_KEY = num.toHex(hash.starknetKeccak('Trade'));
    const tradeEvent = receipt.events.find(e => e.keys[0] === TRADE_EVENT_KEY);
    if (!tradeEvent) throw new Error('Trade event not found in transaction receipt');

    const localIdHex    = tradeEvent.data[1];
    const lenderAddress = tradeEvent.data[2];
    const localId       = Number(localIdHex);

    console.log('Accepting trade localId=', localId, 'lender=', lenderAddress);

    // 1. Connect Braavos wallet
    const selectedSWO = await connect({
      modalMode: 'alwaysAsk',
      modalTheme: 'light',
      include: ['braavos'],
    });
    if (!selectedSWO || selectedSWO.id !== 'braavos') {
      throw new Error('Braavos wallet is required');
    }
    const account = await WalletAccount.connect(
      { nodeUrl: PROVIDER_URL },
      selectedSWO
    );

    // 2. Connect contract
    const contract = await getContract();
    contract.connect(account);

    // 3. Call acceptTrade on-chain with localId
    const uintAmount = cairo.uint256(strk_price * 10 ** 18); // STRK decimals

    const call = contract.populate('transfer', {
      recipient: lenderAddress,
        amount: uintAmount,

    });
    const { transaction_hash } = await account.execute(call);
    setTxHash(transaction_hash);
    const sct_offered = stc_offered
    // 4. Notify backend (you can include lenderAddress if needed)
    const token = localStorage.getItem('token');
    await fetch(`${API_URL}/accept_trade`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        trade_contract_id: localId,
        trade_backend_id: tradeId,
        tx_hash: transaction_hash,
	sct_offered: sct_offered
      }),
    });

    // 5. Refresh list
    const updatedRes = await fetch(`${API_URL}/get_free_trade`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    const updatedData = await updatedRes.json();
    setTrades(updatedData.trades || []);
  } catch (err: any) {
    console.error('Accept Trade Error:', err);
  } finally {
    setIsLoading(false);
  }
};
  return (
    <div className="flex flex-col w-full px-4 py-6 mt-20">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Available Trades</h1>
        <p className="mt-2 text-gray-600">
          Browse pending trades created by other residents and accept one to execute the swap.
        </p>
      </div>

      {/* Submission Tx Hash */}
      {txHash && (
        <p className="mb-4 text-sm text-blue-600 break-all">
          Transaction Submitted: {txHash}
        </p>
      )}

      {/* Trades Table */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm text-left border border-gray-200">
            <thead className="bg-gray-100 text-gray-700 font-semibold">
              <tr>
                <th className="px-4 py-2">Date</th>
                <th className="px-4 py-2">Tx Hash</th>
                <th className="px-4 py-2">SCT Offered</th>
                <th className="px-4 py-2">STRK Price</th>
                <th className="px-4 py-2">Action</th>
              </tr>
            </thead>
            <tbody>
              {isFetching ? (
                <tr>
                  <td colSpan={5} className="text-center py-4">
                    Loading...
                  </td>
                </tr>
              ) : trades.length === 0 ? (
                <tr>
                  <td colSpan={5} className="text-center py-4 text-gray-500">
                    No available trades.
                  </td>
                </tr>
              ) : (
                trades.map((trade) => (
                  <tr key={trade.id} className="border-t hover:bg-gray-50">
                    <td className="px-4 py-2">
                      {new Date(trade.date).toLocaleDateString()}
                    </td>
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
                    <td className="px-4 py-2">{trade.stc_offered} SCT</td>
                    <td className="px-4 py-2">{trade.strk_price} STRK</td>
                    <td className="px-4 py-2">
                      <button
                        onClick={() =>
                          handleAcceptTrade(trade.id, trade.tx_hash, trade.strk_price, trade.stc_offered)
                        }
                        disabled={isLoading}
                        className="text-green-600 hover:underline disabled:opacity-50"
                      >
                        {isLoading ? 'Processing...' : 'Accept'}
                      </button>
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

export default TradeAvailable;

