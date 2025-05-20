// PowerChart.tsx
'use client';

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

interface PowerChartProps {
  data: DataPoint[];
}

export default function PowerChart({ data }: PowerChartProps) {
  return (
    <div className="w-full h-80 bg-white p-4 rounded shadow">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="timestamp" minTickGap={20} />
          <YAxis unit=" W" domain={['auto', 'auto']} />
          <Tooltip
            formatter={(value: number) => `${value.toFixed(4)} W`}
            labelFormatter={(label) => `Time: ${label}`}
          />
          <Line
            type="monotone"
            dataKey="power"
            stroke="#4CAF50"
            strokeWidth={2}
            isAnimationActive={false}
            dot={false}
            connectNulls
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

