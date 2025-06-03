// src/hooks/useAuth.ts
'use client';

import { useRouter, usePathname } from 'next/navigation';
import { useEffect, useRef } from 'react';
import { useToast } from '@/components/providers/ToastProvider';

const useAuth = () => {
  const router = useRouter();
  const pathname = usePathname();
  const { showToast } = useToast();
  const hasRun = useRef(false); // ✅ prevent multiple redirects

  useEffect(() => {
    if (hasRun.current) return; // prevent infinite redirect
    hasRun.current = true;

    const token =
      typeof window !== 'undefined'
        ? localStorage.getItem('token')
        : null;

    const wallet =
      typeof window !== 'undefined'
        ? localStorage.getItem('account_address') // ✅ spelling fix
        : null;

    if (!token) {
      showToast('Please log in to continue.', 'error');
      router.push('/auth/login');
      return;
    }

    const decodedToken = decodeJwt(token);
    if (!decodedToken || decodedToken.exp * 1000 < Date.now()) {
      showToast('Session has expired. Please log in again.', 'error');
      router.push('/auth/login');
      return;
    }

    if (!wallet && pathname !== '/dashboard/resident/profile') {
      showToast('Please complete your profile first.', 'info');
      router.push('/dashboard/resident/profile');
    }
  }, [router, pathname, showToast]);
};

const decodeJwt = (token: string) => {
  try {
    const [, payload] = token.split('.');
    return JSON.parse(atob(payload));
  } catch {
    return null;
  }
};

export default useAuth;
