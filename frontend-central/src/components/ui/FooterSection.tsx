// @/components/ui/Footer.tsx
import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="bg-gray-100 text-sm mt-16">
      <div className="max-w-6xl mx-auto px-4 py-10 grid md:grid-cols-3 gap-8">
        {/* Brand */}
        <div>
          <h2 className="text-xl font-bold text-gray-800 mb-2">Solaris Conexus</h2>
          <p className="text-gray-600">Empowering smart energy trading.</p>
        </div>

        {/* Links */}
        <div>
          <h3 className="text-gray-800 font-semibold mb-2">Quick Links</h3>
          <ul className="space-y-1">
            <li><Link href="/" className="text-gray-600 hover:text-blue-600">Home</Link></li>
            <li><Link href="/#how-it-works" className="text-gray-600 hover:text-blue-600">How it Works</Link></li>
            <li><Link href="/auth/register" className="text-gray-600 hover:text-blue-600">Create an Account</Link></li>
            <li><Link href="/auth/login" className="text-gray-600 hover:text-blue-600">Log In</Link></li>
          </ul>
        </div>

        {/* Legal */}
        <div>
          <h3 className="text-gray-800 font-semibold mb-2">Legal</h3>
          <ul className="space-y-1">
            <li><Link href="/terms" className="text-gray-600 hover:text-blue-600">Terms of Service</Link></li>
            <li><Link href="/privacy" className="text-gray-600 hover:text-blue-600">Privacy Policy</Link></li>
          </ul>
        </div>
      </div>

      <div className="text-center text-gray-500 text-xs py-4 border-t">
        &copy; {new Date().getFullYear()} Solaris Conexus. All rights reserved.
      </div>
    </footer>
  );
}
