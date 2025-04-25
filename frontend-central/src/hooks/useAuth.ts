// src/hooks/useAuth.ts
'use client';

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

const useAuth = () => {
  const router = useRouter();

  useEffect(() => {
    const token =
      typeof window !== 'undefined'
        ? localStorage.getItem('token') || sessionStorage.getItem('token')
        : null;

    if (!token) {
      router.push('/auth/login');
    } else {
      const decodedToken = decodeJwt(token);
      if (!decodedToken || decodedToken.exp * 1000 < Date.now()) {
        router.push('/auth/login');
      }
    }
  }, [router]);
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