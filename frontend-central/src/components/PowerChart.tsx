'use client';

import { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

interface DataPoint {
  timestamp: string;
  power: number;
}

export default function PowerChart() {
  const [data, setData] = useState<DataPoint[]>([]);

  useEffect(() => {
    const es = new EventSource(`${process.env.NEXT_PUBLIC_API_URL}/stream_power`);

    es.onmessage = (event) => {
      const now = new Date().toLocaleTimeString();
      const power = parseFloat(event.data);

      setData((prev) => {
        const next = [...prev, { timestamp: now, power }];
        // keep only last 20 points
        return next.length > 20 ? next.slice(next.length - 20) : next;
      });
    };

    return () => {
      es.close();
    };
  }, []);

  return (
    <div className="w-full h-80 bg-white p-4 rounded shadow">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="timestamp" minTickGap={20} />
          <YAxis unit=" W" />
          <Tooltip formatter={(value: number) => `${value.toFixed(4)} W`} />
          <Line
            type="monotone"
            dataKey="power"
            stroke="#4CAF50"
            strokeWidth={2}
            isAnimationActive={false}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}