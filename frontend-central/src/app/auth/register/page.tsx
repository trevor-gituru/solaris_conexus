// app/auth/register/page.tsx
export const metadata = {
    title: 'Register',
  };
  
import RegisterForm from './RegisterForm';
import { GoogleOAuthProvider } from '@react-oauth/google';

export default function Page() {
	return(
		<GoogleOAuthProvider clientId={process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID!}>
			<RegisterForm />
		</GoogleOAuthProvider>
	);

}
