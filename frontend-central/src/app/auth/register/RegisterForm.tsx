'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation'; // ✅ for App Router

export default function RegisterForm() {
  const router = useRouter();

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [showPassword, setShowPassword] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [showToast, setShowToast] = useState(false);

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

        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });

        const result = await res.json();

        if (!res.ok) {
          setErrors({ api: result.message || 'Something went wrong' });
        } else {
          setSuccessMessage('Registration successful! Redirecting...');
          setShowToast(true);
          setFormData({ username: '', email: '', password: '', confirmPassword: '' });

          setTimeout(() => {
            router.push('/auth/login');
          }, 3000);
        }
      } catch (err) {
        console.error('Login error:', err);
        setErrors({ api: 'Server error. Please try again later.' });
      }
    }
  };

  useEffect(() => {
    if (successMessage || errors.api) {
      setShowToast(true);
      const timeout = setTimeout(() => setShowToast(false), 3000);
      return () => clearTimeout(timeout);
    }
  }, [successMessage, errors.api]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 px-4">
      {/* Toast Message */}
      {showToast && (
        <div className="fixed top-5 w-full max-w-md bg-white border-l-4 border-green-500 shadow-lg px-4 py-3 rounded text-green-700 font-medium z-50 animate-slidein">
          <div className="flex items-center justify-between">
            <span>{successMessage || errors.api}</span>
          </div>
          <div className="h-1 bg-green-500 mt-2 animate-progress" />
        </div>
      )}

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
          {errors.username && <p className="text-red-600 text-sm mt-1">{errors.username}</p>}
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
          {errors.email && <p className="text-red-600 text-sm mt-1">{errors.email}</p>}
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
          {errors.password && <p className="text-red-600 text-sm mt-1">{errors.password}</p>}
        </div>

        {/* Confirm Password */}
        <div>
          <label className="block mb-1 text-sm font-semibold">Confirm Password</label>
          <input
            name="confirmPassword"
            type={showPassword ? 'text' : 'password'}
            value={formData.confirmPassword}
            onChange={handleChange}
            className="w-full border border-gray-300 px-3 py-2 rounded"
            placeholder="••••••••"
          />
          {errors.confirmPassword && (
            <p className="text-red-600 text-sm mt-1">{errors.confirmPassword}</p>
          )}
        </div>

        {/* Show Password Toggle */}
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

        {/* Submit Button */}
        <button
          type="submit"
          className="w-full bg-yellow-500 hover:bg-yellow-600 text-white font-semibold py-2 rounded"
        >
          Register
        </button>

        {/* Redirect to Login */}
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
      </form>

      {/* Animation Styles */}
      <style jsx>{`
        .animate-slidein {
          animation: slidein 0.4s ease-out forwards;
        }

        @keyframes slidein {
          from {
            opacity: 0;
            transform: translateY(-20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-progress {
          animation: shrink 3s linear forwards;
        }

        @keyframes shrink {
          from {
            width: 100%;
          }
          to {
            width: 0%;
          }
        }
      `}</style>
    </div>
  );
}