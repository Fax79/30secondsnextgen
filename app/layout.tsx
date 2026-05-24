import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Script from "next/script";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "30SecondsToGuide | Generatore di Itinerari e Guide",
  description: "Crea il tuo itinerario di viaggio personalizzato in formato PDF, ottimizzato per budget, tempistiche e composizione del gruppo.",
  openGraph: {
    title: '30SecondsToGuide',
    description: 'Generazione editoriale di itinerari e guide di viaggio in PDF.',
    url: 'https://www.30secondstoguide.it', // Sostituisci con il tuo vero dominio
    siteName: '30SecondsToGuide',
    locale: 'it_IT',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: '30SecondsToGuide',
    description: 'Generazione editoriale di itinerari e guide di viaggio in PDF.',
  },
  robots: {
    index: true,
    follow: true,
  }
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="it"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        {children}
        
        {/* Script Umami Analytics */}
        <Script 
          src="https://cloud.umami.is/script.js" 
          data-website-id="897aa2b4-2423-49b6-978d-c1f36c84c4b3" 
          strategy="afterInteractive"
        />
      </body>
    </html>
  );
}
