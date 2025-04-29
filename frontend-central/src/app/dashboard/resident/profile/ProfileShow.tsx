'use client';

import React from 'react';
import Head from 'next/head';
import Sidebar from '../../../../components/Sidebar';
import { UserIcon, ClipboardIcon } from '@heroicons/react/24/outline'; // Import ClipboardIcon

interface ProfileShowProps {
  profileData: {
    id: number;
    first_name: string;
    last_name: string;
    dob: string;
    gender: string;
    phone: string;
    wallet_address: string | null;
  };
}

const ProfileShow: React.FC<ProfileShowProps> = ({ profileData }) => {
  const formatGender = (gender: string) => {
    if (gender === 'male') return 'Male';
    if (gender === 'female') return 'Female';
    return 'Not Specified';
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      alert('Wallet address copied!');
    } catch (err) {
      console.error('Failed to copy!', err);
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <Head>
        <title>{profileData.first_name} {profileData.last_name} - Profile</title>
      </Head>

      <Sidebar />

      <div className="flex-1 p-6 lg:ml-64 mt-16 lg:mt-0">
        <div className="max-w-3xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl p-8 space-y-6">
            <div className="flex items-center space-x-6">
              <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center text-white text-xl">
                <UserIcon className="h-8 w-8" />
              </div>
              <div>
                <h1 className="text-3xl font-semibold text-gray-800">{profileData.first_name} {profileData.last_name}</h1>
                <p className="text-sm text-gray-600">{formatGender(profileData.gender)}</p>
              </div>
            </div>

            {/* Profile Info Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
              <div>
                <p className="font-medium text-gray-700">Date of Birth</p>
                <p className="text-gray-500">{profileData.dob}</p>
              </div>
              <div>
                <p className="font-medium text-gray-700">Phone Number</p>
                <p className="text-gray-500">{profileData.phone}</p>
              </div>

              {/* Wallet Address Section */}
              <div className="sm:col-span-2">
                <p className="font-medium text-gray-700">Wallet Address</p>
                <div className="flex items-center space-x-2 overflow-x-auto bg-gray-100 p-2 rounded-md">
                  <p className="text-gray-500 break-all text-sm">
                    {profileData.wallet_address ? profileData.wallet_address : 'No wallet assigned yet'}
                  </p>
                  {profileData.wallet_address && (
                    <button
                      onClick={() => copyToClipboard(profileData.wallet_address!)}
                      className="text-gray-400 hover:text-gray-600"
                      title="Copy wallet address"
                    >
                      <ClipboardIcon className="h-5 w-5" />
                    </button>
                  )}
                </div>
              </div>

            </div>

          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileShow;