import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";
import { AppHeader } from "@/components/shared/AppHeader";

const geistSans = Geist({
  variable: "--font-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AutiScreen - Pre-depistage du developpement de l'enfant",
  description:
    "Outil de pre-depistage en ligne des troubles du spectre autistique. Evaluation gratuite et confidentielle.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr" className={`${geistSans.variable} h-full antialiased`}>
      <body className="flex min-h-full flex-col bg-gray-50/50 font-sans">
        <AppHeader />
        <main className="flex-1">{children}</main>
        <footer className="border-t border-gray-100 bg-white py-6 text-center text-sm text-gray-400">
          AutiScreen &middot; Outil de pre-depistage &middot; Ce service ne
          constitue pas un diagnostic medical.
        </footer>
      </body>
    </html>
  );
}
