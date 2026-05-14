'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowLeft, BookOpen, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function TermsOfUse() {
  return (
    <div className="min-h-screen bg-[#0A0A0A] text-[#F5F5F7] font-sans selection:bg-[#748FCC] selection:text-white">
      {/* Texture Overlay */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] z-0 texture-linen" />

      <div className="max-w-4xl mx-auto px-6 py-20 relative z-10">
        <Link href="/register" className="inline-flex items-center gap-2 text-[#748FCC] hover:text-[#5F7DB8] transition-colors mb-12 group font-bold uppercase text-[10px] tracking-widest">
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
          Voltar para o cadastro
        </Link>

        <header className="space-y-4 mb-16 text-center lg:text-left">
          <div className="w-16 h-16 rounded-full bg-[#748FCC]/10 flex items-center justify-center text-[#748FCC] mb-6 mx-auto lg:mx-0 shadow-sm">
            <BookOpen className="w-8 h-8" />
          </div>
          <h1 className="text-4xl md:text-5xl font-serif font-medium text-[#F5F5F7] tracking-tight">Termos de <span className="italic text-[#748FCC]">Uso</span></h1>
          <p className="text-[#B8BCC4] font-bold text-[10px] uppercase tracking-[0.2em]">Última atualização: 14 de Maio de 2026</p>
        </header>

        <div className="space-y-12 leading-relaxed text-base bg-[#121417] backdrop-blur-md p-10 md:p-16 rounded-[50px] border border-[#1F2329] shadow-sm">
          <section className="space-y-4">
            <h2 className="text-2xl font-serif font-medium text-[#F5F5F7] flex items-center gap-3">
              <CheckCircle2 className="w-5 h-5 text-[#748FCC]" /> 1. Aceite dos Termos
            </h2>
            <p className="text-[#B8BCC4]">
              Ao acessar e utilizar a <strong>AureaIA</strong>, você concorda em cumprir estes termos. Nosso serviço utiliza inteligência artificial generativa de ponta para criar retratos artísticos baseados em fotos enviadas pelo usuário, visando a celebração da maternidade.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-serif font-medium text-[#F5F5F7] flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 text-[#748FCC]" /> 2. Uso Responsável
            </h2>
            <p className="text-[#B8BCC4]">
              Você declara ser a proprietária das fotos enviadas ou possuir autorização expressa. É estritamente proibido enviar fotos de terceiros sem consentimento, ou qualquer conteúdo que fira a dignidade humana. A AureaIA preza pela elegância e respeito em todas as suas criações.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-serif font-medium text-[#F5F5F7]">3. Créditos e Investimento</h2>
            <p className="text-[#B8BCC4]">
              O sistema funciona através de créditos virtuais. Cada criação de ensaio consome <strong>25 créditos</strong>. Dada a natureza do processamento imediato de alta performance, créditos utilizados não são passíveis de reembolso, garantindo a reserva dos recursos computacionais para sua arte.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-serif font-medium text-[#F5F5F7]">4. Propriedade Artística</h2>
            <p className="text-[#B8BCC4]">
              Você detém os direitos de uso sobre as imagens geradas pela nossa IA para fins pessoais e compartilhamento social. A AureaIA atua como seu estúdio digital, provendo a tecnologia para que sua beleza seja eternizada.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-serif font-medium text-[#F5F5F7]">5. Natureza da Inteligência Artificial</h2>
            <p className="text-[#B8BCC4]">
              A IA é uma ferramenta de interpretação artística. Ao utilizar o serviço, você compreende que os resultados são criações algorítmicas que visam a estética editorial, podendo apresentar variações artísticas únicas em cada geração.
            </p>
          </section>

          <footer className="pt-12 border-t border-white/5 text-[10px] font-bold text-[#B8BCC4]/30 uppercase tracking-widest text-center md:text-left">
            <p>© 2026 AureaIA — Eternizando a jornada da vida através da arte.</p>
          </footer>
        </div>
      </div>
    </div>
  );
}
