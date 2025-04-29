// src/app/dashboard/resident/page.tsx
'use client';

import PowerChart from '../../../components/PowerChart';
import Sidebar from '../../../components/Sidebar';
import useAuth from '../../../hooks/useAuth';

export default function ResidentDashboard() {
  useAuth();

  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 p-6 ml-0 lg:ml-64 lg:pl-0">
        <h1 className="text-3xl font-bold mb-4">Live Power Monitoring</h1>
        <PowerChart />
      </main>
    </div>
  );
}