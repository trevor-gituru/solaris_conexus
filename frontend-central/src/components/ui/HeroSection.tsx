// @/components/HeroSection.jsx
import Link from 'next/link';
import Image from 'next/image';

export default function HeroSection() {
  return (
    <section className="text-center py-20 bg-gradient-to-b from-white to-gray-50">
      <div className="flex justify-center mb-6">
        <Image
          src="/android-chrome-512x512.png" // adjust if you want a different icon file
          alt="Smart Energy Logo"
          width={80}
          height={80}
          priority
        />
      </div>
      <h1 className="text-4xl md:text-5xl font-bold mb-4">
        Empowering Energy Through Decentralized Trading
      </h1>
      <p className="text-lg text-gray-600 max-w-xl mx-auto mb-6">
        Trade power tokens, monitor usage, and earn rewards on the blockchain.
      </p>
      <div className="flex justify-center gap-4">
        <Link href="/auth/register">
          <button className="bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition">
            Get Started
          </button>
        </Link>
      </div>
    </section>
  );
}
