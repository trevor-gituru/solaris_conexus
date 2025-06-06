// app/auth/login/page.tsx
export const metadata = {
  title: 'LogIn',
};

import { GoogleOAuthProvider } from '@react-oauth/google';
import LoginForm from './LoginForm';

export default function Page() {
  return (
    <GoogleOAuthProvider clientId={process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID!}>
      <LoginForm />
    </GoogleOAuthProvider>
  );
}
