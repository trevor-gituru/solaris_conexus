// components/ui/CtaSection.tsx

import Link from 'next/link';

export default function CtaSection() {
  return (
    <section className="py-16 bg-gray-100 text-center">
      <div className="max-w-4xl mx-auto px-4">
        <h2 className="text-3xl font-bold mb-4">Ready to get started?</h2>
        <p className="text-gray-600 mb-8">
          Join now and explore the future of energy trading and smart contracts.
        </p>
        <div className="flex flex-col sm:flex-row justify-center items-center gap-4">
  <Link
    href="/auth/register"
    className="inline-block px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition"
  >
    Create an Account
  </Link>
  <Link
    href="/auth/login"
    className="inline-block px-6 py-3 bg-gray-200 text-gray-800 rounded-xl hover:bg-gray-300 transition"
  >
    Log in
  </Link>
</div>
      </div>
    </section>
  );
}
