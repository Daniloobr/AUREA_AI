'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Sparkles } from 'lucide-react';

export function Footer() {
  const currentYear = new Date().getFullYear();
  const [logoError, setLogoError] = useState(false);

  return (
    <footer className="w-full py-16 px-6 border-t border-white/8 bg-[#0A0A0A]">
      <div className="max-w-[1400px] mx-auto">

        {/* Top row */}
        <div className="flex flex-col lg:flex-row justify-between items-start gap-12 mb-16">

          {/* Brand */}
          <div className="flex flex-col gap-4 max-w-xs">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center">
                {!logoError ? (
                  <img
                    src="/images/logo-aurea.png"
                    alt="AureaIA Logo"
                    className="w-full h-full object-contain"
                    onError={() => setLogoError(true)}
                  />
                ) : (
                  <div className="w-full h-full rounded-lg bg-[#748FCC] flex items-center justify-center">
                    <Sparkles className="w-4 h-4 text-[#F5F5F7]" />
                  </div>
                )}
              </div>
              <span className="font-serif font-bold text-lg tracking-widest text-[#F5F5F7] uppercase">AureaIA</span>
            </div>
            <p className="text-[12px] text-[#B8BCC4] font-light leading-relaxed">
              O futuro da fotografia para gestantes.<br />
              A tecnologia a serviço da sua história.
            </p>
          </div>

          {/* Navigation columns */}
          <div className="flex flex-col sm:flex-row gap-12 lg:gap-20">
            <div className="flex flex-col gap-4">
              <span className="text-[10px] font-bold uppercase tracking-[0.3em] text-white/40">Navegação</span>
              <nav className="flex flex-col gap-3">
                <Link href="/" className="text-[13px] text-[#B8BCC4] hover:text-[#748FCC] transition-colors">Início</Link>
                <Link href="#como-funciona" className="text-[13px] text-[#B8BCC4] hover:text-[#748FCC] transition-colors">Como Funciona</Link>
                <Link href="#exemplos" className="text-[13px] text-[#B8BCC4] hover:text-[#748FCC] transition-colors">Exemplos</Link>
                <Link href="/credits" className="text-[13px] text-[#B8BCC4] hover:text-[#748FCC] transition-colors">Planos</Link>
                <Link href="#sobre" className="text-[13px] text-[#B8BCC4] hover:text-[#748FCC] transition-colors">Sobre</Link>
                <Link href="/help" className="text-[13px] text-[#B8BCC4] hover:text-[#748FCC] transition-colors">Contato</Link>
              </nav>
            </div>

            <div className="flex flex-col gap-4">
              <span className="text-[10px] font-bold uppercase tracking-[0.3em] text-white/40">Legal</span>
              <nav className="flex flex-col gap-3">
                <Link href="/terms" className="text-[13px] text-[#B8BCC4] hover:text-[#748FCC] transition-colors">Termos de Uso</Link>
                <Link href="/privacy" className="text-[13px] text-[#B8BCC4] hover:text-[#748FCC] transition-colors">Política de Privacidade</Link>
                <Link href="/privacy" className="text-[13px] text-[#B8BCC4] hover:text-[#748FCC] transition-colors">Política de Reembolso</Link>
              </nav>
            </div>

            <div className="flex flex-col gap-4">
              <span className="text-[10px] font-bold uppercase tracking-[0.3em] text-white/40">Siga-nos</span>
              <div className="flex items-center gap-4">
                <a href="https://www.instagram.com/aurea.iaoficial/" target="_blank" rel="noopener noreferrer" className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center text-[#B8BCC4] hover:text-[#748FCC] hover:border-[#748FCC]/40 transition-all" aria-label="Instagram">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z" /></svg>
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom row */}
        <div className="border-t border-white/5 pt-8 flex flex-col sm:flex-row justify-between items-center gap-4">
          <p className="text-[11px] text-[#B8BCC4]/60 font-light">
            © {currentYear} AureaIA™. Todos os direitos reservados.
          </p>
        </div>

      </div>
    </footer>
  );
}
