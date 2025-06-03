'use client';

import { useState } from 'react';
import Sidebar from '@/components/Sidebar'; // Adjust path if needed
import TradeMy from './TradeMy';
import TradeAvailable from './TradeAvailable';

export default function TradeDecide() {
  const [activeTab, setActiveTab] = useState<'my' | 'available'>('my');

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <Sidebar />

      {/* Main content */}
      <div className="flex-1 p-6 transition-all duration-300 lg:ml-64 mt-16 lg:mt-0 ml-4 ">
        {/* Tabs */}
        <div className="flex space-x-4 border-b pb-4 mb-6">
          <button
            onClick={() => setActiveTab('my')}
            className={`px-6 py-2 rounded-t-lg font-semibold ${
              activeTab === 'my' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'
            }`}
          >
            My Trades
          </button>
          <button
            onClick={() => setActiveTab('available')}
            className={`px-6 py-2 rounded-t-lg font-semibold ${
              activeTab === 'available' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'
            }`}
          >
            Available Trades
          </button>
        </div>

        {/* Tab content */}
        <div>
          {activeTab === 'my' ? <TradeMy /> : <TradeAvailable />}
        </div>
      </div>
    </div>
  );
}

