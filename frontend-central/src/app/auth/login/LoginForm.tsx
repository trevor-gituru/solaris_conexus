// app/auth/register/LoginForm.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useToast } from '@/components/providers/ToastProvider';
import { GoogleLogin, CredentialResponse } from '@react-oauth/google';

export default function LoginForm() {
  const router = useRouter();
  const { showToast } = useToast();

  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [showPassword, setShowPassword] = useState(false); // state for showing password

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const validate = () => {
    const newErrors: { [key: string]: string } = {};

    if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Enter a valid email.';
    }

    if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters.';
    }

    return newErrors;
  };

const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  const validationErrors = validate();
  setErrors(validationErrors);

  if (Object.keys(validationErrors).length === 0) {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      const result = await res.json();

      if (!res.ok) {
        showToast(result.detail || 'Invalid credentials', 'error');
      } else {
        localStorage.setItem('token', result.access_token);
        showToast('Login successful! Redirecting...', 'success');
        setTimeout(() => router.push('/dashboard/resident/profile'), 4000);
      }
    } catch (err: any) {
      showToast(err?.message || 'Server error. Please try again.', 'error');
    }
  }
};

const handleGoogleSuccess = async (credentialResponse: CredentialResponse) => {
  function parseJwt (token: string) {
  const base64Url = token.split('.')[1];
  const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
  const jsonPayload = decodeURIComponent(
    atob(base64)
      .split('')
      .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
      .join('')
  );

  return JSON.parse(jsonPayload);
}

if (credentialResponse.credential) {
  try {
    const decoded = parseJwt(credentialResponse.credential);
    console.log(JSON.stringify(decoded, null, 2), 'info');
    // send token to backend ...
  
      const result = await res.json();

      if (!res.ok) {
        showToast(result.detail || 'Google login failed', 'error');
      } else {
        localStorage.setItem('token', result.access_token);
        showToast('Google login successful! Redirecting...', 'success');
        setTimeout(() => router.push('/dashboard/resident/profile'), 3000);
      }
    } catch (err: any) {
      showToast(err?.message || 'Server error. Please try again.', 'error');
    }
  } else {
    showToast('Google credential not found.', 'error');
  }
};

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-xl shadow-md w-full max-w-md space-y-4">
        <h2 className="text-2xl font-bold text-center">Login</h2>

        <div>
          <label className="block mb-1 text-sm font-semibold">Email</label>
          <input
            name="email"
            value={formData.email}
            onChange={handleChange}
            className="w-full border border-gray-300 px-3 py-2 rounded"
            placeholder="you@example.com"
          />
          {errors.email && <p className="text-red-600 text-sm mt-1">{errors.email}</p>}
        </div>

        <div className="relative">
          <label className="block mb-1 text-sm font-semibold">Password</label>
          <input
            name="password"
            type={showPassword ? 'text' : 'password'} // toggle password visibility
            value={formData.password}
            onChange={handleChange}
            className="w-full border border-gray-300 px-3 py-2 rounded pr-10"
            placeholder="••••••••"
          />
          <div className="flex items-center mt-2">
            <input
              type="checkbox"
              id="showPassword"
              checked={showPassword}
              onChange={() => setShowPassword(!showPassword)}
              className="mr-2"
            />
            <label htmlFor="showPassword" className="text-sm">Show Password</label>
          </div>
          {errors.password && <p className="text-red-600 text-sm mt-1">{errors.password}</p>}
        </div>

<button
  type="submit"
  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded"
>
  Login
</button>

<div className="text-center mt-2">
  <button
    type="button"
    onClick={() => router.push('/auth/register')}
    className="text-sm text-blue-600 hover:underline"
  >
    Don&apos;t have an account? Register
  </button>
</div>

<div className="relative my-4">
  <div className="absolute inset-0 flex items-center">
    <div className="w-full border-t border-gray-300"></div>
  </div>
  <div className="relative flex justify-center text-sm">
    <span className="bg-white px-2 text-gray-500">or</span>
  </div>
</div>

<div className="flex justify-center">
  <GoogleLogin
    onSuccess={handleGoogleSuccess}
    onError={() => showToast('Google Sign-In failed', 'error')}
  />
</div>
      </form>

      <style jsx>{`
        @keyframes shrink {
          0% {
            width: 100%;
          }
          100% {
            width: 0%;
          }
        }
      `}</style>
    </div>
  );
} 
