'use client';

import React, { useEffect, useState } from 'react';
import Sidebar from '@/components/Sidebar';
import { useToast } from '@/components/providers/ToastProvider';
import useAuth from '@/hooks/useAuth';
import { connect } from '@starknet-io/get-starknet';
import { WalletAccount, cairo } from 'starknet';
import { getContract } from '@/lib/strkContract';
import { Dialog } from '@headlessui/react';

const isToday = (dateStr: string) => {
  const givenDate = new Date(dateStr);
  const today = new Date();
  return (
    givenDate.getDate() === today.getDate() &&
    givenDate.getMonth() === today.getMonth() &&
    givenDate.getFullYear() === today.getFullYear()
  );
};

const formatTime = (dateStr: string) => {
  const date = new Date(dateStr);
  return date.toLocaleTimeString('en-US', { hour12: false });
};

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr);
  return date.toLocaleDateString();
};

const Purchase = () => {
  useAuth();

  const [isLoading, setIsLoading] = useState(false);
  const [amount, setAmount] = useState('');
  const [txHash, setTxHash] = useState<string | null>(null);
  const [selectedTx, setSelectedTx] = useState<any | null>(null);
  const [transactions, setTransactions] = useState<any[]>([]);
  const [isFetching, setIsFetching] = useState(true);
  const [isLoadingMpesa, setIsLoadingMpesa] = useState(false);
  const [apiSuccessMpesa, setApiSuccessMpesa] = useState(false);

  const API_URL = process.env.NEXT_PUBLIC_API_URL;
  const { showToast } = useToast();

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        const token = localStorage.getItem('token');
        const res = await fetch(`${API_URL}/residents/token_purchase/get`, {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (!res.ok) {
          showToast('Failed to fetch transactions', 'error');
          setTransactions([]);
          return;
        }

        const data = await res.json();

        // Sort transactions from newest to oldest
        const sortedData = data.data.sort(
          (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
        );

        setTransactions(sortedData);
      } catch (err) {
        showToast('An error occurred while fetching transactions', {
          type: 'error',
        });
        setTransactions([]);
      } finally {
        setIsFetching(false);
      }
    };

    fetchTransactions();
  }, [API_URL]);

  const normalizeAddress = (addr: string | null) => {
    if (!addr) return '';
    return '0x' + addr.replace(/^0x/, '').padStart(64, '0').toLowerCase();
  };

  const handleBuyStrk = async () => {
    setIsLoading(true);
    setTxHash(null);

    try {
      const selectedSWO = await connect({
        modalTheme: 'light',
        include: ['braavos'],
      });

      if (!selectedSWO || selectedSWO.id !== 'braavos') {
        showToast('Braavos wallet is required', { type: 'error' });
        setIsLoading(false);
        return;
      }

      const account = await WalletAccount.connect(
        { nodeUrl: process.env.NEXT_PUBLIC_PROVIDER_URL! },
        selectedSWO
      );

      const connectedAddress = normalizeAddress(account.address);
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

      const contract = await getContract();
      contract.connect(account);
      const strk_used = parseFloat(amount) / 1000;
      const uintAmount = cairo.uint256(strk_used * 10 ** 18);
      const TO_ADDRESS = process.env.NEXT_PUBLIC_STC_ADDRESS!;
      const call = contract.populate('transfer', {
        recipient: TO_ADDRESS,
        amount: uintAmount,
      });
      const { transaction_hash } = await account.execute(call);
      setTxHash(transaction_hash);

      // Prepare payload to send to backend
      const token = localStorage.getItem('token');
      const kenyaTimeString = new Date().toLocaleString('sv-SE', {
        timeZone: 'Africa/Nairobi',
      });
      // Format: "2025-06-10 08:42:10"

      // Optionally convert to ISO-like format
      const kenyaTimeISO = kenyaTimeString.replace(' ', 'T');

      const bodyPayload = {
        amount_sct: parseFloat(amount),
        payment_tx_id: transaction_hash,
        strk_used: strk_used,
        payment_method: 'STRK',
        date: kenyaTimeISO, // e.g., "2025-06-10T08:42:10"
      };

      // POST new purchase to backend
      const addRes = await fetch(
        `${API_URL}/residents/token_purchase/add_strk`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(bodyPayload),
        }
      );

      const addData = await addRes.json();

      if (!addRes.ok) {
        // Show backend error detail if available
        const errMsg = addData?.detail || 'Failed to add purchase';
        showToast(errMsg, 'error');
        setIsLoading(false);
        return;
      }

      showToast('Purchase successful!', 'success');

      // The backend returns the newly created transaction in addData.data (assumed)
      const newTransaction = addData.data;
      if (newTransaction) {
        // Prepend new transaction to existing list
        setTransactions((prev) => [newTransaction, ...prev]);
      }

      setAmount('');
    } catch (err: any) {
      showToast(err?.message || 'An error occurred during purchase', {
        type: 'error',
      });
    } finally {
      setIsLoading(false);
    }
  };

  // M-PESA
  const handleMpesaInit = async () => {
    setIsLoadingMpesa(true);

    try {
      const token = localStorage.getItem('token');

      const amountFloat = parseFloat(amount);
      if (!amountFloat || isNaN(amountFloat)) {
        showToast('Please enter a valid amount', { type: 'error' });
        setIsLoading(false);
        return;
      }

      const strk_used = amountFloat * 10; // Assuming 1 SCT = 10 STRK equivalent in MPESA value

      const payload = {
        amount_sct: amountFloat,
        payment_tx_id: 'MPESA',
        payment_method: 'MPESA',
        strk_used: strk_used,
        date: new Date().toISOString(),
      };

      const response = await fetch(
        `${API_URL}/residents/token_purchase/add_mpesa`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        }
      );

      const result = await response.json();

      if (!response.ok) {
        const errMsg =
          result?.detail ||
          result?.message ||
          'Failed to initiate MPESA payment';
        showToast(errMsg, { type: 'error' });
        setIsLoading(false);
        return;
      }

      showToast(result?.message || 'M-PESA payment recorded successfully!', {
        type: 'success',
      });

      const newTransaction = result.data;
      if (newTransaction) {
        setTransactions((prev) => [newTransaction, ...prev]);
      }

      setApiSuccessMpesa(true); // This enables Confirm / Cancel buttons
      setAmount('');
    } catch (error: any) {
      showToast(
        error?.message || 'Unexpected error occurred during M-PESA payment.',
        {
          type: 'error',
        }
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleMpesaConfirm = async () => {
    setIsLoading(true);

    try {
      const token = localStorage.getItem('token');

      const confirmRes = await fetch(
        `${API_URL}/residents/token_purchase/confirm_mpesa`,
        {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const confirmData = await confirmRes.json();

      if (!confirmRes.ok) {
        const errMsg =
          confirmData?.detail || 'Failed to confirm MPESA purchase';
        showToast(errMsg, 'error');
        setIsLoading(false);
        return;
      }

      showToast('MPESA purchase confirmed successfully!', 'success');
      setApiSuccessMpesa(false);
      setIsLoadingMpesa(false);

      const newTransaction = confirmData.data;
      if (newTransaction) {
        setTransactions((prev) => [newTransaction, ...prev]);
      }

      setAmount('');
    } catch (err: any) {
      showToast(err?.message || 'An error occurred during MPESA confirmation', {
        type: 'error',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleMpesaCancel = () => {
    setApiSuccessMpesa(false); // Hide confirm/cancel buttons
    setIsLoadingMpesa(false);
  };

  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1 p-6 transition-all duration-300 lg:ml-64 mt-16 lg:mt-0 ml-4 lg:ml-80">
        <h1 className="text-3xl font-bold text-gray-800">Purchase Tokens</h1>
        <p className="mt-4 text-gray-600">
          View your SCT token purchase history and buy more tokens.
        </p>

        {/* Purchase form */}
        {/* Purchase form */}
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
          </div>

          {/* Action buttons */}
          {!apiSuccessMpesa && (
            <div className="flex space-x-4 mt-6">
              <button
                onClick={handleBuyStrk}
                disabled={isLoading || !amount}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
              >
                {isLoading ? 'Processing...' : 'Pay STRK'}
              </button>

              <button
                onClick={handleMpesaInit}
                disabled={isLoadingMpesa || !amount}
                className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
              >
                {isLoadingMpesa ? 'Processing...' : 'Pay M-PESA'}
              </button>
            </div>
          )}
          {/* Conditional buttons shown only if M-PESA request succeeded */}
          {apiSuccessMpesa && (
            <div className="flex space-x-4 mt-4">
              <button
                onClick={handleMpesaConfirm}
                className="bg-gray-800 text-white px-4 py-2 rounded hover:bg-gray-900"
              >
                Confirm
              </button>
              <button
                onClick={handleMpesaCancel}
                className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
              >
                Cancel
              </button>
            </div>
          )}
        </div>

        {/* Purchase history table */}

        {/* Transactions table */}
        <div className="mt-10">
          <div className="hidden sm:block">
            <table className="mt-10 min-w-full bg-white border border-gray-200 shadow-sm rounded-xl overflow-hidden">
              <thead className="bg-gray-100">
                <tr>
                  <th className="text-left px-4 py-2">Date</th>
                  <th className="text-left px-4 py-2">Tx Hash</th>
                  <th className="text-left px-4 py-2">Amount (SCT)</th>
                  <th className="text-left px-4 py-2">Amount Used</th>
                  <th className="text-left px-4 py-2">Payment Method</th>
                  <th className="text-left px-4 py-2">Payment Tx</th>
                </tr>
              </thead>
              <tbody>
                {isFetching ? (
                  <tr>
                    <td colSpan={6} className="text-center py-4">
                      Loading...
                    </td>
                  </tr>
                ) : transactions.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="text-center py-4 text-gray-500">
                      No token purchases found.
                    </td>
                  </tr>
                ) : (
                  transactions.map((tx, i) => (
                    <tr key={i} className="border-t hover:bg-gray-50">
                      <td className="px-4 py-2">
                        {isToday(tx.date)
                          ? formatTime(tx.date)
                          : formatDate(tx.date)}
                      </td>
                      <td className="px-4 py-2">
                        <a
                          href={`https://sepolia.starkscan.co/tx/${tx.sct_tx_hash}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline break-all"
                          title={tx.sct_tx_hash}
                        >
                          {tx.sct_tx_hash.slice(0, 6)}...
                          {tx.sct_tx_hash.slice(-4)}
                        </a>
                      </td>
                      <td className="px-4 py-2">{tx.amount_sct} SCT</td>
                      <td className="px-4 py-2">
                        {tx.payment_method === 'MPESA'
                          ? `Ksh ${tx.strk_used}`
                          : `${tx.strk_used} STRK`}
                      </td>
                      <td className="px-4 py-2">{tx.payment_method}</td>
                      <td className="px-4 py-2">
                        {tx.payment_method === 'STRK' ? (
                          <a
                            href={`https://sepolia.starkscan.co/tx/${tx.payment_tx_id}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-green-600 hover:underline break-all"
                          >
                            {tx.payment_tx_id.slice(0, 6)}...
                            {tx.payment_tx_id.slice(-4)}
                          </a>
                        ) : (
                          <span className="break-all">
                            {tx.payment_tx_id.slice(0, 6)}...
                            {tx.payment_tx_id.slice(-4)}
                          </span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Mobile View */}
          <div className="sm:hidden">
            {transactions.map((tx, i) => (
              <div
                key={i}
                className="border border-gray-200 rounded-lg shadow-sm p-4 mb-4 bg-white"
              >
                <div className="flex justify-between items-center">
                  <div>
                    <div className="text-sm text-gray-600">
                      {new Date(tx.date).toDateString() ===
                      new Date().toDateString()
                        ? new Date(tx.date).toLocaleTimeString()
                        : new Date(tx.date).toLocaleDateString()}
                    </div>
                    <div className="text-lg font-semibold">
                      {tx.amount_sct} STC
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedTx(tx)}
                    className="text-sm text-white bg-blue-600 px-3 py-1 rounded hover:bg-blue-700"
                  >
                    View
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Modal */}
        {/* Modal */}
        <Dialog
          open={!!selectedTx}
          onClose={() => setSelectedTx(null)}
          className="relative z-50"
        >
          <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
          <div className="fixed inset-0 flex items-center justify-center p-4">
            <Dialog.Panel className="bg-white rounded-lg p-6 max-w-md w-full shadow-xl">
              <Dialog.Title className="text-lg font-bold mb-4">
                Transaction Details
              </Dialog.Title>
              <ul className="space-y-2 text-sm text-gray-700">
                <li>
                  <strong>Date:</strong>{' '}
                  {new Date(selectedTx?.date).toLocaleString()}
                </li>
                <li>
                  <strong>Amount (SCT):</strong> {selectedTx?.amount_sct}
                </li>
                <li>
                  <strong>Status:</strong> {selectedTx?.status || 'Confirmed'}
                </li>

                {/* STRK Used or Ksh */}
                {selectedTx?.payment_method === 'STRK' ? (
                  <li>
                    <strong>STRK Used:</strong> {selectedTx?.strk_used}
                  </li>
                ) : (
                  <li>
                    <strong>Ksh:</strong> {selectedTx?.strk_used}
                  </li>
                )}

                <li>
                  <strong>SCT Tx Hash:</strong>{' '}
                  <a
                    href={`https://sepolia.starkscan.co/tx/${selectedTx?.sct_tx_hash}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 underline break-all"
                  >
                    {selectedTx?.sct_tx_hash}
                  </a>
                </li>

                {/* Payment Tx with slicing */}
                <li>
                  <strong>Payment Tx:</strong>{' '}
                  {selectedTx?.payment_method === 'STRK' ? (
                    <a
                      href={`https://sepolia.starkscan.co/tx/${selectedTx?.payment_tx_id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-green-600 underline break-all"
                    >
                      {selectedTx?.payment_tx_id.slice(0, 6)}...
                      {selectedTx?.payment_tx_id.slice(-4)}
                    </a>
                  ) : (
                    <span className="break-all">
                      {selectedTx?.payment_tx_id.slice(0, 6)}...
                      {selectedTx?.payment_tx_id.slice(-4)}
                    </span>
                  )}
                </li>

                <li>
                  <strong>Payment Method:</strong> {selectedTx?.payment_method}
                </li>
              </ul>
              <button
                onClick={() => setSelectedTx(null)}
                className="mt-6 w-full text-white bg-gray-800 hover:bg-gray-900 px-4 py-2 rounded"
              >
                Close
              </button>
            </Dialog.Panel>
          </div>
        </Dialog>
      </div>
    </div>
  );
};

export default Purchase;
