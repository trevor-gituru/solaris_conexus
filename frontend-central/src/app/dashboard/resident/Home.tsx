// src/app/dashboard/resident/Home.tsx
'use client';

import React, { useEffect, useState } from 'react';
import Sidebar from '@/components/Sidebar';
import { useToast } from '@/components/providers/ToastProvider';
import useAuth from '@/hooks/useAuth';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

const Home = () => {
  useAuth();
  const { showToast } = useToast();

  const [userData, setUserData] = useState({
    nos_devices: 0,
    sct_balance: 0,
    strk_balance: 0,
  });

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUserDetails = async () => {
      const token = localStorage.getItem('token'); // Get JWT token from localStorage

      try {
        const res = await fetch(`${API_URL}/residents/user_profile/details`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': token ? `Bearer ${token}` : '', // Add JWT token here if exists
          },
        });
	
	const result = await res.json();
	
        if (!result.success) {
		showToast(result.detail || 'Error fetching user details', 'error');
	} else {
	        setUserData(result.data);
	}
      } catch (error) {
        showToast(error?.message || 'Unkonwn error occurred', 'error');
      } finally {
        setLoading(false);
      }
    };

    fetchUserDetails();
  }, []);

  return (
    <div className="flex">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Dashboard Content */}
      <div className="flex-1 p-6 transition-all duration-300 lg:ml-64 mt-16 lg:mt-0 ml-4 lg:ml-80">
        <h1 className="text-3xl font-bold text-gray-800">Resident Dashboard</h1>
        <p className="mt-4 text-gray-600">Welcome to your resident dashboard!</p>

        {/* Card Section */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
          {/* My Devices Card */}
          <div className="bg-white p-6 rounded-lg shadow-xl">
            <h2 className="text-xl font-semibold text-gray-700">My Devices</h2>
            <p className="mt-2 text-2xl font-bold text-gray-900">
              {loading ? 'Loading...' : `${userData.nos_devices} Devices`}
            </p>
          </div>

          {/* SCT Balance Card */}
          <div className="bg-white p-6 rounded-lg shadow-xl">
            <h2 className="text-xl font-semibold text-gray-700">SCT Balance</h2>
            <p className="mt-2 text-2xl font-bold text-gray-900">
              {loading ? 'Loading...' : `${userData.sct_balance} SCT`}
            </p>
          </div>

          {/* STRK Balance Card */}
          <div className="bg-white p-6 rounded-lg shadow-xl">
            <h2 className="text-xl font-semibold text-gray-700">STRK Balance</h2>
            <p className="mt-2 text-2xl font-bold text-gray-900">
              {loading ? 'Loading...' : `${userData.strk_balance} STRK`}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
