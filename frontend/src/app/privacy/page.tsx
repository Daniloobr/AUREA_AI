'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Shield, ArrowLeft, FileText, Lock, Scale } from 'lucide-react';

export default function PrivacyPolicy() {
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
            <Shield className="w-8 h-8" />
          </div>
          <h1 className="text-4xl md:text-5xl font-serif font-medium text-[#F5F5F7] tracking-tight">Política de <span className="italic text-[#748FCC]">Privacidade</span></h1>
          <p className="text-[#B8BCC4] font-bold text-[10px] uppercase tracking-[0.2em]">Última atualização: 14 de Maio de 2026</p>
        </header>

        <div className="space-y-12 leading-relaxed text-base bg-[#121417] backdrop-blur-md p-10 md:p-16 rounded-[50px] border border-[#1F2329] shadow-sm">
          <section className="space-y-4">
            <h2 className="text-2xl font-serif font-medium text-[#F5F5F7] flex items-center gap-3">
              <Lock className="w-5 h-5 text-[#748FCC]" /> 1. Compromisso com sua Identidade
            </h2>
            <p className="text-[#B8BCC4]">
              Na <strong>AureaIA</strong>, a privacidade das nossas clientes e de seus bebês é nossa prioridade absoluta. Esta política descreve como tratamos seus dados e imagens em conformidade com a <strong>LGPD (Lei Geral de Proteção de Dados)</strong>, garantindo um ambiente seguro e sofisticado.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-serif font-medium text-[#F5F5F7] flex items-center gap-3">
              <FileText className="w-5 h-5 text-[#748FCC]" /> 2. Coleta de Dados e Finalidade
            </h2>
            <p className="text-[#B8BCC4]">
              Coletamos suas fotos de referência exclusivamente para a finalidade de <strong>criação artística da sua obra-prima</strong>. Suas fotos originais são tratadas como segredos de estado: servem apenas para que nossa IA aprenda seus traços únicos e são descartadas imediatamente após o processamento.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-serif font-medium text-[#F5F5F7] flex items-center gap-3">
              <Scale className="w-5 h-5 text-[#748FCC]" /> 3. Segurança por Design
            </h2>
            <div className="bg-[#748FCC]/5 border border-[#748FCC]/10 p-8 rounded-3xl space-y-4">
              <p className="font-bold text-[#F5F5F7]/80 text-sm uppercase tracking-widest">Nossa promessa de proteção:</p>
              <ul className="list-disc list-inside space-y-2 text-[#B8BCC4]/60 text-sm">
                <li>As fotos originais são deletadas permanentemente após a geração das imagens.</li>
                <li>As fotos geradas pela IA ficam em sua galeria particular criptografada.</li>
                <li>Você tem total controle sobre seus arquivos, podendo deletá-los permanentemente a qualquer momento.</li>
                <li>Não compartilhamos seus dados artísticos com terceiros para fins comerciais.</li>
              </ul>
            </div>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-serif font-medium text-[#F5F5F7]">4. Seus Direitos</h2>
            <p className="text-[#B8BCC4]">
              Conforme a LGPD, você tem o direito de acessar, corrigir ou solicitar a exclusão de seus dados. A AureaIA oferece total transparência, permitindo que você gerencie sua presença digital em nosso estúdio com facilidade e elegância.
            </p>
          </section>

          <footer className="pt-12 border-t border-white/5 text-[10px] font-bold text-[#B8BCC4]/30 uppercase tracking-widest text-center md:text-left">
            <p>© 2026 AureaIA — Tecnologia de Luxo para Maternidade. Todos os direitos reservados.</p>
          </footer>
        </div>
      </div>
    </div>
  );
}
