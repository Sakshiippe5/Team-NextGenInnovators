import AppBar from "@/components/app/appbar";
import Providers from "@/components/app/providers";
import type { Metadata, Viewport } from "next";
import { Nunito } from "next/font/google";
import NextTopLoader from "nextjs-toploader";
import "./globals.css";

const nunito = Nunito({ subsets: ["latin"] });

export const metadata: Metadata = {
  metadataBase: new URL("https://www.airoadmapgenerator.com/"),
  title: "AI Roadmap Generator",
  description: "Generate your roadmaps with AI.",
  openGraph: {
    url: "https://www.airoadmapgenerator.com/",

    images: "/opengraph-image.png",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full">
      <body className={`${nunito.className} min-h-full antialiased`}>
        <Providers>
          <NextTopLoader showSpinner={false} color="black" />
          <AppBar />
          {children}
        </Providers>
      </body>
    </html>
  );
}
