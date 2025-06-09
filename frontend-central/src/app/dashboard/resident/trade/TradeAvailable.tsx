'use client';

import React, { useEffect, useState } from 'react';
import Sidebar from '@/components/Sidebar';
import useAuth from '@/hooks/useAuth';
import { connect } from '@starknet-io/get-starknet';
import { WalletAccount, cairo } from 'starknet';
import { getContract } from '@/lib/strkContract';
import { Dialog } from '@headlessui/react';
import { useToast } from '@/components/providers/ToastProvider';

import { RpcProvider, num, hash } from 'starknet';

const TradeAvailable = () => {
  useAuth();

  const [isLoading, setIsLoading] = useState(false);
  const [txHash, setTxHash] = useState<string | null>(null);
  const [trades, setTrades] = useState<any[]>([]);
  const [isFetching, setIsFetching] = useState(true);
  const [selectedTrade, setSelectedTrade] = useState(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL;
  const PROVIDER_URL = process.env.NEXT_PUBLIC_PROVIDER_URL!;
  const { showToast } = useToast();

  // Fetch available trades
  useEffect(() => {
    const fetchAvailable = async () => {
      try {
        const token = localStorage.getItem('token');
        const res = await fetch(`${API_URL}/residents/trade/available`, {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
        if (!res.ok) throw new Error('Failed to fetch available trades');
        const data = await res.json();
        // ✅ Expecting List[Dict] directly, so we just sort and set
        const sortedTrades = data.data.sort(
          (a: any, b: any) =>
            new Date(b.date).getTime() - new Date(a.date).getTime()
        );

        setTrades(sortedTrades);
        setTrades(data.data || []);
      } catch (err) {
        showToast('Fetch error:', 'error');
        setTrades([]);
      } finally {
        setIsFetching(false);
      }
    };

    fetchAvailable();
  }, [API_URL]);

  const normalizeAddress = (addr: string | null) => {
    if (!addr) return '';
    return '0x' + addr.replace(/^0x/, '').padStart(64, '0').toLowerCase();
  };

  const handleAcceptTrade = async (
    tradeId: number,
    originalTxHash: string,
    strk_price: number,
    sct_offered: number
  ) => {
    setIsLoading(true);
    setTxHash(null);

    try {
      // 0. Fetch receipt to extract local_id and lender address
      const provider = new RpcProvider({ nodeUrl: PROVIDER_URL });
      const receipt = await provider.getTransactionReceipt(originalTxHash);

      const TRADE_EVENT_KEY = num.toHex(hash.starknetKeccak('Trade'));
      const tradeEvent = receipt.events.find(
        (e) => e.keys[0] === TRADE_EVENT_KEY
      );
      if (!tradeEvent)
        throw new Error('Trade event not found in transaction receipt');

      const localIdHex = tradeEvent.data[1];
      const lenderAddress = tradeEvent.data[2];
      const localId = Number(localIdHex);

      showToast(`Accepting trade localId=${localId} lender=${lenderAddress}`);

      // 1. Connect Braavos wallet
      const selectedSWO = await connect({
        modalTheme: 'light',
        include: ['braavos'],
      });

      const account = await WalletAccount.connect(
        { nodeUrl: PROVIDER_URL },
        selectedSWO
      );
      const connectedAddress = normalizeAddress(account?.address);
      const storedAddress = normalizeAddress(
        localStorage.getItem('account_address')
      );
      if (storedAddress !== connectedAddress) {
        showToast(
          `Please switch to the correct Braavos account address: ${storedAddress || 'Not set'}`,
          { type: 'error' }
        );
        setIsLoading(false);
        return;
      }

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
      // 4. Notify backend (you can include lenderAddress if needed)
      const token = localStorage.getItem('token');
      const res = await fetch(`${API_URL}/residents/trade/accept`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          trade_contract_id: localId,
          trade_backend_id: tradeId,
          tx_hash: transaction_hash,
          sct_offered: sct_offered,
        }),
      });
      const result = await res.json();

      if (!res.ok) {
        showToast(result.detail || 'Failed to Accept trade', 'error');
        return;
      }

      showToast('Trade successfully Accepted!', 'success');

      //Remove new trade to top of list
      setTrades((prev) => prev.filter((trade) => trade.id !== tradeId));

      // Clear inputs
    } catch (err: any) {
      showToast('Unexpected error occurred while accepting trade', 'error');
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
          Browse pending trades created by other residents and accept one to
          execute the swap.
        </p>
      </div>

      {/* Trade History Table */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Trade History</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm text-left border border-gray-200">
            <thead className="bg-gray-100 text-gray-700 font-semibold">
              <tr>
                <th className="px-4 py-2">Date</th>
                <th className="px-4 py-2">SCT Offered</th>
                <th className="px-4 py-2 ">STRK Price</th>
                <th className="px-4 py-2 hidden sm:table-cell">Status</th>
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
                    No trades found.
                  </td>
                </tr>
              ) : (
                trades.map((trade, i) => (
                  <tr key={i} className="border-t hover:bg-gray-50">
                    <td className="px-4 py-2">
                      {(() => {
                        const tradeDate = new Date(trade.date);
                        const now = new Date();

                        const isToday =
                          tradeDate.toLocaleDateString('en-KE', {
                            timeZone: 'Africa/Nairobi',
                          }) ===
                          now.toLocaleDateString('en-KE', {
                            timeZone: 'Africa/Nairobi',
                          });

                        return isToday
                          ? tradeDate.toLocaleTimeString('en-KE', {
                              hour: '2-digit',
                              minute: '2-digit',
                              timeZone: 'Africa/Nairobi',
                            })
                          : tradeDate.toLocaleDateString('en-KE', {
                              timeZone: 'Africa/Nairobi',
                            });
                      })()}
                    </td>
                    <td className="px-4 py-2">
                      {Math.floor(trade.sct_offered)} STC
                    </td>
                    <td className="px-4 py-2 ">
                      {Number(trade.strk_price).toFixed(4)} STRK
                    </td>
                    <td className="px-4 py-2 capitalize hidden sm:table-cell">
                      {trade.status}
                    </td>
                    <td className="px-4 py-2">
                      <button
                        onClick={() => setSelectedTrade(trade)}
                        className="text-blue-600 hover:underline"
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
      {/* Trade Details Modal */}
      <Dialog
        open={!!selectedTrade}
        onClose={() => setSelectedTrade(null)}
        className="relative z-50"
      >
        {/* Backdrop */}
        <div className="fixed inset-0 bg-black/30" aria-hidden="true" />

        {/* Modal Panel */}
        <div className="fixed inset-0 flex items-center justify-center p-4">
          <Dialog.Panel className="bg-white rounded-lg p-6 max-w-md w-full shadow-xl">
            <Dialog.Title className="text-lg font-bold mb-4">
              Trade Details
            </Dialog.Title>
            {selectedTrade ? (
              <ul className="space-y-2 text-sm text-gray-700">
                <li>
                  <strong>Date:</strong>{' '}
                  {new Date(selectedTrade.date).toLocaleString('en-KE', {
                    timeZone: 'Africa/Nairobi',
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                    hour12: true, // or false if you want 24-hour format
                  })}
                </li>
                <li>
                  <strong>SCT Offered:</strong> {selectedTrade.sct_offered}
                </li>
                <li>
                  <strong>STRK Price:</strong> {selectedTrade.strk_price}
                </li>
                <li>
                  <strong>Status:</strong> {selectedTrade.status}
                </li>
                <li>
                  <strong>Seller:</strong> {selectedTrade.seller || 'N/A'}
                </li>
                <li>
                  <strong>Buyer:</strong> {selectedTrade.buyer || 'N/A'}
                </li>

                <ul className="space-y-2 text-sm">
                  {selectedTrade.tx_data?.create && (
                    <li>
                      <strong>Create Tx:</strong>{' '}
                      <a
                        href={`https://sepolia.starkscan.co/tx/${selectedTrade.tx_data.create}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-green-600 underline break-words"
                      >
                        {selectedTrade.tx_data.create.slice(0, 6)}...
                        {selectedTrade.tx_data.create.slice(-4)}
                      </a>
                    </li>
                  )}

                  {selectedTrade.status === 'cancelled' &&
                    selectedTrade.tx_data?.cancelled && (
                      <li>
                        <strong>Cancel Tx:</strong>{' '}
                        <a
                          href={`https://sepolia.starkscan.co/tx/${selectedTrade.tx_data.cancelled}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-red-600 underline break-words"
                        >
                          {selectedTrade.tx_data.cancelled.slice(0, 6)}...
                          {selectedTrade.tx_data.cancelled.slice(-4)}
                        </a>
                      </li>
                    )}

                  {selectedTrade.status === 'accepted' && (
                    <>
                      {selectedTrade.tx_data?.accept && (
                        <li>
                          <strong>Accept Tx:</strong>{' '}
                          <a
                            href={`https://sepolia.starkscan.co/tx/${selectedTrade.tx_data.accept}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 underline break-words"
                          >
                            {selectedTrade.tx_data.accept.slice(0, 6)}...
                            {selectedTrade.tx_data.accept.slice(-4)}
                          </a>
                        </li>
                      )}

                      {selectedTrade.tx_data?.pay_accept && (
                        <li>
                          <strong>Pay Accept Tx:</strong>{' '}
                          <a
                            href={`https://sepolia.starkscan.co/tx/${selectedTrade.tx_data.pay_accept}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-purple-600 underline break-words"
                          >
                            {selectedTrade.tx_data.pay_accept.slice(0, 6)}...
                            {selectedTrade.tx_data.pay_accept.slice(-4)}
                          </a>
                        </li>
                      )}

                      {Array.isArray(selectedTrade.tx_data?.pay) &&
                        selectedTrade.tx_data.pay.length > 0 && (
                          <li>
                            <strong>Payment Txs:</strong>
                            <ul className="pl-4 list-disc space-y-1">
                              {selectedTrade.tx_data.pay.map(
                                (tx: string, idx: number) => (
                                  <li key={idx}>
                                    <a
                                      href={`https://sepolia.starkscan.co/tx/${tx}`}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="text-indigo-600 underline break-words"
                                    >
                                      {tx.slice(0, 6)}...{tx.slice(-4)}
                                    </a>
                                  </li>
                                )
                              )}
                            </ul>
                          </li>
                        )}
                    </>
                  )}
                </ul>
              </ul>
            ) : null}

            {/* Close Button */}
            {selectedTrade && (
              <>
                {/* Close Button */}
                <button
                  onClick={() => setSelectedTrade(null)}
                  className="mt-6 w-full text-white bg-gray-800 hover:bg-gray-900 px-4 py-2 rounded"
                >
                  Close
                </button>

                {/* Cancel Trade Button – only when status is pending */}
                {selectedTrade.status === 'pending' && (
                  <button
                    onClick={() =>
                      handleAcceptTrade(
                        selectedTrade.id,
                        selectedTrade.tx_data?.create,
                        selectedTrade.strk_price,
                        selectedTrade.sct_offered
                      )
                    }
                    className="mt-2 w-full text-white bg-red-600 hover:bg-red-700 px-4 py-2 rounded"
                  >
                    Accept Trade
                  </button>
                )}
              </>
            )}
          </Dialog.Panel>
        </div>
      </Dialog>
    </div>
  );
};

export default TradeAvailable;
