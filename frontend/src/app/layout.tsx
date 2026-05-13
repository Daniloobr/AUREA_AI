import type { Metadata } from "next";
import { Inter, Sora } from "next/font/google";
import Link from "next/link";
import "./globals.css";
import { Sparkles, Crown, LogOut } from "lucide-react";

import { AuthProvider } from "@/contexts/AuthContext";

// Fontes Premium solicitadas
const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const sora = Sora({
  variable: "--font-sora",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Lumière Maternity | Alta Costura em IA",
  description: "Ensaios fotográficos cinematográficos de maternidade.",
};

import { Navbar } from "@/components/Navbar";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" className="scroll-smooth">
      <body
        className={`${inter.variable} ${sora.variable} antialiased bg-onyx-950 text-zinc-100 min-h-screen flex flex-col font-sans selection:bg-brand-purple selection:text-white`}
      >
        <AuthProvider>
          <Navbar />
          {/* Content Wrapper */}
          <main className="flex-1 w-full pt-16">
            {children}
          </main>

          {/* Footer */}
          <footer className="w-full py-10 px-6 md:px-10 border-t border-white/5 bg-onyx-950">
            <div className="max-w-[1400px] mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-brand-lavender" />
                <p className="text-xs font-medium text-zinc-500 font-display tracking-widest uppercase">
                  LUMIÈRE STUDIOS © 2026
                </p>
              </div>
              <div className="flex items-center gap-6">
                <a href="#" className="text-xs text-zinc-500 hover:text-white transition-colors">Termos</a>
                <a href="#" className="text-xs text-zinc-500 hover:text-white transition-colors">Privacidade</a>
                <a href="#" className="text-xs text-zinc-500 hover:text-white transition-colors">Instagram</a>
              </div>
            </div>
          </footer>
        </AuthProvider>
      </body>
    </html>
  );
}
