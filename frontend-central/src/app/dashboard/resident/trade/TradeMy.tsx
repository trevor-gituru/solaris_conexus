'use client';

import React, { useEffect, useState } from 'react';
import Sidebar from '@/components/Sidebar';
import useAuth from '@/hooks/useAuth';
import { connect } from '@starknet-io/get-starknet';
import { WalletAccount, cairo } from 'starknet';
import { getContract } from '@/lib/stcContract';
import { Dialog } from '@headlessui/react';
import { useToast } from '@/components/providers/ToastProvider';

import { RpcProvider, num, hash } from 'starknet';

const TradeMy = () => {
  useAuth();

  const [isLoading, setIsLoading] = useState(false);
  const [stcOffered, setStcOffered] = useState('');
  const [strkPrice, setStrkPrice] = useState('');
  const [txHash, setTxHash] = useState<string | null>(null);
  const [trades, setTrades] = useState<any[]>([]);
  const [isFetching, setIsFetching] = useState(true);
  const [selectedTrade, setSelectedTrade] = useState(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL;
  const { showToast } = useToast();

  // Fetch trades
useEffect(() => {
  const fetchTrades = async () => {
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API_URL}/residents/trade/user`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!res.ok) throw new Error("Failed to fetch trade history");

      const data = await res.json();

      // ✅ Expecting List[Dict] directly, so we just sort and set
      const sortedTrades = data.data.sort(
        (a: any, b: any) => new Date(b.date).getTime() - new Date(a.date).getTime()
      );

      setTrades(sortedTrades);
    } catch (err) {
      showToast("Fetch error:", "error");
      setTrades([]);
    } finally {
      setIsFetching(false);
    }
  };

  fetchTrades();
}, [API_URL]);

const normalizeAddress = (addr: string | null) => {
  if (!addr) return '';
  return '0x' + addr.replace(/^0x/, '').padStart(64, '0').toLowerCase();
};


 const handleCreateTrade = async () => {
  setIsLoading(true);

  try {
    const selectedSWO = await connect({
      modalTheme: 'light',
      include: ['braavos'],
    });

    const account = await WalletAccount.connect(
      { nodeUrl: process.env.NEXT_PUBLIC_PROVIDER_URL! },
      selectedSWO
    );
    const connectedAddress = normalizeAddress(account?.address);
    const storedAddress = normalizeAddress(localStorage.getItem('account_address'));
    if (storedAddress !== connectedAddress) {
      showToast(
        `Please switch to the correct Braavos account address: ${storedAddress || 'Not set'}`,
        { type: 'error' }
      );
      setIsLoading(false);
      return;
    }

    const contract = await getContract();
    contract.connect(account);

    const uintAmount = cairo.uint256(parseFloat(stcOffered));
    const call = contract.populate('createTrade', { amount: uintAmount });

    const { transaction_hash } = await account.execute(call);

    // Send trade to backend
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_URL}/residents/trade/create`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        sct_offered: parseFloat(stcOffered),
        strk_price: strkPrice,
        tx_hash: transaction_hash,
        date: new Date().toISOString(),
      }),
    });

    const result = await res.json();

    if (!res.ok) {
      showToast(result.message || 'Failed to create trade', { type: 'error' });
      return;
    }

    showToast('Trade successfully created!', { type: 'success' });

    // Add new trade to top of list
    setTrades((prev) => [result.data, ...prev]);

    // Clear inputs
    setStcOffered('');
    setStrkPrice('');
  } catch (err: any) {
    showToast('Unexpected error occurred while creating trade', { type: 'error' });
  } finally {
    setIsLoading(false);
  }
};


const handleDeleteTrade = async (tradeId: string, originalTxHash: string) => {
  setIsLoading(true);
  setTxHash(null);
  try {
    // 1. Fetch receipt to extract local_id of trade event
    const provider = new RpcProvider({ nodeUrl: process.env.NEXT_PUBLIC_PROVIDER_URL! });
    const receipt = await provider.getTransactionReceipt(originalTxHash);

    const TRADE_EVENT_KEY = num.toHex(hash.starknetKeccak('Trade'));
    const tradeEvent = receipt.events.find((e) => e.keys[0] === TRADE_EVENT_KEY);

    if (!tradeEvent) {
      showToast('Trade event not found in transaction receipt', "error");
      return;
    }
    // Assuming local_id is first element in event data array (adjust if needed)
    const localIdHex = tradeEvent.data[1];
    const localId = Number(localIdHex);
    // 2. Connect wallet and contract
    const selectedSWO = await connect({
      modalTheme: 'light',
      include: ['braavos'],
    });

    const account = await WalletAccount.connect(
      { nodeUrl: process.env.NEXT_PUBLIC_PROVIDER_URL! },
      selectedSWO
    );
    const connectedAddress = normalizeAddress(account?.address);
    const storedAddress = normalizeAddress(localStorage.getItem('account_address'));
    if (storedAddress !== connectedAddress) {
      showToast(
        `Please switch to the correct Braavos account address: ${storedAddress || 'Not set'}`,
        { type: 'error' }
      );
      setIsLoading(false);
      return;
    }


    const contract = await getContract();
    contract.connect(account);
    // 3. Call deleteTrade with localId
    const call = contract.populate('deleteTrade', { trade_id: localId });

    const { transaction_hash } = await account.execute(call);

    // 4. Send tradeId and delete tx hash to backend to update status
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_URL}/residents/trade/cancel`, {
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

    const result = await res.json();

    if (!res.ok) {
      showToast(result.detail || 'Failed to delete trade', 'error');
      return;
    }

    showToast('Trade successfully Deleted!', 'success');

    // Add new trade to top of list
    setTrades((prev) =>
  prev.map((trade) =>
    trade.id === result.data.id ? result.data : trade
  )
);

    // Clear inputs
  } catch (err: any) {
    showToast('Unexpected error occurred while deleting trade', 'error');
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
          placeholder="SCT Offered"
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
      <th className="px-4 py-2">SCT Offered</th>
      <th className="px-4 py-2">Status</th>
      <th className="px-4 py-2 hidden md:table-cell">STRK Price</th>
      <th className="px-4 py-2">Action</th>
    </tr>
  </thead>
  <tbody>
    {isFetching ? (
      <tr>
        <td colSpan={5} className="text-center py-4">Loading...</td>
      </tr>
    ) : trades.length === 0 ? (
      <tr>
        <td colSpan={5} className="text-center py-4 text-gray-500">No trades found.</td>
      </tr>
    ) : (
      trades.map((trade, i) => (
        <tr key={i} className="border-t hover:bg-gray-50">
          <td className="px-4 py-2">
            {(() => {
              const tradeDate = new Date(trade.date);
              const now = new Date();
              const isToday = tradeDate.toDateString() === now.toDateString();
              return isToday
                ? tradeDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                : tradeDate.toLocaleDateString();
            })()}
          </td>
          <td className="px-4 py-2">{Math.floor(trade.sct_offered)} SCT</td>
          <td className="px-4 py-2 capitalize">{trade.status}</td>
          <td className="px-4 py-2 hidden md:table-cell">{trade.strk_price} STRK</td>
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
<Dialog open={!!selectedTrade} onClose={() => setSelectedTrade(null)} className="relative z-50">
  {/* Backdrop */}
  <div className="fixed inset-0 bg-black/30" aria-hidden="true" />

  {/* Modal Panel */}
  <div className="fixed inset-0 flex items-center justify-center p-4">
    <Dialog.Panel className="bg-white rounded-lg p-6 max-w-md w-full shadow-xl">
      <Dialog.Title className="text-lg font-bold mb-4">Trade Details</Dialog.Title>
      {selectedTrade ? (
        <ul className="space-y-2 text-sm text-gray-700">
          <li><strong>Date:</strong> {new Date(selectedTrade.date).toLocaleString()}</li>
          <li><strong>SCT Offered:</strong> {selectedTrade.sct_offered}</li>
          <li><strong>STRK Price:</strong> {selectedTrade.strk_price}</li>
          <li><strong>Status:</strong> {selectedTrade.status}</li>
          <li><strong>Seller:</strong> {selectedTrade.seller || 'N/A'}</li>
          <li><strong>Buyer:</strong> {selectedTrade.buyer || 'N/A'}</li>

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
        {selectedTrade.tx_data.create.slice(0, 6)}...{selectedTrade.tx_data.create.slice(-4)}
      </a>
    </li>
  )}

  {selectedTrade.status === 'cancelled' && selectedTrade.tx_data?.cancelled && (
    <li>
      <strong>Cancel Tx:</strong>{' '}
      <a
        href={`https://sepolia.starkscan.co/tx/${selectedTrade.tx_data.cancelled}`}
        target="_blank"
        rel="noopener noreferrer"
        className="text-red-600 underline break-words"
      >
        {selectedTrade.tx_data.cancelled.slice(0, 6)}...{selectedTrade.tx_data.cancelled.slice(-4)}
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
            {selectedTrade.tx_data.accept.slice(0, 6)}...{selectedTrade.tx_data.accept.slice(-4)}
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
            {selectedTrade.tx_data.pay_accept.slice(0, 6)}...{selectedTrade.tx_data.pay_accept.slice(-4)}
          </a>
        </li>
      )}

      {Array.isArray(selectedTrade.tx_data?.pay) && selectedTrade.tx_data.pay.length > 0 && (
        <li>
          <strong>Payment Txs:</strong>
          <ul className="pl-4 list-disc space-y-1">
            {selectedTrade.tx_data.pay.map((tx: string, idx: number) => (
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
            ))}
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
        onClick={() => handleDeleteTrade(selectedTrade.id, selectedTrade.tx_data?.create)}
        className="mt-2 w-full text-white bg-red-600 hover:bg-red-700 px-4 py-2 rounded"
      >
        Cancel Trade
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

export default TradeMy;

