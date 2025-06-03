'use client';

import React, { useState, useEffect } from 'react';
import Sidebar from '@/components/Sidebar';
import Monitor from './Monitor';
import useAuth from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';
import { useToast } from '@/components/providers/ToastProvider';

interface PinLoad {
  pin: string;
  load: string;
}

interface Device {
  id: number;
  device_type: string;
  device_id: string;
  connection_type: string;
  estate: string | null;
  status: string | null;
  pin_loads: PinLoad[];
  created_at: string;
}

export default function Devices() {
  useAuth();
  const router = useRouter();
  const API_URL = process.env.NEXT_PUBLIC_API_URL!;

  const [device, setDevice] = useState<Device | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [successMessage, setSuccessMessage] = useState<string>('');
  const [showAddDeviceForm, setShowAddDeviceForm] = useState(false);
  const [togglingDeviceId, setTogglingDeviceId] = useState<number | null>(null);
  const [showMonitorDeviceId, setShowMonitorDeviceId] = useState<number | null>(null);
  
  const [showEditDeviceForm, setShowEditDeviceForm] = useState(false);

  const [deviceForm, setDeviceForm] = useState({
    device_type: '',
    device_id: '',
    connection_type: '',
    estate: 'Juja',
    pin_loads: [{ pin: '', load: '' }],
  });
  
  const { showToast } = useToast();


  // Fetch devices
useEffect(() => {
  const fetchDevices = async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API_URL}/residents/device/get`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      const result = await res.json();

      if (!result.success) {
	  showToast(result.detail || 'Failed to fetch device', 'error');
       } else {
	  setDevice(result.data ?? null); // handle either one device or null
       }
    } catch (error: any) {
      showToast(error?.message || 'An unexpected error occurred', 'error');
    } finally {
      setLoading(false);
    }
  };

  fetchDevices();
}, [API_URL]);

   const hasDevice = !loading && device && Object.keys(device).length > 0;
  const [editDeviceForm, setEditDeviceForm] = useState(deviceForm);


  // Handlers for Create Device form
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>, idx: number) => {
    const { name, value } = e.target;
    const updated = [...deviceForm.pin_loads];
    updated[idx] = { ...updated[idx], [name]: value };
    setDeviceForm({ ...deviceForm, pin_loads: updated });
  };

const handleEditInputChange = (e: React.ChangeEvent<HTMLInputElement>, idx: number) => {
  const { name, value } = e.target;
  const updated = [...editDeviceForm.pin_loads];
  updated[idx] = { ...updated[idx], [name]: value };
  setEditDeviceForm({ ...editDeviceForm, pin_loads: updated });
};

  const handleAddPinLoad = () => {
    setDeviceForm(prev => ({
      ...prev,
      pin_loads: [...prev.pin_loads, { pin: '', load: '' }],
    }));
  };


  const handleSubmit = async () => {
    const { device_type, device_id, connection_type, estate, pin_loads } = deviceForm;
    if (!device_type || !device_id || !connection_type || !estate || !pin_loads.length) {
      setError('All fields must be filled out');
      return;
    }
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API_URL}/residents/device/create`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(deviceForm),
      });
      const data = await res.json();
      if (!res.ok) {
 	   showToast({ message: data.detail || 'Failed to create device', type: 'error' });
	    return;
  	}
      showToast('Device created successfully!', 'success' );

      setTimeout(() => {
      	window.location.reload();
     }, 4000);
    } catch (err: unknown) {
      showToast(
	    err instanceof Error ? err.message : 'An unexpected error occurred',
	    'error',
      );
    }
  };


const handleEditSubmit = async () => {
  const token = localStorage.getItem('token');
  try {
    const res = await fetch(`${API_URL}/residents/device/update`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(editDeviceForm),
    });

    const data = await res.json();

    if (!res.ok) {
      showToast(data.detail || 'Failed to update device', 'error');
      return;
    }

    showToast('Device updated successfully!', 'success');
    setShowEditDeviceForm(false);

    setTimeout(() => {
      window.location.reload();
    }, 4000);
  } catch (err: any) {
    showToast(err.message || 'An unexpected error occurred', 'error');
  }
};


  // Toggle device
  const toggleDevice = async (deviceId: number) => {
    const token = localStorage.getItem('token');
    setTogglingDeviceId(deviceId);
    try {
      const res = await fetch(`${API_URL}/residents/device/toggle`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      if (!res.ok) {
        const errData = await res.json();
        showToast(errData.detail || 'Failed to toggle device', "error");
      }
      const data = await res.json();
      showToast(data.message || `Device toggled`, "success");
    } catch (err: unknown) {
      showToast(err instanceof Error ? err.message : 'Toggle error', "error");
    } finally {
      setTogglingDeviceId(null);
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
        {!loading && (!device || Object.keys(device).length === 0) && (
  <div className="bg-white rounded-xl shadow-lg p-8 text-center w-full max-w-md">
    <h2 className="text-2xl font-semibold text-gray-800 mb-4">No Device Registered</h2>
    <p className="text-gray-600 mb-6">
      It looks like there is no device. Click below to add your device.
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

              {error && <div className="bg-red-100 text-red-700 p-4 rounded-lg mb-4">{error}</div>}
              {successMessage && <div className="bg-green-100 text-green-700 p-4 rounded-lg mb-4">{successMessage}</div>}

              <div className="space-y-4">
                <div>
                  <span className="font-medium text-gray-600">Device Type:</span>
                  <select
                    value={deviceForm.device_type}
                    onChange={e => setDeviceForm({ ...deviceForm, device_type: e.target.value })}
                    className="border p-2 w-full rounded-md"
                  >
                    <option value="">Select Device Type</option>
                    <option value="Arduino Uno">Arduino Uno</option>
                    <option value="Arduino Mega">Arduino Mega</option>
                    <option value="Raspberry Pi">Raspberry Pi</option>
                    <option value="ESP32">ESP32</option>
                  </select>
                </div>

                <input
                  type="text"
                  placeholder="Device ID"
                  value={deviceForm.device_id}
                  onChange={e => setDeviceForm({ ...deviceForm, device_id: e.target.value })}
                  className="border p-2 w-full rounded-md"
                />

                <div>
                  <span className="font-medium text-gray-600">Power Role:</span>
                  <select
                    value={deviceForm.connection_type}
                    onChange={e => setDeviceForm({ ...deviceForm, connection_type: e.target.value })}
                    className="border p-2 w-full rounded-md"
                  >
                    <option value="">Select Power Role</option>
                    <option value="Producer">Producer</option>
                    <option value="Consumer">Consumer</option>
                  </select>
                </div>

                <div>
                  <span className="font-medium text-gray-600">Estate:</span>
                  <input
                    type="text"
                    value={deviceForm.estate}
                    disabled
                    className="border p-2 w-full rounded-md"
                  />
                </div>

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

{showEditDeviceForm && (
  <div className="fixed inset-0 flex items-center justify-center z-50">
    <div
      className="absolute inset-0 bg-black/30 backdrop-blur-sm"
      onClick={() => setShowEditDeviceForm(false)}
    />
    <div className="relative bg-white p-8 rounded-xl shadow-lg w-full max-w-md">
      <h2 className="text-2xl font-semibold text-gray-800 mb-4">Edit Device</h2>

      <div className="space-y-4">
        <select
          value={editDeviceForm.device_type}
          onChange={e =>
            setEditDeviceForm({ ...editDeviceForm, device_type: e.target.value })
          }
          className="border p-2 w-full rounded-md"
        >
          <option value="">Select Device Type</option>
          <option value="Arduino Uno">Arduino Uno</option>
          <option value="Arduino Mega">Arduino Mega</option>
          <option value="Raspberry Pi">Raspberry Pi</option>
          <option value="ESP32">ESP32</option>
        </select>

        <input
          type="text"
          placeholder="Device ID"
          value={editDeviceForm.device_id}
          onChange={e =>
            setEditDeviceForm({ ...editDeviceForm, device_id: e.target.value })
          }
          className="border p-2 w-full rounded-md"
        />

        <select
          value={editDeviceForm.connection_type}
          onChange={e =>
            setEditDeviceForm({ ...editDeviceForm, connection_type: e.target.value })
          }
          className="border p-2 w-full rounded-md"
        >
          <option value="">Select Power Role</option>
          <option value="Producer">Producer</option>
          <option value="Consumer">Consumer</option>
        </select>

        <input
          type="text"
          value={editDeviceForm.estate}
          disabled
          className="border p-2 w-full rounded-md"
        />

        <div>
          <span className="font-medium">Pin Loads</span>
          {editDeviceForm.pin_loads.map((pl, idx) => (
            <div key={idx} className="flex space-x-2 mt-2">
              <input
                name="pin"
                value={pl.pin}
                onChange={e => handleEditInputChange(e, idx)}
                placeholder="Pin"
                className="border p-2 w-24 rounded-md"
              />
              <input
                name="load"
                value={pl.load}
                onChange={e => handleEditInputChange(e, idx)}
                placeholder="Load"
                className="border p-2 w-24 rounded-md"
              />
            </div>
          ))}
        </div>

        <div className="flex justify-end space-x-4 mt-6">
          <button
            className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 transition"
            onClick={() => setShowEditDeviceForm(false)}
          >
            Close
          </button>
          <button
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition"
            onClick={handleEditSubmit}
          >
            Save Changes
          </button>
        </div>
      </div>
    </div>
  </div>
)}

       {/* Single Device Card */}
{/* Device Card */}
        {hasDevice && (
          <div className="w-full max-w-4xl mx-auto mt-8">
            <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow max-w-sm">
              <h2 className="text-xl font-semibold text-gray-800 mb-2">{device.device_id}</h2>

              <div className="mb-3">
                <span className="font-medium text-gray-600">Device Type:</span>
                <span className="text-gray-800"> {device.device_type}</span>
              </div>

              <div className="mb-3">
                <span className="font-medium text-gray-600">Power Role:</span>
                <span className="text-gray-800"> {device.connection_type}</span>
              </div>

              <div className="mb-3">
                <span className="font-medium text-gray-600">Estate:</span>
                <span className="text-gray-800"> {device.estate ?? '—'}</span>
              </div>

              <div className="mb-3">
                <span className="font-medium text-gray-600">Status:</span>
                <span className="text-gray-800"> {device.status ?? 'Inactive'}</span>
              </div>

              <div className="mt-3">
                <span className="font-medium text-gray-600">Pin Loads:</span>
                <ul className="list-disc list-inside ml-4">
                  {device.pin_loads?.length > 0 ? (
                    device.pin_loads.map((pl, i) => (
                      <li key={i}>
                        {pl.pin}: {pl.load}
                      </li>
                    ))
                  ) : (
                    <li>—</li>
                  )}
                </ul>
              </div>

              <p className="text-sm text-gray-500 mt-4">
                Registered: {new Date(device.created_at).toLocaleString()}
              </p>

              <div className="flex flex-wrap items-center gap-3 mt-4">
<button
  disabled={device.status !== 'active' || togglingDeviceId === device.id}
  onClick={() => toggleDevice(device.id)}
  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2
    ${device.status === 'active' && togglingDeviceId !== device.id
      ? 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-400'
      : 'bg-gray-300 text-gray-600 cursor-not-allowed'}
  `}
>
  {togglingDeviceId === device.id ? 'Toggling...' : 'Toggle Device'}
</button>
		  <button
		    disabled={device.status !== 'active'}
		    onClick={() => setShowMonitorDeviceId(device.id)}
		    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2
		      ${device.status === 'active'
			? 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-400'
			: 'bg-gray-300 text-gray-600 cursor-not-allowed'}
		    `}
		  >
		    Monitor
		  </button>

		  <button
		    onClick={() => {
		      if (device) {
			setEditDeviceForm({
			  device_type: device.device_type,
			  device_id: device.device_id,
			  connection_type: device.connection_type,
			  estate: device.estate || '',
			  pin_loads: device.pin_loads,
			});
			setShowEditDeviceForm(true);
		      }
		    }}
		    className="px-4 py-2 rounded-lg text-sm font-medium text-indigo-600 hover:text-white hover:bg-indigo-600 border border-indigo-600 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-300"
		  >
		    Edit Device
		  </button>
	</div>
            </div>
          </div>
        )}

        {/* Monitor Modal */}
        {showMonitorDeviceId !== null && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <Monitor
              deviceId={showMonitorDeviceId}
              onClose={() => setShowMonitorDeviceId(null)}
            />
          </div>
        )}
      </div>
    </div>
  );
}

