// app/layout.tsx
import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import './globals.css';
import { ToastProvider } from '@/components/providers/ToastProvider';

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
});

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: 'Solaris Conexus',
  description: 'The homepage',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />

        {/* JSON-LD Structured Data */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "SoftwareApplication",
              "name": "Solaris Conexus",
              "operatingSystem": "Web",
              "applicationCategory": "Energy Trading Platform",
              "description":
                "Solaris Conexus is a decentralized energy trading platform that uses IoT and blockchain to enable solar power producers and consumers to trade using PowerTokens.",
              "url": "https://solaris.razaoul.xyz",
              "image": "https://www.razaoul.xyz/preview.jpg",
              "creator": {
                "@type": "Person",
                "name": "Trevor Muriuki Gituru",
              },
              "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD",
              },
              "sameAs": [
                "https://github.com/trevor-gituru/solaris_conexus.git",
                "https://sepolia.voyager.online/contract/0x0696e1ba36b1b46ccfda4a6ae963b12c932e36d1a1008d5d0a03033b12d86827"
              ],
            }),
          }}
        />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ToastProvider>{children}</ToastProvider>
      </body>
    </html>
  );
}
