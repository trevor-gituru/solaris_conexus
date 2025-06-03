// src/app/dashboard/resident/profile/ProfileUpate.tsx
'use client';

import React, { useState } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import ConnectWallet from '@/components/ConnectWallet'; // Adjust the path as needed
import { useToast } from '@/components/providers/ToastProvider';

const ProfileUpdate = ({
  profileData,
  onProfileUpdate
}: {
  profileData: any;
  onProfileUpdate: (updated: any) => void;
}) => {
  const { showToast } = useToast();
  const API_URL = process.env.NEXT_PUBLIC_API_URL ; // Backend URL
  const [showModal, setShowModal] = useState(false);
  const [phone, setPhone] = useState(profileData.phone || '');
  const [accountAddress, setAccountAddress] = useState(profileData.account_address || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

const validateInputs = () => {
  if (!phone.match(/^\+?[0-9]{10}$/)) {
    setError('Invalid phone number format.');
    return false;
  }
  if (accountAddress && !/^0x[a-fA-F0-9]{60,64}$/.test(accountAddress)) {
    setError('Invalid wallet address format (must be 60-64 hex characters after 0x).');
    return false;
  }
  setError('');
  return true;
};


const handleSave = async () => {
  if (!validateInputs()) return;

  setLoading(true);
  setError('');

  try {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_URL}/residents/user_profile/update`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        phone,
        account_address: accountAddress || null,
      }),
    });

    const data = await response.json();

    if (!response.ok || data.success !== true) {
      throw new Error(data?.detail || data?.message || 'Failed to update profile');
    }

    // Use request values to update local state
    setPhone(phone);
    setAccountAddress(accountAddress);

    showToast('Profile updated successfully.', 'success');
    onProfileUpdate({
  ...profileData,
  phone,
  account_address: accountAddress || '',
});
    setShowModal(false);
  } catch (err: any) {
    console.error('Update failed:', err);
    showToast(err.message || 'Something went wrong.', 'error');
  } finally {
    setLoading(false);
  }
};

  return (
    <>
      <button
        onClick={() => setShowModal(true)}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Edit Profile
      </button>

      {showModal && (
        <div className="fixed inset-0 bg-white/60 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-xl p-6 w-full max-w-md relative">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Update Profile</h2>

            {error && <p className="text-red-600 mb-2">{error}</p>}

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700">Phone Number</label>
              <input
                type="text"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200"
              />
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700">Wallet Address</label>
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  value={accountAddress}
                  onChange={(e) => setAccountAddress(e.target.value)}
                  className="flex-1 mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200"
                />
                {accountAddress && (
                  <button
                    onClick={() => setAccountAddress('')}
                    className="text-gray-400 hover:text-red-600"
                    title="Clear wallet address"
                  >
                    <XMarkIcon className="h-5 w-5" />
                  </button>
                )}
              </div>
            </div>

            {/* Connect Wallet Button */}
            <div className="mt-6">
              <ConnectWallet />
            </div>

            {/* Save / Cancel Row */}
            <div className="mt-4 flex justify-end space-x-2">
              <button
                onClick={() => setShowModal(false)}
                className="bg-red-500 text-white py-2 px-4 rounded"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded"
                disabled={loading}
              >
                {loading ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ProfileUpdate;
