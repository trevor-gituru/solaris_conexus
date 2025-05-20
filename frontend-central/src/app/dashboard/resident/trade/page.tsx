// app/dashboard/resident/trade/page.tsx

import TradeDecide from './TradeDecide'; // Import the decision logic

export const metadata = {
  title: 'Trade',
  description: 'Resident sell/buy tokens',
};

export default function TradePage() {
  return <TradeDecide />;
}
