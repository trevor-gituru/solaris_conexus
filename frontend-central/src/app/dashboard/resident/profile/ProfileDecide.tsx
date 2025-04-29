// app/profile/profileDecide.tsx
"use client"

import { useEffect, useState } from 'react';
import Profile from './Profile';
import ProfileShow from './ProfileShow';
import useAuth from '../../../../hooks/useAuth';

interface ProfileData {
  id: number;
  first_name: string;
  last_name: string;
  dob: string;
  gender: string;
  phone: string;
  wallet_address: string | null; // <-- Add this
}

const ProfileDecide = () => {
  useAuth();
  const [profileData, setProfileData] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL ; // Backend URL

  useEffect(() => {
    const fetchProfileData = async () => {
      try {
        const response = await fetch(`${API_URL}/get_profile`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch profile data');
        }

        const data = await response.json();
        setProfileData(data); // Set profile data in state
      } catch (error: unknown) {
        if (error instanceof Error) {
          setError(error.message); // Set error message if fetch fails
        } else {
          setError('An unexpected error occurred'); // Fallback error message
        }
      } finally {
        setLoading(false); // Set loading to false after request completes
      }
    };

    fetchProfileData();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return profileData ? <ProfileShow profileData={profileData} /> : <Profile />;
};

export default ProfileDecide;