// src/app/dashboard/resident/profile/ProfileDecide.tsx

"use client"

import { useEffect, useState } from 'react';
import Profile from './Profile';
import ProfileShow from './ProfileShow';
import useAuth from '@/hooks/useAuth';
import { useToast } from '@/components/providers/ToastProvider';

interface ProfileData {
  first_name: string;
  last_name: string;
  dob: string;
  gender: string;
  phone: string;
  account_address: string | null;
}

const ProfileDecide = () => {
  useAuth();
  const { showToast } = useToast();
  const [profileData, setProfileData] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const API_URL = process.env.NEXT_PUBLIC_API_URL; // Backend URL

  useEffect(() => {
    const fetchProfileData = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_URL}/residents/user_profile/get`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            ...(token && { Authorization: `Bearer ${token}` }),
          },
        });

        const result = await response.json();

        if (!result.success) {
          showToast(result.detail || 'Error fetching user profile', 'error');
        } else {
          setProfileData(result.data);
	  // ✅ Save account_address to localStorage
          if (result.data.account_address) {
            localStorage.setItem('account_address', result.data.account_address);
          } else {
            localStorage.removeItem('account_address');
          }
        }
      } catch (error: unknown) {
        showToast(
          typeof error === 'object' && error !== null && 'message' in error
            ? (error as Error).message
            : 'Unknown error occurred',
          'error'
        );
      } finally {
        setLoading(false);
      }
    };

    fetchProfileData();
  }, []);

  if (loading) return <div>Loading...</div>;

  return profileData && profileData.first_name
    ? <ProfileShow profileData={profileData} />
    : <Profile />;
};

export default ProfileDecide;
