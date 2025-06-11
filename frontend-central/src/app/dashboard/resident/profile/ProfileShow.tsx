// src/app/dashboard/resident/profile/ProfileShow.tsx
'use client';

import React from 'react';
import Head from 'next/head';
import ProfileUpdate from './ProfileUpdate';
import Sidebar from '@/components/Sidebar';
import { UserIcon, ClipboardIcon } from '@heroicons/react/24/outline'; // Import ClipboardIcon

interface ProfileShowProps {
  profileData: {
    first_name: string;
    last_name: string;
    dob: string;
    gender: string;
    phone: string;
    phone2: string;
    notification: string;
    account_address: string | null;
  };
}

const ProfileShow: React.FC<ProfileShowProps> = ({
  profileData: initialData,
}) => {
  const [profileData, setProfileData] = React.useState(initialData);
  const formatGender = (gender: string) => {
    if (gender === 'Male') return 'Male';
    if (gender === 'Female') return 'Female';
    return 'Not Specified';
  };
  const formatNotification = (notification: string) => {
    if (notification === 'sms') return 'SMS';
    if (notification  === 'email') return 'Email';
    return 'None';
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
        <title>
          {profileData.first_name} {profileData.last_name} - Profile
        </title>
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
                <h1 className="text-3xl font-semibold text-gray-800">
                  {profileData.first_name} {profileData.last_name}
                </h1>
                <p className="text-sm text-gray-600">
                  {formatGender(profileData.gender)}
                </p>
              </div>
            </div>

            {/* Profile Info Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
              <div>
                <p className="font-medium text-gray-700">Date of Birth</p>
                <p className="text-gray-500">{profileData.dob}</p>
              </div>
              <div>
                <p className="font-medium text-gray-700">Mpesa Number</p>
                <p className="text-gray-500">{profileData.phone}</p>
              </div>
              <div>
                <p className="font-medium text-gray-700">Notification Type</p>
                <p className="text-gray-500">
                  {formatNotification(profileData.notification)}
                </p>
              </div>
              <div>
                <p className="font-medium text-gray-700">Notification Number</p>
                <p className="text-gray-500">{profileData.phone2 || 'None'}</p>
              </div>

              {/* Wallet Address Section */}
              <div className="sm:col-span-2">
                <p className="font-medium text-gray-700">Wallet Address</p>
                <div className="flex items-center space-x-2 overflow-x-auto bg-gray-100 p-2 rounded-md">
                  <p className="text-gray-500 break-all text-sm">
                    {profileData.account_address
                      ? profileData.account_address
                      : 'No wallet assigned yet'}
                  </p>
                  {profileData.account_address && (
                    <button
                      onClick={() =>
                        copyToClipboard(profileData.account_address!)
                      }
                      className="text-gray-400 hover:text-gray-600"
                      title="Copy wallet address"
                    >
                      <ClipboardIcon className="h-5 w-5" />
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* INSERT UPDATE BUTTON MODAL HERE */}
            <div className="pt-4 text-right">
              <ProfileUpdate
                profileData={profileData}
                onProfileUpdate={setProfileData}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileShow;
