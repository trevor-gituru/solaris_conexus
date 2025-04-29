// src/app/dashboard/resident/page.tsx

export const metadata = {
  title: 'My Devices',
  description: 'Resident Dashboard Devices',
};

import Devices from './Devices';

export default function Page() {
  return <Devices />;
}