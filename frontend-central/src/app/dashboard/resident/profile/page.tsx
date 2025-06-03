// src/app/dashboard/resident/profile/page.tsx

import ProfileDecide from './ProfileDecide'; // Import the decision logic

export const metadata = {
  title: 'Profile',
  description: 'User profile page',
};

export default function ProfilePage() {
  return <ProfileDecide />;
}
