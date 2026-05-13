'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowLeft, BookOpen, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function TermsOfUse() {
  return (
    <div className="min-h-screen bg-onyx-950 text-zinc-300 font-sans selection:bg-brand-purple selection:text-white">
      <div className="max-w-4xl mx-auto px-6 py-20">
        <Link href="/register" className="inline-flex items-center gap-2 text-brand-lavender hover:text-white transition-colors mb-12 group">
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
          Voltar para o cadastro
        </Link>

        <header className="space-y-4 mb-16 text-center lg:text-left">
          <div className="w-12 h-12 rounded-2xl bg-brand-purple/10 flex items-center justify-center text-brand-purple mb-6 mx-auto lg:mx-0">
            <BookOpen className="w-6 h-6" />
          </div>
          <h1 className="text-4xl md:text-5xl font-display font-bold text-white tracking-tighter">Termos de <span className="text-gradient">Uso</span></h1>
          <p className="text-zinc-500 font-light">Válido a partir de: 13 de Maio de 2026</p>
        </header>

        <div className="space-y-12 leading-relaxed text-lg">
          <section className="space-y-4">
            <h2 className="text-2xl font-display font-bold text-white flex items-center gap-3">
              <CheckCircle2 className="w-5 h-5 text-brand-purple" /> 1. Aceite dos Termos
            </h2>
            <p>
              Ao acessar e utilizar o <strong>Lumière Studios</strong>, você concorda em cumprir estes termos. Nosso serviço utiliza inteligência artificial generativa para criar retratos artísticos baseados em fotos enviadas pelo usuário.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-display font-bold text-white flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 text-brand-purple" /> 2. Uso Responsável
            </h2>
            <p>
              Você declara ser a proprietária das fotos enviadas ou possuir autorização expressa para utilizá-las. É estritamente proibido enviar fotos de terceiros sem consentimento, imagens de nudez, violência ou qualquer conteúdo ilegal.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-display font-bold text-white">3. Créditos e Pagamentos</h2>
            <p>
              O sistema funciona através de créditos virtuais (moedas). Cada geração de ensaio consome <strong>25 créditos</strong>. Créditos adquiridos não são reembolsáveis após o uso da ferramenta de geração, dada a natureza do custo de processamento computacional imediato da IA.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-display font-bold text-white">4. Propriedade Intelectual</h2>
            <p>
              Você detém os direitos de uso sobre as imagens geradas pela nossa IA para fins pessoais e de mídia social. No entanto, o Lumière Studios reserva-se o direito de remover qualquer conteúdo que viole nossas diretrizes éticas.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-display font-bold text-white">5. Limitação de Responsabilidade</h2>
            <p>
              A IA pode, ocasionalmente, gerar artefatos visuais ou interpretações artísticas inesperadas. Ao utilizar o serviço, você compreende que os resultados são gerados de forma algorítmica e podem variar em fidelidade.
            </p>
          </section>

          <footer className="pt-12 border-t border-white/5 text-sm text-zinc-500">
            <p>© 2026 Lumière Studios — Transformando momentos em arte eterna.</p>
          </footer>
        </div>
      </div>
    </div>
  );
}
