// @/components/WorkSection.jsx
import Link from 'next/link';

export default function WorkSection() {
  return (
    <section className="py-16 bg-white">
      <div className="max-w-5xl mx-auto px-4 text-center">
        <h2 className="text-3xl font-bold mb-4">How It Works</h2>
        <p className="text-gray-600 mb-10">
          Simple steps to start trading power using SCT tokens.
        </p>
        <div className="grid gap-8 md:grid-cols-3">
          <div className="bg-gray-50 rounded-2xl p-6 shadow-sm hover:shadow-md transition">
            <div className="text-blue-600 text-4xl font-bold mb-2">1</div>
            <h3 className="text-xl font-semibold mb-2">Sign Up</h3>
            <p className="text-gray-600">
              Create an account and connect your Starknet wallet.
            </p>
          </div>
          <div className="bg-gray-50 rounded-2xl p-6 shadow-sm hover:shadow-md transition">
            <div className="text-blue-600 text-4xl font-bold mb-2">2</div>
            <h3 className="text-xl font-semibold mb-2">Add Power</h3>
            <p className="text-gray-600">
              Generate or receive power tokens (SCT) by contributing energy.
            </p>
          </div>
          <div className="bg-gray-50 rounded-2xl p-6 shadow-sm hover:shadow-md transition">
            <div className="text-blue-600 text-4xl font-bold mb-2">3</div>
            <h3 className="text-xl font-semibold mb-2">Trade or Monitor</h3>
            <p className="text-gray-600">
              Offer tokens, view requests, and track your transactions in real
              time.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
