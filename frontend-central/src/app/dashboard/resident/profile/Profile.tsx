'use client';

import React, { useState, useEffect } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import Sidebar from '../../../../components/Sidebar';
import useAuth from '../../../../hooks/useAuth';

const Profile = () => {
  useAuth();

  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    dob: '',
    gender: '',
    phoneNumber: '',
  });
  const [emailConfirmed, setEmailConfirmed] = useState(false);
  const [showEmailConfirmation, setShowEmailConfirmation] = useState(false);
  const [confirmationCode, setConfirmationCode] = useState('');
  const [timer, setTimer] = useState(60);
  const [isResendDisabled, setIsResendDisabled] = useState(false);
  const [storedCode, setStoredCode] = useState(''); // Store the confirmation code

  const API_URL = process.env.NEXT_PUBLIC_API_URL ; // Backend URL

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleEmailConfirmation = async () => {
    const token = localStorage.getItem('token'); // Get JWT token
    setShowEmailConfirmation(true);
    setTimer(60);
    setIsResendDisabled(true);
  
    try {
      // Send request to get the confirmation code
      const response = await fetch(`${API_URL}/confirm_email`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`, // Add JWT token here
        },
      });
  
      const data = await response.json();
  
      if (response.ok) {
        // Assuming the confirmation code is in `data.code`
        setStoredCode(data.code); // Store the confirmation code received from the backend
      } else {
        // If response is not ok, handle error
        alert('Error confirming email: ' + data.detail);
      }
    } catch (error: unknown) { 
      // Catch network or unexpected errors
      if (error instanceof Error) {
        // If the error is an instance of Error, access the message property
        alert(`An unexpected error occurred: ${error.message}`);
      } else {
        // If the error is not an instance of Error, handle it as a generic unknown error
        alert('An unexpected error occurred.');
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
      alert('Invalid confirmation code');
    }
  };

  const handleResendCode = async () => {
    setTimer(60);
    setIsResendDisabled(true);

    const token = localStorage.getItem('token'); // Get JWT token
    const response = await fetch(`${API_URL}/confirm_email`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`, // Add JWT token here
      },
    });

    const data = await response.json();
    if (data.success) {
      setStoredCode(data.code); // Update the stored code after resend
    } else {
      alert('Error resending code');
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

  const token = localStorage.getItem('token'); // Get JWT token

  // Construct the data object based on the form data
  const profileData = {
    first_name: formData.firstName,
    last_name: formData.lastName,
    dob: formData.dob,
    gender: formData.gender,
    phone: formData.phoneNumber || null, // Optional field, so set it to null if not provided
  };

  try {
    const response = await fetch(`${API_URL}/create_profile`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`, // Add JWT token here
      },
      body: JSON.stringify(profileData), // Send the profile data to the backend
    });

    const data = await response.json();

    if (response.ok) {
      // Success: Profile created
      alert('Profile successfully created');
      window.location.href = '/dashboard/resident/profile'; // Redirect to profile page
    } else {
      // Error: Handle validation or other errors
      if (data.detail) {
        // Show backend error message (e.g., validation error)
        alert(`Error: ${data.detail}`);
      } else {
        // If no detail provided, show a generic error message
        alert('Error creating profile. Please try again later.');
      }
    }
  } catch (error: unknown) { 
    // Catch network or unexpected errors
    if (error instanceof Error) {
      // If the error is an instance of Error, access the message property
      alert(`An unexpected error occurred: ${error.message}`);
    } else {
      // If the error is not an instance of Error, handle it as a generic unknown error
      alert('An unexpected error occurred.');
    }
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
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>

            {/* Phone Number */}
            <div>
              <label className="block mb-1 text-sm font-semibold">Phone Number</label>
              <input
                name="phoneNumber"
                value={formData.phoneNumber}
                onChange={handleInputChange}
                className="w-full border border-gray-300 px-3 py-2 rounded"
                placeholder="(123) 456-7890"
              />
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
              disabled={!emailConfirmed} // Disable save if email is not confirmed
            >
              Save Changes
            </button>
          </form>
        </div>

        {/* Email Confirmation Popup */}
        {showEmailConfirmation && (
          <div className="fixed inset-0 flex items-center justify-center z-50">
            {/* blurred background overlay */}
            <div
              className="absolute inset-0 bg-white/30 backdrop-blur-sm"
              onClick={() => setShowEmailConfirmation(false)}
            />

            <div className="relative bg-white p-6 rounded-lg shadow-md w-full max-w-sm space-y-4 z-10">
              {/* close icon */}
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