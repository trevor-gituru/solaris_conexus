'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginForm() {
  const router = useRouter();

  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error' | ''>('');
  const [showMessage, setShowMessage] = useState(false);
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
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData),
        });

        const result = await res.json();

        if (!res.ok) {
          setMessageType('error');
          setMessage(result.message || 'Invalid credentials');
          setShowMessage(true);
        } else {
          // Store the JWT token in localStorage
          localStorage.setItem('token', result.access_token);
          setMessageType('success');
          setMessage('Login successful! Redirecting...');
          setShowMessage(true);
          setTimeout(() => router.push('/dashboard/resident'), 2000);
        }
      } catch (err) {
        setMessageType('error');
        console.error('Login error:', err);
        setMessage('Server error. Please try again.');
        setShowMessage(true);
      }
    }
  };

  useEffect(() => {
    if (showMessage) {
      const timer = setTimeout(() => setShowMessage(false), 3000);
      return () => clearTimeout(timer);
    }
  }, [showMessage]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-xl shadow-md w-full max-w-md space-y-4">
        <h2 className="text-2xl font-bold text-center">Login</h2>

        {showMessage && (
          <div className={`text-center p-2 rounded ${messageType === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
            {message}
            <div className={`h-1 ${messageType === 'success' ? 'bg-green-500' : 'bg-red-500'} animate-[shrink_3s_linear_forwards]`} />
          </div>
        )}

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

        <div className="text-center">
          <button
            type="button"
            onClick={() => router.push('/auth/register')}
            className="text-sm text-blue-600 hover:underline mt-2"
          >
            Don&apos;t have an account? Register
          </button>
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