import React, { useEffect, useState } from 'react';
import PowerChart from '@/components/PowerChart'; // adjust path as needed

interface MonitorProps {
  deviceId: number;
  onClose: () => void;
}

interface DataPoint {
  timestamp: string;
  power: number;
}

export default function Monitor({ deviceId, onClose }: MonitorProps) {
  const [powerData, setPowerData] = useState<DataPoint[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const BACKEND_HOST = process.env.NEXT_PUBLIC_BACKEND_HOST;
    const socket = new WebSocket(
      `${protocol}://${BACKEND_HOST}/device/stream?token=${token}`
    );

    socket.onopen = () => {
      console.log(`WebSocket opened for device ${deviceId}`);
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (typeof data.power === 'number') {
          const now = new Date();
          const timestamp = now.toLocaleTimeString('en-GB', { hour12: false });

          setPowerData((prev) => {
            const next = [...prev, { timestamp, power: data.power }];
            return next.length > 20 ? next.slice(next.length - 20) : next;
          });
        }
      } catch (e) {
        console.error('Invalid JSON:', e);
      }
    };

    socket.onerror = (event) => {
      console.warn('WebSocket encountered error:', event);
      //setError('Connection error. Please try again later.');
    };

    socket.onclose = (event) => {
      if (event.code !== 1006) {
        console.log(`WebSocket closed: code=${event.code}, reason=${event.reason}`);
      } else {
        console.log('WebSocket closed with code 1006 (ignored)');
      }
    };

    return () => {
      socket.close(1000, 'Component unmounted');
    };
  }, [deviceId]);

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-2xl">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-semibold">Monitor Device {deviceId}</h2>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-gray-700"
        >
          ✕
        </button>
      </div>

      {error && <p className="text-red-600 mb-4">{error}</p>}

      <PowerChart data={powerData} />
    </div>
  );
}

