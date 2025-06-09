'use client';

import { useState } from 'react';
import Sidebar from '@/components/Sidebar';
import TradeMy from './TradeMy';
import TradeAvailable from './TradeAvailable';

export default function TradeDecide() {
  const [activeTab, setActiveTab] = useState<'my' | 'available'>('my');

  return (
    <div className="flex min-h-screen flex-col lg:flex-row">
      {/* Sidebar */}
      <Sidebar />

      {/* Main content */}
      <main className="flex-1 p-4 pt-20 lg:pt-6 lg:ml-64 w-full max-w-full overflow-x-hidden">
        {/* Tabs */}
        <div className="flex flex-col sm:flex-row sm:space-x-4 space-y-2 sm:space-y-0 border-b pb-4 mb-6">
          <button
            onClick={() => setActiveTab('my')}
            className={`px-4 py-2 rounded font-semibold ${
              activeTab === 'my'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            My Trades
          </button>
          <button
            onClick={() => setActiveTab('available')}
            className={`px-4 py-2 rounded font-semibold ${
              activeTab === 'available'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            Available Trades
          </button>
        </div>

        {/* Tab content */}
        <div>{activeTab === 'my' ? <TradeMy /> : <TradeAvailable />}</div>
      </main>
    </div>
  );
}
