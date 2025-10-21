# Frontend - Central Dashboard

This directory contains the source code for the Solaris Conexus web dashboard, a Next.js application that serves as the primary user interface for interacting with the system.

## Overview

The frontend allows users to:
-   Authenticate and manage their profile.
-   View real-time energy consumption and production data.
-   Connect their Starknet wallet (Braavos).
-   Purchase and trade Solaris Conexus Tokens (SCT).
-   Monitor their devices.

## Tech Stack

-   **Framework:** [Next.js](https://nextjs.org/) (with App Router)
-   **Language:** [TypeScript](https://www.typescriptlang.org/)
-   **Styling:** [Tailwind CSS](https://tailwindcss.com/)
-   **Wallet Integration:** [Starknet.js](https://www.starknetjs.com/) for wallet connectivity.
-   **Charting:** A charting library is used within `PowerChart.tsx` (e.g., Recharts, Chart.js).

## Project Structure

```
src/
├── app/
│   ├── auth/         # Authentication pages (login, signup)
│   ├── dashboard/    # Main user dashboard pages
│   ├── layout.tsx    # Root layout
│   └── page.tsx      # Landing page
├── components/
│   ├── providers/    # React Context providers (e.g., for wallet, auth)
│   ├── ui/           # General UI components (buttons, inputs, etc.)
│   ├── ConnectWallet.tsx # Starknet wallet connection component
│   ├── PowerChart.tsx    # Component for displaying energy data charts
│   └── Sidebar.tsx       # Dashboard navigation sidebar
├── hooks/            # Custom React hooks
└── lib/              # Library functions, API clients, and utilities
```

## Getting Started

### Prerequisites

-   [Node.js](https://nodejs.org/) (v18 or later)
-   [npm](https://www.npmjs.com/) or [yarn](https://yarnpkg.com/)

### Installation

1.  Navigate to the `frontend-central` directory:
    ```bash
    cd frontend-central
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```

### Running the Development Server

To start the development server, run:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

### Environment Variables

Create a `.env.local` file in the root of the `frontend-central` directory and add the following environment variables:

```
# The base URL for the central backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BACKEND_HOST=http://localhost:8000

# The address of the deployed Solaris Conexus Token (SCT) contract on Starknet
NEXT_PUBLIC_SCT_ADDRESS=0x...

# The address of the deployed Stark (STRK) contract on Starknet
NEXT_PUBLIC_STRK_ADDRESS=0x...

# The client ID for Google OAuth authentication
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com

# The Starknet RPC provider URL
NEXT_PUBLIC_PROVIDER_URL=https://starknet-sepolia.g.alchemy.com/v2/your-alchemy-api-key
```

#### Where to get these values:

-   **`NEXT_PUBLIC_SCT_ADDRESS`**: This is the address of your deployed Starknet smart contract. You can find this in the deployment output of the `solaris_conexus_token` project.
-   **`GOOGLE_CLIENT_ID`**: This can be obtained from the [Google Cloud Console](https://console.cloud.google.com/). You'll need to create a new project, configure the OAuth consent screen, and then create an "OAuth 2.0 Client ID" for a "Web application".
-   **`NEXT_PUBLIC_PROVIDER_URL`**: This is your connection endpoint to the Starknet network. You can get a free RPC URL from a provider like [Alchemy](https://www.alchemy.com/) by creating a new Starknet application in your dashboard.
