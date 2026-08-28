import type { Metadata } from "next";
import "./globals.css";
import { EcosystemProvider } from "@/lib/context";
import { Navbar } from "@/components/Navbar";
import { WelcomeModal } from "@/components/WelcomeModal";
import { ErrorReportModal } from "@/components/ErrorReportModal";
import { CommandPalette } from "@/components/CommandPalette";
import { SidebarNavigation } from "@/components/SidebarNavigation";
import { AiChatWidget } from "@/components/AiChatWidget";
import { Footer } from "@/components/Footer";
import { Analytics } from "@vercel/analytics/react";

export const metadata: Metadata = {
  metadataBase: new URL("https://sir-modpack.web.app"),
  title: "SIR ModPack — The Ultimate Minecraft Ecosystem (v1.0.0)",
  description: "The official home of SIR ModPack (v1.0.0). Unified Minecraft ecosystem featuring Modern 26.2 (Fabric) & Legacy 1.8.9 (Forge), 2048 SIR Shaders, PBR POM 32x textures, and Hardware Power Governor.",
  keywords: [
    "SIR ModPack",
    "SIR-ModPack",
    "SIR Modpack Minecraft",
    "Minecraft SIR ModPack",
    "SIR Mod Pack",
    "SIR Ecosystem",
    "Modern 26.2 Fabric",
    "Legacy 1.8.9 Forge",
    "OptiFine",
    "Sodium",
    "Iris",
    "SIR Shaders",
    "InGameAccountSwitcher",
    "Minecraft Mods",
    "Hypixel PvP",
    "SIR Launcher"
  ],
  authors: [{ name: "SIR Ahmed", url: "https://linktr.ee/sir.ahmed" }],
  creator: "SIR Ahmed",
  publisher: "SIR ModPack Ecosystem",
  alternates: {
    canonical: "https://sir-modpack.web.app",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  icons: {
    icon: [
      { url: "/favicon.ico", sizes: "any" },
      { url: "/favicon-32x32.png", sizes: "32x32", type: "image/png" },
      { url: "/favicon-16x16.png", sizes: "16x16", type: "image/png" },
      { url: "/icon.png", sizes: "192x192", type: "image/png" },
    ],
    shortcut: "/favicon.ico",
    apple: "/apple-touch-icon.png",
  },
  openGraph: {
    title: "SIR ModPack — The Ultimate Minecraft Ecosystem (v1.0.0)",
    description: "Modern 26.2 (Fabric) & Legacy 1.8.9 (Forge), 2048 HD Shaders, PBR POM 32x Textures & InGameAccountSwitcher.",
    url: "https://sir-modpack.web.app",
    siteName: "SIR ModPack",
    images: [
      {
        url: "/sir-logo.png",
        width: 512,
        height: 512,
        alt: "SIR ModPack Cyber Emblem",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "SIR ModPack — The Ultimate Minecraft Ecosystem (v1.0.0)",
    description: "Modern 26.2 (Fabric) & Legacy 1.8.9 (Forge), 2048 HD Shaders, PBR POM 32x Textures & InGameAccountSwitcher.",
    images: ["/sir-logo.png"],
    creator: "@sir_ahmed",
  },
};

const jsonLd = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "SIR ModPack",
  "url": "https://sir-modpack.web.app",
  "operatingSystem": "Windows 10, Windows 11",
  "applicationCategory": "GameApplication",
  "description": "Unified Minecraft gaming ecosystem with Modern 26.2 (Fabric) and Legacy 1.8.9 (Forge), SIR Shaders, and InGameAccountSwitcher.",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  },
  "author": {
    "@type": "Person",
    "name": "SIR Ahmed",
    "url": "https://linktr.ee/sir.ahmed"
  }
};

import { CookieConsent } from "@/components/CookieConsent";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" dir="ltr" className="dark scroll-smooth" suppressHydrationWarning style={{ backgroundColor: '#07090e', colorScheme: 'dark' }}>
      <head>
        <style dangerouslySetInnerHTML={{ __html: `
          html, body {
            background-color: #07090e !important;
            background: #07090e !important;
            color-scheme: dark !important;
            color: #f8fafc !important;
          }
          html.light-theme, html.light-theme body {
            background-color: #f8fafc !important;
            background: #f8fafc !important;
            color-scheme: light !important;
            color: #0f172a !important;
          }
        `}} />
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  var getCookie = function(name) {
                    var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
                    return match ? decodeURIComponent(match[2]) : null;
                  };
                  var theme = localStorage.getItem('sir_theme_mode') || localStorage.getItem('sir_theme') || getCookie('sir_theme_mode') || getCookie('sir_theme') || 'dark';
                  var lang = localStorage.getItem('sir_lang') || getCookie('sir_lang') || 'en';
                  var perf = localStorage.getItem('sir_perf_mode') || getCookie('sir_perf_mode') || 'cinematic';
                  
                  document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
                  document.documentElement.lang = lang;
                  document.documentElement.setAttribute('data-perf-mode', perf);
                  
                  if (theme === 'light') {
                    document.documentElement.classList.remove('dark');
                    document.documentElement.classList.add('light-theme');
                    document.documentElement.style.backgroundColor = '#f8fafc';
                    document.documentElement.style.colorScheme = 'light';
                  } else {
                    document.documentElement.classList.remove('light-theme');
                    document.documentElement.classList.add('dark');
                    document.documentElement.style.backgroundColor = '#07090e';
                    document.documentElement.style.colorScheme = 'dark';
                  }
                } catch (e) {}
              })();
            `
          }}
        />
        <meta httpEquiv="X-Content-Type-Options" content="nosniff" />
        <meta httpEquiv="X-XSS-Protection" content="1; mode=block" />
        <meta name="referrer" content="strict-origin-when-cross-origin" />
        <meta httpEquiv="Permissions-Policy" content="camera=(), microphone=(), geolocation=(), payment=()" />
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body className="min-h-screen flex flex-col bg-[#07090e] text-gray-100 antialiased selection:bg-[#00e5ff]/30 selection:text-[#00e5ff]" style={{ backgroundColor: '#07090e' }} suppressHydrationWarning>
        <EcosystemProvider>
          <Navbar />
          <SidebarNavigation />
          <CommandPalette />
          <WelcomeModal />
          <ErrorReportModal />
          <main className="flex-1">
            {children}
          </main>

          <AiChatWidget />
          <CookieConsent />
          <Footer />
          <Analytics />
        </EcosystemProvider>
      </body>
    </html>
  );
}
