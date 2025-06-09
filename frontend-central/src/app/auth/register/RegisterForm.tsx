// app/auth/register/RegisterForm.tsx
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useToast } from '@/components/providers/ToastProvider';
import { useGoogleLogin, CredentialResponse } from '@react-oauth/google';
import { FcGoogle } from 'react-icons/fc';

export default function RegisterForm() {
  const router = useRouter();
  const { showToast } = useToast();

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [showPassword, setShowPassword] = useState(false);
 const [googleUserInfo, setGoogleUserInfo] = useState<null | { email: string, sub: string }>(null);

  const [isGoogleRegistering, setIsGoogleRegistering] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const validate = () => {
    const newErrors: { [key: string]: string } = {};

    if (!/^[a-zA-Z0-9_]{3,}$/.test(formData.username)) {
      newErrors.username =
        'Username must be at least 3 characters and contain only letters, numbers, or underscores.';
    }

    if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Enter a valid email.';
    }

    if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters.';
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match.';
    }

    return newErrors;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const validationErrors = validate();
    setErrors(validationErrors);

    if (Object.keys(validationErrors).length === 0) {
      try {
        const { username, email, password } = formData;
        const payload = { username, email, password };

        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/auth/register`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
          }
        );

        const result = await res.json();

        if (!res.ok) {
          // 🔥 showToast for server-side error
          showToast(result.detail || 'Something went wrong', 'error');
        } else {
          // ✅ showToast for successful registration
          showToast('Registration successful! Redirecting...', 'success');
          setFormData({
            username: '',
            email: '',
            password: '',
            confirmPassword: '',
          });

          setTimeout(() => {
            router.push('/auth/login');
          }, 4000);
        }
      } catch (err: any) {
        // 🌐 showToast for network error
        showToast(
          err?.message || 'Network error. Please try again later.',
          'error'
        );
      }
    }
  };

  const handleGoogleRegister = () => {
    if (!/^[a-zA-Z0-9_]{3,}$/.test(formData.username)) {
      showToast(
        'Username must be at least 3 characters and contain only letters, numbers, or underscores.',
        'error'
      );
      return;
    }

    googleRegister(); // triggers the login flow
  };

const googleRegister = useGoogleLogin({
  onSuccess: async (tokenResponse) => {
    try {
      const res = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
        headers: {
          Authorization: `Bearer ${tokenResponse.access_token}`,
        },
      });
      const data = await res.json();

      // Update formData with Google data
      setFormData((prev) => ({
        ...prev,
        email: data.email,
        password: data.sub,
        confirmPassword: data.sub,
      }));

      setGoogleUserInfo({ email: data.email, sub: data.sub });
    } catch (err) {
      showToast('Failed to fetch user info', 'error');
    }
  },
  onError: () => showToast('Google login failed', 'error'),
});

useEffect(() => {
  if (googleUserInfo) {
    // Set formData and delay submit until formData updates
    const newFormData = {
      username: formData.username,
      email: googleUserInfo.email,
      password: googleUserInfo.sub,
      confirmPassword: googleUserInfo.sub,
    };

    setFormData(newFormData);

    // Delay calling submit to allow state to propagate
    setTimeout(() => {
      handleSubmit({ preventDefault: () => {} } as React.FormEvent);
    }, 100); // 100ms is enough for state update

    // Reset googleUserInfo
    setGoogleUserInfo(null);
  }
}, [googleUserInfo]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 px-4">
      <form
        onSubmit={handleSubmit}
        className="bg-white p-6 rounded-xl shadow-md w-full max-w-md space-y-4 mt-20"
      >
        <h2 className="text-2xl font-bold text-center">Register</h2>

        {/* Username */}
        <div>
          <label className="block mb-1 text-sm font-semibold">Username</label>
          <input
            name="username"
            value={formData.username}
            onChange={handleChange}
            className="w-full border border-gray-300 px-3 py-2 rounded"
            placeholder="Your username"
          />
          {errors.username && (
            <p className="text-red-600 text-sm mt-1">{errors.username}</p>
          )}
        </div>

        {/* Email */}
        <div>
          <label className="block mb-1 text-sm font-semibold">Email</label>
          <input
            name="email"
            value={formData.email}
            onChange={handleChange}
            className="w-full border border-gray-300 px-3 py-2 rounded"
            placeholder="you@example.com"
          />
          {errors.email && (
            <p className="text-red-600 text-sm mt-1">{errors.email}</p>
          )}
        </div>

        {/* Password */}
        <div>
          <label className="block mb-1 text-sm font-semibold">Password</label>
          <input
            name="password"
            type={showPassword ? 'text' : 'password'}
            value={formData.password}
            onChange={handleChange}
            className="w-full border border-gray-300 px-3 py-2 rounded"
            placeholder="••••••••"
          />
          {errors.password && (
            <p className="text-red-600 text-sm mt-1">{errors.password}</p>
          )}
        </div>

        {/* Confirm Password */}
        <div>
          <label className="block mb-1 text-sm font-semibold">
            Confirm Password
          </label>
          <input
            name="confirmPassword"
            type={showPassword ? 'text' : 'password'}
            value={formData.confirmPassword}
            onChange={handleChange}
            className="w-full border border-gray-300 px-3 py-2 rounded"
            placeholder="••••••••"
          />
          {errors.confirmPassword && (
            <p className="text-red-600 text-sm mt-1">
              {errors.confirmPassword}
            </p>
          )}
        </div>

        {/* Show Password */}
        <div className="flex items-center">
          <input
            type="checkbox"
            id="showPassword"
            className="mr-2"
            checked={showPassword}
            onChange={() => setShowPassword(!showPassword)}
          />
          <label htmlFor="showPassword" className="text-sm">
            Show Passwords
          </label>
        </div>

        <button
          type="submit"
          className="w-full bg-yellow-500 hover:bg-yellow-600 text-white font-semibold py-2 rounded"
        >
          Register
        </button>

        <p className="text-center text-sm mt-4">
          Already have an account?{' '}
          <button
            type="button"
            onClick={() => router.push('/auth/login')}
            className="text-yellow-600 font-semibold hover:underline"
          >
            Login
          </button>
        </p>
        <div className="relative my-4">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="bg-white px-2 text-gray-500">or</span>
          </div>
        </div>

        <button
          onClick={() => {
            handleGoogleRegister();
          }}
          className="flex items-center justify-center gap-2 bg-white border border-gray-300 hover:bg-gray-100 text-black font-medium py-2 px-4 rounded w-full"
          disabled={isLoading}
          type="button"
        >
          <FcGoogle size={20} />
          {isLoading ? 'Loading....' : 'Sign up with Google'}
        </button>
      </form>
    </div>
  );
}
