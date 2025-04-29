'use client';

import React, { useState, useEffect } from 'react';
import Sidebar from '../../../../components/Sidebar';
import useAuth from '../../../../hooks/useAuth';
import { useRouter } from 'next/navigation';

interface Device {
  id: number;
  device_type: string;
  device_id: string;
  connection_type: string;
  estate: string | null;
  status: string | null;
  pin_loads: Array<{ pin: string; load: string }>;
  created_at: string;
}

export default function Devices() {
  useAuth();
  const router = useRouter();
  const API_URL = process.env.NEXT_PUBLIC_API_URL;

  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [showAddDeviceForm, setShowAddDeviceForm] = useState(false);
  const [deviceForm, setDeviceForm] = useState({
    device_type: '',
    device_id: '',
    connection_type: '',
    estate: 'juja',  // Hardcoded to "juja"
    pin_loads: [{ pin: '', load: '' }],
  });

  // Fetch existing devices
  useEffect(() => {
    const fetchDevices = async () => {
      const token = localStorage.getItem('token');
      try {
        const res = await fetch(`${API_URL}/get_devices`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
        if (!res.ok) throw new Error('Failed to fetch devices');
        const data = await res.json();
        setDevices(data.devices || []);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'An unexpected error occurred');
      } finally {
        setLoading(false);
      }
    };
    fetchDevices();
  }, [API_URL]);

  // Handle form inputs for pin_loads
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>, idx: number) => {
    const { name, value } = e.target;
    const updated = [...deviceForm.pin_loads];
    updated[idx] = { ...updated[idx], [name]: value };
    setDeviceForm({ ...deviceForm, pin_loads: updated });
  };

  const handleAddPinLoad = () => {
    setDeviceForm(prev => ({ 
      ...prev, 
      pin_loads: [...prev.pin_loads, { pin: '', load: '' }] 
    }));
  };

  const handleSubmit = async () => {
    // Check if any field in the deviceForm is empty
    console.log("About to submit:", deviceForm);
    const { device_type, device_id, connection_type, estate, pin_loads } = deviceForm;
    if (!device_type || !device_id || !connection_type || !estate || !pin_loads?.length) {
      setError("All fields must be filled out");
      return;
    }
  
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API_URL}/create_device`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(deviceForm),
      });
  
      const data = await res.json();
  
      if (!res.ok) throw new Error(data.detail || 'Failed to create device');
  
      // Show success message
      setSuccessMessage("Device created successfully!");
  
      // After the success message disappears, refresh the page
      setTimeout(() => {
        setSuccessMessage('');
        window.location.reload();
      }, 2000); // Delay before page refresh to show the success message
  
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    }
  };

  return (
    <div className="flex">
      <Sidebar />

      <div className="flex-1 p-6 ml-0 lg:ml-64 lg:pl-0 mt-16 lg:mt-0 flex flex-col items-center">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">My Devices</h1>

        {loading && <p className="text-gray-600">Loading devices...</p>}
        {error && <p className="text-red-600 mb-4">Error: {error}</p>}

        {/* No Devices */}
        {!loading && devices.length === 0 && (
          <div className="bg-white rounded-xl shadow-lg p-8 text-center w-full max-w-md">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">No Devices Registered</h2>
            <p className="text-gray-600 mb-6">
              It looks like there are no devices. Click below to add your first device.
            </p>
            <button
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
              onClick={() => setShowAddDeviceForm(true)}
            >
              Add Device
            </button>
          </div>
        )}

        {/* Add Device Form Popup */}
        {showAddDeviceForm && (
          <div className="fixed inset-0 flex items-center justify-center z-50">
            <div
              className="absolute inset-0 bg-black/30 backdrop-blur-sm"
              onClick={() => setShowAddDeviceForm(false)}
            />
            <div className="relative bg-white p-8 rounded-xl shadow-lg w-full max-w-md">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">Add New Device</h2>

              {/* Error and Success Messages */}
              {error && <div className="bg-red-100 text-red-700 p-4 rounded-lg mb-4">{error}</div>}
              {successMessage && <div className="bg-green-100 text-green-700 p-4 rounded-lg mb-4">{successMessage}</div>}

              <div className="space-y-4">
                {/* Device Type */}
                <div>
                  <span className="font-medium text-gray-600">Device Type:</span>
                  <select
                    value={deviceForm.device_type}
                    onChange={(e) => setDeviceForm({ ...deviceForm, device_type: e.target.value })}
                    className="border p-2 w-full rounded-md"
                  >
                    <option value="">Select Device Type</option>
                    <option value="Arduino Uno">Arduino Uno</option>
                    <option value="Arduino Mega">Arduino Mega</option>
                    <option value="Raspberry Pi">Raspberry Pi</option>
                    <option value="ESP32">ESP32</option>
                  </select>
                </div>

                {/* Device ID */}
                <input
                  type="text"
                  placeholder="Device ID"
                  value={deviceForm.device_id}
                  onChange={(e) => setDeviceForm({ ...deviceForm, device_id: e.target.value })}
                  className="border p-2 w-full rounded-md"
                />

                {/* Connection Type */}
                <div>
                  <span className="font-medium text-gray-600">Connection Type:</span>
                  <select
                    value={deviceForm.connection_type}
                    onChange={(e) => setDeviceForm({ ...deviceForm, connection_type: e.target.value })}
                    className="border p-2 w-full rounded-md"
                  >
                    <option value="">Select Connection Type</option>
                    <option value="Wired">Wired</option>
                    <option value="Wireless">Wireless</option>
                  </select>
                </div>

                {/* Estate (hardcoded to Juja) */}
                <div>
                  <span className="font-medium text-gray-600">Estate:</span>
                  <input
                    type="text"
                    value={deviceForm.estate}
                    disabled
                    className="border p-2 w-full rounded-md"
                  />
                </div>

                {/* Pin Loads */}
                <div>
                  <span className="font-medium">Pin Loads</span>
                  {deviceForm.pin_loads.map((pl, idx) => (
                    <div key={idx} className="flex space-x-2 mt-2">
                      <input
                        name="pin"
                        value={pl.pin}
                        onChange={e => handleInputChange(e, idx)}
                        placeholder="Pin"
                        className="border p-2 w-24 rounded-md"
                      />
                      <input
                        name="load"
                        value={pl.load}
                        onChange={e => handleInputChange(e, idx)}
                        placeholder="Load"
                        className="border p-2 w-24 rounded-md"
                      />
                    </div>
                  ))}
                  <button
                    type="button"
                    className="mt-2 text-blue-600 hover:underline"
                    onClick={handleAddPinLoad}
                  >
                    + Add Pin Load
                  </button>
                </div>

                <div className="flex justify-end space-x-4 mt-6">
                  <button
                    className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 transition"
                    onClick={() => setShowAddDeviceForm(false)}
                  >
                    Close
                  </button>
                  <button
                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
                    onClick={handleSubmit}
                  >
                    Create Device
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Device Cards */}
        {!loading && devices.length > 0 && (
          <div className="w-full max-w-4xl mx-auto mt-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {devices.map(device => (
                <div
                  key={device.id}
                  className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow max-w-sm"
                >
                  <h2 className="text-xl font-semibold text-gray-800 mb-2">{device.device_id}</h2>
                  
                  <div className="mb-3">
                    <span className="font-medium text-gray-600">Device Type:</span>
                    <span className="text-gray-800">{device.device_type}</span>
                  </div>

                  <div className="mb-3">
                    <span className="font-medium text-gray-600">Connection Type:</span>
                    <span className="text-gray-800">{device.connection_type}</span>
                  </div>

                  <div className="mb-3">
                    <span className="font-medium text-gray-600">Estate:</span>
                    <span className="text-gray-800">{device.estate ?? '—'}</span>
                  </div>

                  <div className="mb-3">
                    <span className="font-medium text-gray-600">Status:</span>
                    <span className="text-gray-800">{device.status ?? 'Inactive'}</span>
                  </div>

                  <div className="mt-3">
                    <span className="font-medium text-gray-600">Pin Loads:</span>
                    <ul className="list-disc list-inside ml-4">
                      {device.pin_loads.length > 0
                        ? device.pin_loads.map((pl, i) => (
                            <li key={i}>{pl.pin}: {pl.load}</li>
                          ))
                        : <li>—</li>
                      }
                    </ul>
                  </div>

                  <p className="text-sm text-gray-500 mt-4">
                    Registered: {new Date(device.created_at).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}