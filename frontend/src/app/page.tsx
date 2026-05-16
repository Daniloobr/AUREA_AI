'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import {
  Sparkles,
  Camera,
  Image as ImageIcon,
  Heart,
  ChevronDown,
  Star,
  ShieldCheck,
  ArrowRight,
  Gem,
  Clock,
  Download,
  Users,
  Award,
  CheckCircle2,
  Zap,
  Play,
  Eye,
  Lock,
  Bolt,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

/* ═══════════════════════════════════════════════════════════════════════════
   DADOS
   ═══════════════════════════════════════════════════════════════════════════ */

const howItWorks = [
  {
    step: '01',
    title: 'Envie suas fotos',
    description: 'Três fotos simples do seu celular. Sem precisar de estúdio, fotógrafo ou sair de casa.',
    icon: Camera,
  },
  {
    step: '02',
    title: 'Escolha o cenário',
    description: 'Selecione entre coleções editoriais — do minimalismo clássico ao luxo Vogue.',
    icon: Sparkles,
  },
  {
    step: '03',
    title: 'Receba sua obra-prima',
    description: 'Em minutos, seu ensaio profissional está pronto para download em altíssima resolução.',
    icon: ImageIcon,
  },
];

const features = [
  {
    icon: Sparkles,
    title: 'Imagens Realistas',
    desc: 'IA treinada para gerar fotos com qualidade de estúdio.',
  },
  {
    icon: Eye,
    title: 'Estilos Exclusivos',
    desc: 'Cenários, looks e atmosferas personalizados para você.',
  },
  {
    icon: Lock,
    title: 'Privacidade Total',
    desc: 'Seus dados e imagens são 100% seguros.',
  },
  {
    icon: Zap,
    title: 'Entrega Rápida',
    desc: 'Seu ensaio pronto em até 24 horas.',
  },
];

const avatarUrls = [
  'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=80&h=80&fit=crop&crop=face',
  'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=80&h=80&fit=crop&crop=face',
  'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=80&h=80&fit=crop&crop=face',
  'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=80&h=80&fit=crop&crop=face',
];

const testimonials = [
  {
    text: 'Eu tava com 35 semanas, super inchada, sem ânimo pra nada. Fiz só pra testar e gente… chorei horrores. Ficou lindo demais, nem parece eu!',
    name: 'Mariana S.',
    detail: 'São Paulo · 35 semanas',
    stars: 5,
    avatar: 'https://images.unsplash.com/photo-1580489944761-15a19d654956?w=96&h=96&fit=crop&crop=face',
  },
  {
    text: 'Meu marido que fez de surpresa pra mim. Quando abri o link e vi as fotos, não consegui parar de chorar. Melhor presente da gestação.',
    name: 'Beatriz L.',
    detail: 'Rio de Janeiro · 32 semanas',
    stars: 5,
    avatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=96&h=96&fit=crop&crop=face',
  },
  {
    text: 'Eu estava exausta nessa reta final e não tinha energia para um estúdio. Fiz pela AureaIA e me senti a mulher mais linda do mundo. As fotos ficaram com uma luz divina... é emocionante se ver com tanto brilho e sofisticação.',
    name: 'Amanda C.',
    detail: 'Belo Horizonte · Mãe do Theo',
    stars: 5,
    avatar: 'https://images.unsplash.com/photo-1607746882042-944635dfe10e?w=96&h=96&fit=crop&crop=face',
  },
];

const galleryImages = [
  { src: '/landing/gallery1.png', alt: 'Ensaio maternidade estúdio lunar' },
  { src: '/ensaios/floral.png', alt: 'Ensaio maternidade floral' },
  { src: '/landing/gallery3.png', alt: 'Ensaio maternidade clássico' },
  { src: '/landing/gallery4.png', alt: 'Ensaio maternidade editorial' },
  { src: '/landing/gallery2.png', alt: 'Ensaio maternidade azul' },
  { src: '/ensaios/editorial.png', alt: 'Ensaio maternidade editorial luxo' },
];

/* ═══════════════════════════════════════════════════════════════════════════
   COMPONENTE PRINCIPAL
   ═══════════════════════════════════════════════════════════════════════════ */

export default function LandingPage() {
  return (
    <div className="bg-[#0A0A0A] min-h-screen text-[#F5F5F7] overflow-hidden">

      {/* ══════════════════════════════════════════════════════════════
          HERO — Layout split com imagem à direita (como na referência)
      ══════════════════════════════════════════════════════════════ */}
      <section id="hero" className="relative min-h-[100vh] flex items-center overflow-hidden">
        {/* Background subtle glow */}
        <div className="absolute top-1/2 left-1/4 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-[#748FCC]/8 blur-[180px] rounded-full pointer-events-none" />

        <div className="max-w-[1400px] mx-auto w-full px-6 md:px-10 grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-4 items-center relative z-10">
          {/* Left — Text content */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, ease: 'easeOut' }}
            className="space-y-8 py-12 lg:py-0"
          >
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-[#748FCC]/30 text-[#F5F5F7] text-[11px] font-semibold tracking-[0.15em] uppercase"
            >
              Ensaios para gestantes com inteligência artificial
            </motion.div>

            {/* Título */}
            <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-[5.5rem] font-serif font-semibold tracking-tight leading-[1.0]">
              Sua essência.
              <br />
              Eternizada com
              <br />
              <span className="bg-gradient-to-r from-[#748FCC] to-[#9FB3E6] bg-clip-text text-transparent">
                tecnologia.
              </span>
            </h1>

            {/* Subtítulo */}
            <p className="text-lg sm:text-xl text-[#B8BCC4] font-light max-w-lg leading-relaxed">
              Ensaio fotográfico para gestantes gerado por IA.
              <br />
              Imagens realistas, emocionantes e atemporais.
            </p>

            {/* CTAs */}
            <div className="flex flex-wrap items-center gap-4 pt-2">
              <Link href="/register">
                <Button className="h-14 px-8 text-sm font-semibold rounded-full bg-[#748FCC] hover:bg-[#5F7DB8] transition-all duration-500 shadow-xl shadow-[#748FCC]/20 group flex items-center gap-2">
                  Criar meu ensaio
                  <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                </Button>
              </Link>
              <Link
                href="#exemplos"
                className="h-14 px-8 text-sm font-semibold rounded-full border border-white/15 hover:border-white/30 transition-all inline-flex items-center gap-2 text-[#F5F5F7]"
              >
                Explorar Galeria
                <Play className="w-4 h-4 fill-current" />
              </Link>
            </div>

            {/* Social proof */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="flex items-center gap-4 pt-4"
            >
              {/* Avatars stack — fotos reais */}
              <div className="flex -space-x-3">
                {avatarUrls.map((url, i) => (
                  <img
                    key={i}
                    src={url}
                    alt="Cliente AureaIA"
                    className="w-10 h-10 rounded-full border-2 border-[#0A0A0A] object-cover"
                  />
                ))}
              </div>
              <div>
                <p className="text-sm text-[#F5F5F7] font-medium">
                  +2.500 mamães já eternizaram
                </p>
                <p className="text-xs text-[#B8BCC4]">esse momento único</p>
              </div>
            </motion.div>
          </motion.div>

          {/* Right — Hero image with neon ring */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1.2, delay: 0.3 }}
            className="relative flex justify-center lg:justify-end"
          >
            {/* Neon ring glow behind */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] md:w-[500px] md:h-[500px] rounded-full border-2 border-[#748FCC]/40 shadow-[0_0_80px_rgba(116,143,204,0.25),inset_0_0_80px_rgba(116,143,204,0.08)] pointer-events-none" />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[420px] h-[420px] md:w-[520px] md:h-[520px] rounded-full bg-[#748FCC]/5 blur-[40px] pointer-events-none" />
            
            <div className="relative w-full max-w-[500px] aspect-[3/4] rounded-[32px] overflow-hidden">
              <img
                src="/landing/hero.png"
                alt="AureaIA — Ensaio de maternidade profissional com IA"
                className="w-full h-full object-cover object-top"
              />
              {/* Bottom gradient fade */}
              <div className="absolute inset-x-0 bottom-0 h-32 bg-gradient-to-t from-[#0A0A0A] to-transparent" />
            </div>
          </motion.div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════════
          FEATURES BAR — 4 ícones em linha (como na referência)
      ══════════════════════════════════════════════════════════════ */}
      <section className="py-16 px-6 border-y border-[#1F2329] bg-[#0D0D10]">
        <div className="max-w-[1200px] mx-auto grid grid-cols-2 md:grid-cols-4 gap-8">
          {features.map((f, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="flex flex-col items-center text-center gap-3 group"
            >
              <div className="w-14 h-14 rounded-2xl bg-[#121417] border border-white/10 flex items-center justify-center group-hover:border-[#748FCC]/40 group-hover:bg-[#748FCC]/10 transition-all duration-500">
                <f.icon className="w-6 h-6 text-[#748FCC]" />
              </div>
              <h4 className="text-sm font-bold text-[#F5F5F7]">{f.title}</h4>
              <p className="text-xs text-[#B8BCC4] font-light leading-relaxed max-w-[180px]">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════════
          COMPARAÇÃO — Por que AureaIA vs Estúdio Tradicional
      ══════════════════════════════════════════════════════════════ */}
      <section className="py-28 sm:py-40 px-6 sm:px-8 bg-[#121417] border-y border-[#1F2329]">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16 sm:mb-24 space-y-4">
            <span className="text-[10px] sm:text-[11px] font-bold uppercase tracking-[0.4em] text-[#748FCC]">Comparação</span>
            <h2 className="text-3xl sm:text-5xl md:text-6xl font-serif font-semibold tracking-tight text-[#F5F5F7]">
              Por que famílias escolhem <br className="hidden sm:block" />a AureaIA?
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 sm:gap-12">
            {/* Estúdio tradicional */}
            <div className="p-8 sm:p-12 rounded-[28px] bg-white/[0.02] border border-white/8">
              <p className="text-[11px] font-bold uppercase tracking-[0.3em] text-[#B8BCC4] mb-8">Estúdio Tradicional</p>
              <div className="space-y-5">
                {[
                  'R$1.500 a R$5.000',
                  'Agendar com semanas de antecedência',
                  'Deslocamento, trânsito, estresse',
                  'Resultado em 15 a 30 dias',
                  'Poucas poses e cenários',
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-3 text-[#B8BCC4]">
                    <div className="w-5 h-5 rounded-full border border-white/10 flex items-center justify-center shrink-0">
                      <span className="text-[9px]">✕</span>
                    </div>
                    <span className="text-sm sm:text-base font-light">{item}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* AureaIA */}
            <div className="p-8 sm:p-12 rounded-[28px] bg-[#748FCC]/10 border-2 border-[#748FCC]/40 relative overflow-hidden">
              <div className="absolute top-0 right-0 bg-[#748FCC] text-[10px] font-bold uppercase tracking-widest px-4 py-1.5 rounded-bl-2xl text-[#F5F5F7]">
                Recomendado
              </div>
              <p className="text-[11px] font-bold uppercase tracking-[0.3em] text-[#748FCC] mb-8">AureaIA™</p>
              <div className="space-y-5">
                {[
                  'A partir de R$25',
                  'Pronto em minutos, 24 horas por dia',
                  'Do conforto da sua casa',
                  'Resultado instantâneo em alta resolução',
                  '6 coleções editoriais exclusivas',
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-3 text-[#F5F5F7]">
                    <CheckCircle2 className="w-5 h-5 text-[#748FCC] shrink-0" />
                    <span className="text-sm sm:text-base font-medium">{item}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════════
          COMO FUNCIONA — Três passos. Dois minutos.
      ══════════════════════════════════════════════════════════════ */}
      <section id="como-funciona" className="py-28 sm:py-40 px-6 sm:px-8 max-w-[1400px] mx-auto scroll-mt-20">
        <div className="text-center mb-16 sm:mb-24 space-y-5">
          <span className="text-[10px] sm:text-[11px] font-bold uppercase tracking-[0.4em] text-[#748FCC]">Simples & Rápido</span>
          <h2 className="text-3xl sm:text-5xl md:text-7xl font-serif font-semibold tracking-tight text-[#F5F5F7]">
            Três passos. Dois minutos.
          </h2>
          <p className="text-lg sm:text-xl text-[#B8BCC4] font-light max-w-2xl mx-auto">
            Sem sair de casa, com preço acessível, tecnologia de estúdio profissional.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 sm:gap-10">
          {howItWorks.map((step, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.15 }}
            >
              <Card className="p-10 sm:p-14 space-y-6 flex flex-col items-center text-center group border-[#1F2329] hover:border-[#748FCC]/40 transition-all duration-700 rounded-[28px]">
                {/* Step number + Icon */}
                <div className="relative">
                  <div className="w-20 h-20 rounded-[20px] bg-[#748FCC]/10 flex items-center justify-center group-hover:scale-110 group-hover:bg-[#748FCC]/20 transition-all duration-700 border border-[#748FCC]/30">
                    <step.icon className="w-9 h-9 text-[#748FCC]" />
                  </div>
                  <span className="absolute -top-2 -right-2 text-[11px] font-bold text-[#F5F5F7] bg-[#748FCC] w-7 h-7 rounded-full flex items-center justify-center shadow-lg shadow-[#748FCC]/20">{step.step}</span>
                </div>
                <h3 className="text-2xl sm:text-3xl font-serif font-semibold text-[#F5F5F7]">{step.title}</h3>
                <p className="text-[#B8BCC4] font-light leading-relaxed text-base sm:text-lg">{step.description}</p>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════════
          GALERIA — "Feito para você" (como na referência)
      ══════════════════════════════════════════════════════════════ */}
      <section id="exemplos" className="py-28 sm:py-40 px-6 sm:px-8 bg-[#0A0A0A] scroll-mt-20">
        <div className="max-w-[1400px] mx-auto">
          <div className="text-center mb-16 sm:mb-20 space-y-5">
            <span className="text-[10px] sm:text-[11px] font-bold uppercase tracking-[0.4em] text-[#748FCC]">Galeria Editorial</span>
            <h2 className="text-3xl sm:text-5xl md:text-6xl font-serif font-semibold tracking-tight text-[#F5F5F7]">
              Do seu jeito. Do <span className="italic">seu sonho.</span>
              <br />
              Do seu momento.
            </h2>
            <p className="text-lg sm:text-xl text-[#B8BCC4] font-light max-w-3xl mx-auto leading-relaxed">
              Crie ensaios únicos com IA, com a sua cara, a energia que você
              sonha e a beleza que você merece.
            </p>
          </div>

          {/* Gallery grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3 sm:gap-4">
            {galleryImages.map((img, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08 }}
                className="group relative aspect-[3/4] rounded-2xl overflow-hidden cursor-pointer"
              >
                <img
                  src={img.src}
                  alt={img.alt}
                  className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 flex items-end p-4">
                  <span className="text-xs font-medium text-white/90">{img.alt}</span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════════
          DEPOIMENTOS — Confiança
      ══════════════════════════════════════════════════════════════ */}
      <section className="py-28 sm:py-40 px-6 sm:px-8 max-w-[1200px] mx-auto">
        <div className="text-center mb-16 sm:mb-20 space-y-4">
          <span className="text-[10px] sm:text-[11px] font-bold uppercase tracking-[0.4em] text-[#748FCC]">Depoimentos Reais</span>
          <h2 className="text-3xl sm:text-5xl font-serif font-semibold tracking-tight text-[#F5F5F7]">
            O que nossas mamães dizem.
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {testimonials.map((t, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
            >
              <Card className="p-6 sm:p-8 space-y-4 rounded-[24px] hover:border-[#748FCC]/30 transition-all h-full">
                <div className="flex items-center gap-1">
                  {Array.from({ length: t.stars }).map((_, s) => (
                    <Star key={s} className="w-4 h-4 fill-[#748FCC] text-[#748FCC]" />
                  ))}
                </div>
                <p className="text-sm sm:text-base font-serif font-light italic text-[#F5F5F7]/90 leading-relaxed">
                  &ldquo;{t.text}&rdquo;
                </p>
                <div className="pt-3 border-t border-white/8 flex items-center gap-3">
                  <img src={t.avatar} alt={t.name} className="w-9 h-9 rounded-full object-cover border border-white/10" />
                  <div>
                    <p className="text-xs font-bold text-[#F5F5F7]">{t.name}</p>
                    <p className="text-[10px] text-[#B8BCC4] font-light">{t.detail}</p>
                  </div>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════════
          CTA FINAL — Fechamento forte
      ══════════════════════════════════════════════════════════════ */}
      <section className="py-32 sm:py-48 px-6 sm:px-8 text-center relative overflow-hidden">
        {/* Background energy */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#0A0A0A] via-[#748FCC]/05 to-[#0A0A0A] pointer-events-none" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] bg-[#748FCC]/10 blur-[150px] rounded-full pointer-events-none" />

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-4xl mx-auto space-y-10 relative z-10"
        >
          <div className="inline-flex items-center gap-3 px-5 py-2 rounded-full bg-[#748FCC]/20 border border-[#748FCC]/30 text-[#F5F5F7] text-[10px] font-bold tracking-[0.3em] uppercase">
            <Zap className="w-4 h-4 text-[#748FCC]" /> Oferta de Lançamento
          </div>

          <h2 className="text-5xl sm:text-7xl md:text-8xl font-serif font-semibold tracking-tight leading-[0.95] text-[#F5F5F7]">
            Eternize sua história.
          </h2>
          <p className="text-lg sm:text-2xl text-[#B8BCC4] font-light max-w-2xl mx-auto leading-relaxed">
            Cada momento da maternidade merece ser celebrado com a grandeza que você carrega.
            <span className="text-[#F5F5F7] font-medium"> Comece agora.</span>
          </p>

          <div className="flex flex-col items-center gap-6 pt-4">
            <Link href="/register">
              <Button className="h-16 sm:h-20 px-14 sm:px-20 text-lg sm:text-xl font-bold uppercase tracking-[0.2em] bg-[#748FCC] hover:bg-[#5F7DB8] transition-all duration-700 rounded-2xl shadow-2xl shadow-[#748FCC]/30 group">
                Criar meu ensaio agora
                <ArrowRight className="w-6 h-6 transition-transform group-hover:translate-x-1" />
              </Button>
            </Link>
            <p className="text-[10px] sm:text-[11px] uppercase tracking-[0.3em] text-[#B8BCC4] font-bold">
              Cadastro rápido · Sem cartão de crédito · Resultados em minutos
            </p>
          </div>
        </motion.div>
      </section>

    </div>
  );
}
