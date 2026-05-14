import React from 'react';
import Link from 'next/link';
import { Sparkles } from 'lucide-react';

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="w-full py-16 px-6 border-t border-white/8 bg-[#0A0A0A]">
      <div className="max-w-[1400px] mx-auto">
        
        {/* Top row */}
        <div className="flex flex-col lg:flex-row justify-between items-start gap-12 mb-16">
          
          {/* Brand */}
          <div className="flex flex-col gap-4 max-w-xs">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-[#748FCC] flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-[#F5F5F7]" />
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
                <Link href="mailto:ola@aureaia.com" className="text-[13px] text-[#B8BCC4] hover:text-[#748FCC] transition-colors">Contato</Link>
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
                {/* Instagram */}
                <a href="#" className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center text-[#B8BCC4] hover:text-[#748FCC] hover:border-[#748FCC]/40 transition-all" aria-label="Instagram">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>
                </a>
                {/* TikTok */}
                <a href="#" className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center text-[#B8BCC4] hover:text-[#748FCC] hover:border-[#748FCC]/40 transition-all" aria-label="TikTok">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1v-3.5a6.37 6.37 0 00-.79-.05A6.34 6.34 0 003.15 15.2a6.34 6.34 0 006.34 6.34 6.34 6.34 0 006.34-6.34V8.92a8.27 8.27 0 004.76 1.5V7a4.84 4.84 0 01-1-.31z"/></svg>
                </a>
                {/* Pinterest */}
                <a href="#" className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center text-[#B8BCC4] hover:text-[#748FCC] hover:border-[#748FCC]/40 transition-all" aria-label="Pinterest">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0C5.373 0 0 5.372 0 12c0 5.084 3.163 9.426 7.627 11.174-.105-.949-.2-2.405.042-3.441.218-.937 1.407-5.965 1.407-5.965s-.359-.719-.359-1.782c0-1.668.967-2.914 2.171-2.914 1.023 0 1.518.769 1.518 1.69 0 1.029-.655 2.568-.994 3.995-.283 1.194.599 2.169 1.777 2.169 2.133 0 3.772-2.249 3.772-5.495 0-2.873-2.064-4.882-5.012-4.882-3.414 0-5.418 2.561-5.418 5.207 0 1.031.397 2.138.893 2.738a.36.36 0 01.083.345l-.333 1.36c-.053.22-.174.267-.402.161-1.499-.698-2.436-2.889-2.436-4.649 0-3.785 2.75-7.262 7.929-7.262 4.163 0 7.398 2.967 7.398 6.931 0 4.136-2.607 7.464-6.227 7.464-1.216 0-2.359-.631-2.75-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24 12 24c6.627 0 12-5.373 12-12 0-6.628-5.373-12-12-12z"/></svg>
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
