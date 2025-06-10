// components/ui/FeatureSection.tsx

export default function FeatureSection() {
  return (
    <section className="py-16 bg-white">
      <div className="max-w-6xl mx-auto px-4 text-center">
        <h2 className="text-3xl font-bold mb-4">Why Choose Our Platform?</h2>
        <p className="text-gray-600 mb-10">
          Here’s what makes us different and useful.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8">
          <div className="p-6 border rounded-xl shadow-sm">
            <h3 className="text-xl font-semibold mb-2">Transparent Trades</h3>
            <p className="text-gray-500">View, verify, and track all trades in real time.</p>
          </div>

          <div className="p-6 border rounded-xl shadow-sm">
            <h3 className="text-xl font-semibold mb-2">Token Integration</h3>
            <p className="text-gray-500">Easily trade using SCT and STRK tokens via wallet.</p>
          </div>

          <div className="p-6 border rounded-xl shadow-sm">
            <h3 className="text-xl font-semibold mb-2">Smart Contracts</h3>
            <p className="text-gray-500">Built on secure and verifiable Starknet contracts.</p>
          </div>
        </div>
      </div>
    </section>
  );
}
