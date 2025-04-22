'use client';

import { useState } from 'react';

export default function RegisterForm() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [showPassword, setShowPassword] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

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
        const res = await fetch('/api/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData),
        });

        const result = await res.json();

        if (!res.ok) {
          setErrors({ api: result.message || 'Something went wrong' });
        } else {
          setSuccessMessage('Registration successful!');
          setFormData({ username: '', email: '', password: '', confirmPassword: '' });
        }
      } catch (err) {
        setErrors({ api: 'Server error. Please try again later.' });
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-xl shadow-md w-full max-w-md space-y-4">
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
          <label htmlFor="showPassword" className="text-sm">Show Passwords</label>
        </div>

        {/* Error / Success Messages */}
        {errors.api && <p className="text-red-600 text-sm text-center">{errors.api}</p>}
        {successMessage && <p className="text-green-600 text-sm text-center">{successMessage}</p>}

        <button
          type="submit"
          className="w-full bg-yellow-500 hover:bg-yellow-600 text-white font-semibold py-2 rounded"
        >
          Register
        </button>
      </form>
    </div>
  );
}
