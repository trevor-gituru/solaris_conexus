'use client';

import React from 'react';
import Sidebar from '../../../components/Sidebar'; // Adjust path as necessary
import useAuth from '../../../hooks/useAuth'; // Adjust path as necessary

const Home = () => {
  useAuth();
  return (
    <div className="flex">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Dashboard Content */}
      <div className="flex-1 p-6 transition-all duration-300 ml-0 lg:ml-64 lg:pl-0 mt-16 lg:mt-0">
        {/* Content will shift right by 16rem (64px) on mobile */}
        <h1 className="text-3xl font-bold text-gray-800">Resident Dashboard</h1>
        <p className="mt-4 text-gray-600">Welcome to your resident dashboard!</p>
        {/* Add more dashboard-related components here */}
      </div>
    </div>
  );
};

export default Home;