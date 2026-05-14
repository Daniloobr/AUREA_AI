'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Mail, ChevronDown, Sparkles, MessageCircle, Clock, Shield } from 'lucide-react';
import { Card } from '@/components/ui/Card';

const FAQS = [
  {
    q: "Como o AureaIA cria as imagens?",
    a: "Utilizamos uma inteligência artística de última geração, treinada para compreender a luz, a forma e a emoção da maternidade. O processo combina suas fotos reais com cenários digitais de luxo, resultando em obras que capturam a essência única de cada mulher."
  },
  {
    q: "As fotos são reais ou geradas por inteligência artificial?",
    a: "As fotos são criadas por nossa IA editorial, mas preservam seus traços e essência reais. O resultado é um retrato artístico que parece ter sido capturado em um estúdio profissional de alto padrão."
  },
  {
    q: "Quanto tempo leva para minha obra ficar pronta?",
    a: "Normalmente, seu ensaio está pronto em cerca de 1 a 2 minutos. Você poderá acompanhar o progresso em tempo real em sua Galeria Privada."
  },
  {
    q: "Como funciona o sistema de créditos?",
    a: "Cada criação de ensaio completo consome 25 créditos. Os créditos são vitalícios — nunca expiram. Você pode adquiri-los em nossa página Adquirir Créditos e usá-los no momento que desejar."
  },
  {
    q: "Posso compartilhar ou imprimir minhas obras?",
    a: "Absolutamente. Ao criar suas imagens, você detém o direito de uso pessoal completo: compartilhar, imprimir, emoldurar — eternize sua memória da forma que desejar."
  },
  {
    q: "Meus dados e fotos estão seguros?",
    a: "Sua privacidade é nosso compromisso de luxo. Todas as fotos de referência são processadas em ambiente criptografado e removidas de nossos servidores após a geração. Nenhuma imagem sua é armazenada sem sua autorização explícita."
  },
];

export default function HelpPage() {
  return (
    <div className="min-h-screen bg-[#0A0A0A] text-[#F5F5F7] pt-24 pb-32 px-6">
      <div className="max-w-[900px] mx-auto space-y-24">
        
        {/* ── Cabeçalho ──────────────────────────────────────────────── */}
        <motion.header
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center space-y-8"
        >
          <div className="inline-flex items-center gap-3 px-6 py-2 rounded-full bg-[#121417] border border-[#1F2329] text-[#B8BCC4] font-bold text-[10px] tracking-[0.4em] uppercase">
            <Sparkles className="w-4 h-4 text-[#748FCC]" /> AureaIA™ • Suporte & Ajuda
          </div>
          <h1 className="text-5xl md:text-7xl font-serif font-medium tracking-tight leading-tight text-[#F5F5F7]">
            Estamos aqui<br /><span className="italic text-[#748FCC]/60">por você.</span>
          </h1>
          <p className="text-[#B8BCC4] font-light text-xl max-w-xl mx-auto leading-relaxed">
            Seu momento único merece uma experiência impecável — do início ao fim. 
            Se tiver qualquer dúvida, nossa equipe está a uma mensagem de distância.
          </p>
        </motion.header>

        {/* ── Cards de suporte ─────────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 sm:grid-cols-3 gap-6"
        >
          {/* E-mail */}
          <Card className="p-8 text-center space-y-5 bg-[#121417] border border-[#1F2329] hover:border-[#748FCC]/30 transition-all">
            <div className="w-14 h-14 rounded-2xl bg-[#748FCC]/10 flex items-center justify-center mx-auto">
              <Mail className="w-7 h-7 text-[#748FCC]" />
            </div>
            <div className="space-y-2">
              <h3 className="text-base font-bold uppercase tracking-[0.2em] text-[#F5F5F7]">E-mail</h3>
              <p className="text-[#B8BCC4] font-light text-sm">Resposta em até 24 horas</p>
            </div>
            <a 
              href="mailto:ola@aureaia.com" 
              className="text-base font-medium text-[#F5F5F7] hover:text-[#748FCC] transition-colors"
            >
              ola@aureaia.com
            </a>
          </Card>

          {/* Tempo de resposta */}
          <Card className="p-8 text-center space-y-5 bg-[#121417] border border-[#1F2329] hover:border-[#748FCC]/30 transition-all">
            <div className="w-14 h-14 rounded-2xl bg-[#748FCC]/10 flex items-center justify-center mx-auto">
              <Clock className="w-7 h-7 text-[#748FCC]" />
            </div>
            <div className="space-y-2">
              <h3 className="text-base font-bold uppercase tracking-[0.2em] text-[#F5F5F7]">Disponibilidade</h3>
              <p className="text-[#B8BCC4] font-light text-sm">Segunda a Sábado</p>
            </div>
            <p className="text-base font-medium text-[#F5F5F7]">9h às 18h (BRT)</p>
          </Card>

          {/* Privacidade */}
          <Card className="p-8 text-center space-y-5 bg-[#121417] border border-[#1F2329] hover:border-[#748FCC]/30 transition-all">
            <div className="w-14 h-14 rounded-2xl bg-[#748FCC]/10 flex items-center justify-center mx-auto">
              <Shield className="w-7 h-7 text-[#748FCC]" />
            </div>
            <div className="space-y-2">
              <h3 className="text-base font-bold uppercase tracking-[0.2em] text-[#F5F5F7]">Privacidade</h3>
              <p className="text-[#B8BCC4] font-light text-sm">Seus dados protegidos</p>
            </div>
            <p className="text-base font-medium text-[#F5F5F7]">LGPD Compliant</p>
          </Card>
        </motion.div>

        {/* ── Perguntas frequentes ─────────────────────────────────────── */}
        <motion.section
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="space-y-10"
        >
          <div className="space-y-4">
            <h2 className="text-4xl md:text-5xl font-serif font-medium tracking-tight text-[#F5F5F7]">Dúvidas Frequentes.</h2>
            <div className="h-0.5 w-16 bg-[#748FCC] rounded-full" />
          </div>

          <div className="space-y-2">
            {FAQS.map((faq, i) => (
              <details key={i} className="group border-b border-[#1F2329]">
                <summary className="flex items-center justify-between py-8 cursor-pointer list-none hover:text-[#748FCC] transition-colors">
                  <span className="text-xl font-light pr-8 text-[#F5F5F7]">{faq.q}</span>
                  <ChevronDown className="w-5 h-5 shrink-0 transition-transform duration-300 group-open:rotate-180 text-[#B8BCC4]" />
                </summary>
                <div className="pb-8 text-[#B8BCC4] font-light leading-relaxed text-lg animate-fade-in">
                  {faq.a}
                </div>
              </details>
            ))}
          </div>
        </motion.section>

        {/* ── CTA final ────────────────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-center space-y-6 pt-8 border-t border-[#1F2329]"
        >
          <p className="text-[#B8BCC4] font-light">
            Sua dúvida não está aqui? Fale diretamente com nossa equipe.
          </p>
          <a
            href="mailto:ola@aureaia.com"
            className="inline-flex items-center gap-3 bg-[#748FCC] text-[#F5F5F7] rounded-full px-12 py-5 font-bold tracking-[0.1em] hover:bg-[#5F7DB8] transition-all shadow-xl shadow-[#748FCC]/20"
          >
            <MessageCircle className="w-5 h-5" />
            Falar com o Suporte
          </a>
          
          {/* Assinatura */}
          <div className="pt-12 opacity-20">
            <Sparkles className="w-6 h-6 mx-auto text-[#748FCC]" />
          </div>
        </motion.div>

      </div>
    </div>
  );
}
