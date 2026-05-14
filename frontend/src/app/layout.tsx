import type { Metadata } from "next";
import { Cormorant_Garamond, Montserrat } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/contexts/AuthContext";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";

// ─── Tipografia ───────────────────────────────────────────────────────────────
// Cormorant Garamond: títulos serifados elegantes
const cormorant = Cormorant_Garamond({
  subsets: ["latin"],
  variable: "--font-cormorant",
  weight: ["300", "400", "500", "600", "700"],
  display: "swap",
});

// Montserrat: corpo de texto sans-serif refinado
const montserrat = Montserrat({
  subsets: ["latin"],
  variable: "--font-montserrat",
  weight: ["300", "400", "500", "600", "700"],
  display: "swap",
});

// ─── SEO ──────────────────────────────────────────────────────────────────────
export const metadata: Metadata = {
  title: "AureaIA™ | Seu ensaio de maternidade. Em casa. Em minutos.",
  description:
    "Crie sua obra-prima. Tecnologia de estúdio profissional ao alcance de todas as famílias. Seu momento único, eternizado em alta definição — sem sair de casa.",
  keywords: [
    "ensaio de maternidade",
    "fotos de gestante",
    "inteligência artificial",
    "estúdio virtual",
    "AureaIA",
    "obra prima",
  ],
  openGraph: {
    title: "AureaIA™ — Seu momento único, eternizado.",
    description:
      "Tecnologia de estúdio profissional. Direção de arte digital. Resultados que eternizam sua jornada única.",
    siteName: "AureaIA",
    locale: "pt_BR",
    type: "website",
  },
  robots: {
    index: true,
    follow: true,
  },
};

// ─── Layout raiz ─────────────────────────────────────────────────────────────
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" className="scroll-smooth">
      <body
        className={`${montserrat.variable} ${cormorant.variable} antialiased bg-black text-white min-h-screen flex flex-col font-sans`}
      >
        <AuthProvider>
          <Navbar />
          <main className="flex-1 w-full pt-16">
            {children}
          </main>
          <Footer />
        </AuthProvider>
      </body>
    </html>
  );
}
