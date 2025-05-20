'use client';

import React, { useState } from 'react';
import { 
  HomeIcon, DevicePhoneMobileIcon, ArchiveBoxIcon, 
  CogIcon, CreditCardIcon, ArrowRightOnRectangleIcon,
  Bars3Icon, XMarkIcon 
} from '@heroicons/react/24/outline';
import Link from 'next/link';
import { useRouter } from 'next/navigation'; // For page redirection after logout

const Sidebar = () => {
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const router = useRouter();

  const toggleMobileSidebar = () => {
    setIsMobileOpen(!isMobileOpen);
  };

  const handleLogout = () => {
    // Remove the JWT token from localStorage
    localStorage.removeItem('token');
    // Redirect to the home page
    router.push('/'); // Redirect to home page after logout
  };

  return (
    <>
      {/* Sidebar for large screens */}
      <div className="hidden lg:block w-64 h-screen fixed bg-gray-800 text-white p-5">
        <div className="flex flex-col space-y-4">
          <Link href="/dashboard/resident" className="flex items-center space-x-2 hover:bg-gray-700 p-2 rounded-md">
            <HomeIcon className="h-6 w-6" />
            <span>Home</span>
          </Link>
          <Link href="/dashboard/resident/devices" className="flex items-center space-x-2 hover:bg-gray-700 p-2 rounded-md">
            <DevicePhoneMobileIcon className="h-6 w-6" />
            <span>My Devices</span>
          </Link>
          <Link href="/dashboard/resident/trade" className="flex items-center space-x-2 hover:bg-gray-700 p-2 rounded-md">
            <ArchiveBoxIcon className="h-6 w-6" />
            <span>Trade Tokens</span>
          </Link>
          
          <Link href="/dashboard/resident/buy-tokens" className="flex items-center space-x-2 hover:bg-gray-700 p-2 rounded-md">
            <CreditCardIcon className="h-6 w-6" />
            <span>Purchase Tokens</span>
          </Link>
          <Link href="/dashboard/resident/profile" className="flex items-center space-x-2 hover:bg-gray-700 p-2 rounded-md">
            <CogIcon className="h-6 w-6" />
            <span>Profile Settings</span>
          </Link>
          <button
            onClick={handleLogout}
            className="flex items-center space-x-2 hover:bg-gray-700 p-2 rounded-md"
          >
            <ArrowRightOnRectangleIcon className="h-6 w-6" />
            <span>Logout</span>
          </button>
        </div>
      </div>

      {/* Mobile Sidebar */}
      <div
        className={`lg:hidden fixed top-0 left-0 w-64 h-full bg-gray-800 text-white p-5 transform ${isMobileOpen ? 'translate-x-0' : '-translate-x-full'} transition-transform duration-300 ease-in-out z-40`}
      >
        {/* Close Button inside sidebar */}
        <div className="flex justify-end mb-6">
          <button
            className="text-white bg-gray-700 hover:bg-gray-600 p-2 rounded-md"
            onClick={toggleMobileSidebar}
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        {/* Sidebar links */}
        <div className="flex flex-col space-y-4">
          <Link href="/dashboard/resident" className="flex items-center space-x-2 hover:bg-gray-700 p-2 rounded-md">
            <HomeIcon className="h-6 w-6" />
            <span>Home</span>
          </Link>
          <Link href="/dashboard/resident/devices" className="flex items-center space-x-2 hover:bg-gray-700 p-2 rounded-md">
            <DevicePhoneMobileIcon className="h-6 w-6" />
            <span>My Devices</span>
          </Link>
          <Link href="/dashboard/resident/trade" className="flex items-center space-x-2 hover:bg-gray-700 p-2 rounded-md">
            <ArchiveBoxIcon className="h-6 w-6" />
            <span>Trade Tokens</span>
          </Link>
          <Link href="/dashboard/resident/buy-tokens" className="flex items-center space-x-2 hover:bg-gray-700 p-2 rounded-md">
            <CreditCardIcon className="h-6 w-6" />
            <span>Purchase Tokens</span>
          </Link>
          <Link href="/dashboard/resident/profile" className="flex items-center space-x-2 hover:bg-gray-700 p-2 rounded-md">
            <CogIcon className="h-6 w-6" />
            <span>Profile Settings</span>
          </Link>
          {/* Mobile Logout Button */}
          <button
            onClick={handleLogout}
            className="flex items-center space-x-2 hover:bg-gray-700 p-2 rounded-md"
          >
            <ArrowRightOnRectangleIcon className="h-6 w-6" />
            <span>Logout</span>
          </button>
        </div>
      </div>

      {/* Mobile Toggle Button (Menu) */}
      {!isMobileOpen && (
        <button
          className="lg:hidden fixed top-4 left-4 text-white z-50 p-2 bg-gray-700 rounded-md"
          onClick={toggleMobileSidebar}
        >
          <Bars3Icon className="h-6 w-6" />
        </button>
      )}
    </>
  );
};

export default Sidebar;
