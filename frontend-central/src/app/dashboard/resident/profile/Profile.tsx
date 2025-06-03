// src/app/dashboard/resident/profile/Profile.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import Sidebar from '@/components/Sidebar';
import ConnectWallet from '@/components/ConnectWallet';
import useAuth from '@/hooks/useAuth';
import { useToast } from '@/components/providers/ToastProvider';


const Profile = () => {
  useAuth();
  const { showToast } = useToast();

  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    dob: '',
    gender: '',
    phoneNumber: '',
    accountAddress: '',
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [emailConfirmed, setEmailConfirmed] = useState(false);
  const [showEmailConfirmation, setShowEmailConfirmation] = useState(false);
  const [confirmationCode, setConfirmationCode] = useState('');
  const [timer, setTimer] = useState(60);
  const [isResendDisabled, setIsResendDisabled] = useState(false);
  const [storedCode, setStoredCode] = useState(''); // Store the confirmation code

  const API_URL = process.env.NEXT_PUBLIC_API_URL ; // Backend URL
  const token = localStorage.getItem('token'); 

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

const handleEmailConfirmation = async () => {
  setShowEmailConfirmation(true);
  setTimer(60);
  setIsResendDisabled(true);


  try {
    // Send request to get the confirmation code
    const response = await fetch(`${API_URL}/residents/user_profile/confirm_email`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`, // Add JWT token here
      },
    });

    const data = await response.json();

    if (response.ok) {
      // Assuming the confirmation code is in `data.code`
      setStoredCode(data.data.code); // Store the confirmation code received from the backend
    } else {
      // If response is not ok, handle error
      showToast(`Error confirming email: ${data.detail}`, 'error');
    }
  } catch (error: unknown) {
    // Catch network or unexpected errors
    if (error instanceof Error) {
      // If the error is an instance of Error, access the message property
      showToast(`An unexpected error occurred: ${error.message}`, 'error');
    } else {
      // If the error is not an instance of Error, handle it as a generic unknown error
      showToast('An unexpected error occurred.', 'error');
    }
  }
};

  const handleCodeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setConfirmationCode(e.target.value);
  };

  const handleConfirmCode = () => {
    if (confirmationCode === storedCode) {
      setEmailConfirmed(true);
      setShowEmailConfirmation(false);
    } else {
      showToast('Invalid confirmation code', 'error');
    }
  };

  const handleResendCode = async () => {
    setTimer(60);
    setIsResendDisabled(true);

    const response = await fetch(`${API_URL}/residents/user_profile/confirm_email`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`, // Add JWT token here
      },
    });

    const data = await response.json();
    if (data.success) {
      setStoredCode(data.data.code); // Update the stored code after resend
    } else {
      showToast('Error resending code', 'error');
    }
  };

  useEffect(() => {
    if (showEmailConfirmation && isResendDisabled && timer > 0) {
      const interval = setInterval(() => setTimer(prev => prev - 1), 1000);
      return () => clearInterval(interval);
    }
    if (timer === 0) {
      setIsResendDisabled(false);
    }
  }, [timer, showEmailConfirmation, isResendDisabled]);



const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  // Validation logic
  const errors: Record<string, string> = {};
  const nameRegex = /^[A-Za-z]+$/;
  const phoneRegex = /^\d{10}$/;

  if (!formData.firstName.trim()) {
    errors.firstName = 'First name is required';
  } else if (!nameRegex.test(formData.firstName)) {
    errors.firstName = 'First name must contain only letters';
  }

  if (!formData.lastName.trim()) {
    errors.lastName = 'Last name is required';
  } else if (!nameRegex.test(formData.lastName)) {
    errors.lastName = 'Last name must contain only letters';
  }

  if (!formData.dob) {
    errors.dob = 'Date of birth is required';
  }

  if (!formData.gender) {
    errors.gender = 'Gender is required';
  }

  if (!formData.phoneNumber.trim()) {
    errors.phoneNumber = 'Phone number is required';
  } else if (!phoneRegex.test(formData.phoneNumber)) {
    errors.phoneNumber = 'Phone number must be 10 digits';
  }

  if (!formData.accountAddress.trim()) {
    errors.accountAddress = 'Account address is required';
  }

  if (Object.keys(errors).length > 0) {
    setFormErrors(errors);
    return;
  }

  setFormErrors({}); // Clear errors if valid

  // Construct and send data
  const profileData = {
    first_name: formData.firstName,
    last_name: formData.lastName,
    dob: formData.dob,
    gender: formData.gender,
    phone: formData.phoneNumber,
    account_address: formData.accountAddress,
  };
	console.log(profileData);
  try {
    const response = await fetch(`${API_URL}/residents/user_profile/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(profileData),
    });

    const data = await response.json();

    if (response.ok) {
      showToast('Profile successfully created', 'success');
      window.location.href = '/dashboard/resident/profile';
    } else {
      showToast(`Error: ${data.detail || 'Error creating profile'}`, 'error');
    }
  } catch (error: any) {
    showToast(`An unexpected error occurred: ${error.message || error}`, 'error');
  }
};

  return (
  <div className="flex">
    {/* Sidebar */}
    <Sidebar />

    {/* Profile Form Section */}
    <div className="flex-1 p-6 transition-all duration-300 ml-0 lg:ml-64 lg:pl-0 mt-16 lg:mt-0">
      <div className="max-w-2xl mx-auto">
        <form onSubmit={handleSubmit} className="bg-white p-6 rounded-xl shadow-md space-y-4">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Profile Settings</h2>

          {/* First Name */}
          <div>
            <label className="block mb-1 text-sm font-semibold">First Name</label>
            <input
              name="firstName"
              value={formData.firstName}
              onChange={handleInputChange}
              className="w-full border border-gray-300 px-3 py-2 rounded"
            />
            {formErrors.firstName && (
              <p className="text-red-500 text-sm mt-1">{formErrors.firstName}</p>
            )}
          </div>

          {/* Last Name */}
          <div>
            <label className="block mb-1 text-sm font-semibold">Last Name</label>
            <input
              name="lastName"
              value={formData.lastName}
              onChange={handleInputChange}
              className="w-full border border-gray-300 px-3 py-2 rounded"
            />
            {formErrors.lastName && (
              <p className="text-red-500 text-sm mt-1">{formErrors.lastName}</p>
            )}
          </div>

          {/* DOB */}
          <div>
            <label className="block mb-1 text-sm font-semibold">Date of Birth</label>
            <input
              name="dob"
              type="date"
              value={formData.dob}
              onChange={handleInputChange}
              className="w-full border border-gray-300 px-3 py-2 rounded"
            />
            {formErrors.dob && (
              <p className="text-red-500 text-sm mt-1">{formErrors.dob}</p>
            )}
          </div>

          {/* Gender */}
          <div>
            <label className="block mb-1 text-sm font-semibold">Gender</label>
            <select
              name="gender"
              value={formData.gender}
              onChange={handleInputChange}
              className="w-full border border-gray-300 px-3 py-2 rounded"
            >
              <option value="">Select Gender</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
            {formErrors.gender && (
              <p className="text-red-500 text-sm mt-1">{formErrors.gender}</p>
            )}
          </div>

          {/* Phone Number */}
          <div>
            <label className="block mb-1 text-sm font-semibold">Phone Number</label>
            <input
              name="phoneNumber"
              value={formData.phoneNumber}
              onChange={handleInputChange}
              className="w-full border border-gray-300 px-3 py-2 rounded"
              placeholder="0723456789"
            />
            {formErrors.phoneNumber && (
              <p className="text-red-500 text-sm mt-1">{formErrors.phoneNumber}</p>
            )}
          </div>

          {/* Account Address */}
          <div>
            <label className="block mb-1 text-sm font-semibold">Account Address</label>
            <input
              name="accountAddress"
              value={formData.accountAddress}
              onChange={handleInputChange}
              className="w-full border border-gray-300 px-3 py-2 rounded"
              placeholder="0xABC123..."
            />
            {formErrors.accountAddress && (
              <p className="text-red-500 text-sm mt-1">{formErrors.accountAddress}</p>
            )}
          </div>

          <div className="flex items-center space-x-4">
            <ConnectWallet />
          </div>

          {/* Confirm Email */}
          <div className="flex items-center space-x-4">
            <button
              type="button"
              onClick={handleEmailConfirmation}
              className={`py-2 px-4 rounded font-semibold ${
                emailConfirmed
                  ? 'bg-green-500 text-white'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {emailConfirmed ? 'Email Confirmed' : 'Confirm Email'}
            </button>
            {emailConfirmed && <span className="text-green-600">✔️</span>}
          </div>

          {/* Save */}
          <button
            type="submit"
            className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2 rounded"
            disabled={!emailConfirmed}
          >
            Save Changes
          </button>
        </form>
      </div>

      {/* Email Confirmation Popup */}
      {showEmailConfirmation && (
        <div className="fixed inset-0 flex items-center justify-center z-50">
          <div
            className="absolute inset-0 bg-white/30 backdrop-blur-sm"
            onClick={() => setShowEmailConfirmation(false)}
          />

          <div className="relative bg-white p-6 rounded-lg shadow-md w-full max-w-sm space-y-4 z-10">
            <button
              className="absolute top-3 right-3 text-gray-500 hover:text-gray-700"
              onClick={() => setShowEmailConfirmation(false)}
            >
              <XMarkIcon className="h-6 w-6" />
            </button>

            <h3 className="text-lg font-semibold">Enter Confirmation Code</h3>
            <input
              type="text"
              value={confirmationCode}
              onChange={handleCodeChange}
              className="w-full border border-gray-300 px-3 py-2 rounded"
              placeholder="Enter code"
            />
            {formErrors.confirmationCode && (
              <p className="text-red-500 text-sm mt-1">{formErrors.confirmationCode}</p>
            )}
            <div className="flex justify-between items-center">
              <button
                onClick={handleConfirmCode}
                className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded"
              >
                Confirm Code
              </button>
              <button
                onClick={handleResendCode}
                disabled={isResendDisabled}
                className={`py-2 px-4 rounded font-semibold ${
                  isResendDisabled
                    ? 'bg-gray-400 text-gray-700'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                Resend {isResendDisabled && `(${timer}s)`}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  </div>
);
};

export default Profile;
