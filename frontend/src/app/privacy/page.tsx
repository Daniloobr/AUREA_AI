'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Shield, ArrowLeft, FileText, Lock, Scale } from 'lucide-react';

export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-onyx-950 text-zinc-300 font-sans selection:bg-brand-purple selection:text-white">
      <div className="max-w-4xl mx-auto px-6 py-20">
        <Link href="/register" className="inline-flex items-center gap-2 text-brand-lavender hover:text-white transition-colors mb-12 group">
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
          Voltar para o cadastro
        </Link>

        <header className="space-y-4 mb-16 text-center lg:text-left">
          <div className="w-12 h-12 rounded-2xl bg-brand-purple/10 flex items-center justify-center text-brand-purple mb-6 mx-auto lg:mx-0">
            <Shield className="w-6 h-6" />
          </div>
          <h1 className="text-4xl md:text-5xl font-display font-bold text-white tracking-tighter">Política de <span className="text-gradient">Privacidade</span></h1>
          <p className="text-zinc-500 font-light">Última atualização: 13 de Maio de 2026</p>
        </header>

        <div className="space-y-12 leading-relaxed text-lg">
          <section className="space-y-4">
            <h2 className="text-2xl font-display font-bold text-white flex items-center gap-3">
              <Lock className="w-5 h-5 text-brand-purple" /> 1. Compromisso com sua Identidade
            </h2>
            <p>
              No <strong>Lumière Studios</strong>, a privacidade das nossas clientes e de seus bebês é nossa prioridade absoluta. Esta política descreve como tratamos seus dados biométricos (fotos de rosto) e informações pessoais em conformidade com a <strong>LGPD (Lei Geral de Proteção de Dados)</strong>.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-display font-bold text-white flex items-center gap-3">
              <FileText className="w-5 h-5 text-brand-purple" /> 2. Coleta de Dados e Finalidade
            </h2>
            <p>
              Coletamos suas fotos de referência exclusivamente para a finalidade de <strong>treinamento temporário do modelo de IA</strong> para gerar seus retratos. Estes dados não são utilizados para nenhum outro fim, não são vendidos e não são compartilhados com terceiros para fins publicitários.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-display font-bold text-white flex items-center gap-3">
              <Scale className="w-5 h-5 text-brand-purple" /> 3. Retenção de Dados (Política de 24h)
            </h2>
            <div className="bg-white/5 border border-white/10 p-6 rounded-3xl space-y-4">
              <p className="font-bold text-white">Segurança por design:</p>
              <ul className="list-disc list-inside space-y-2 text-zinc-400">
                <li>As fotos originais enviadas por você são deletadas permanentemente do nosso servidor e da nuvem após o processamento.</li>
                <li>As fotos geradas pela IA ficam disponíveis em sua galeria por apenas <strong>24 horas</strong>.</li>
                <li>Após esse período, nosso sistema de limpeza automática remove todos os arquivos de mídia permanentemente, mantendo apenas o registro da transação em sua conta.</li>
              </ul>
            </div>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-display font-bold text-white">4. Seus Direitos</h2>
            <p>
              Conforme a LGPD, você tem o direito de acessar, corrigir ou solicitar a exclusão de seus dados a qualquer momento através das configurações de sua conta ou enviando um e-mail para nossa equipe de suporte.
            </p>
          </section>

          <footer className="pt-12 border-t border-white/5 text-sm text-zinc-500">
            <p>© 2026 Lumière Studios — Tecnologia de IA para Maternidade. Todos os direitos reservados.</p>
          </footer>
        </div>
      </div>
    </div>
  );
}
