"use client";

import { Check, Sparkles, Crown, Zap, ShieldCheck } from "lucide-react";
import { motion } from "framer-motion";

const plans = [
  {
    name: "Essencial",
    price: "9.90",
    desc: "Perfeito para uma primeira experiência cinematográfica.",
    credits: "50 Créditos",
    features: ["Até 10 Retratos HD", "Estilos Básicos", "Entrega em 24h", "Suporte Standard"],
    button: "Escolher Essencial",
    popular: false
  },
  {
    name: "Luxe",
    price: "19.90",
    desc: "O padrão ouro para ensaios completos e variados.",
    credits: "150 Créditos",
    features: ["Até 30 Retratos 4K", "Todos os Estilos Premium", "Geração Prioritária", "Sem Marca D'água", "Suporte VIP"],
    button: "Escolher Luxe",
    popular: true
  }
];

export default function Pricing() {
  return (
    <div className="min-h-screen bg-[#0A0A0A] px-6 py-24 relative overflow-hidden">
      {/* Background Gradients */}
      <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-[#748FCC]/10 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-[#F5F5F7]/5 blur-[100px] rounded-full pointer-events-none" />

      <div className="max-w-[1200px] mx-auto relative z-10">
        <div className="text-center mb-20">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-[#F5F5F7] text-[10px] font-bold tracking-[0.3em] uppercase mb-6"
          >
            <Crown className="w-3 h-3" /> Investimento em Memórias
          </motion.div>
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-5xl md:text-7xl font-serif font-bold text-[#F5F5F7] mb-6 tracking-tighter"
          >
            Sua Galeria <span className="text-[#748FCC]">Premium</span>
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-lg text-[#B8BCC4] max-w-2xl mx-auto leading-relaxed font-light"
          >
            Escolha o plano que melhor se adapta ao seu momento. Cada retrato é processado com nossa engine de IA de altíssimo padrão.
          </motion.p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {plans.map((plan, idx) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + idx * 0.1 }}
              className={`relative rounded-[40px] p-10 flex flex-col transition-all duration-500 hover:scale-[1.02] ${
                plan.popular 
                  ? 'bg-gradient-to-b from-white/[0.08] to-transparent border-2 border-[#748FCC]/30 shadow-[0_20px_50px_rgba(116,143,204,0.15)]' 
                  : 'bg-[#121417] border border-[#1F2329]'
              }`}
            >
              {plan.popular && (
                <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-[#748FCC] text-[#F5F5F7] px-5 py-1.5 rounded-full text-[10px] font-bold tracking-widest uppercase shadow-xl flex items-center gap-2">
                  <Sparkles className="w-3 h-3" /> Mais Escolhido
                </div>
              )}
              
              <div className="mb-10">
                <h3 className="text-2xl font-serif font-bold text-[#F5F5F7] mb-2">{plan.name}</h3>
                <p className="text-sm text-[#B8BCC4] font-light mb-8">{plan.desc}</p>
                <div className="flex items-baseline gap-1">
                  <span className="text-[#B8BCC4] text-xl font-light">R$</span>
                  <span className="text-6xl font-serif font-bold text-[#F5F5F7] tracking-tighter">{plan.price}</span>
                  <span className="text-[#B8BCC4] text-sm ml-2">BRL</span>
                </div>
              </div>

              <div className="flex items-center gap-3 p-4 bg-white/5 rounded-2xl mb-8 border border-white/5">
                <Zap className="w-5 h-5 text-[#748FCC]" />
                <span className="font-bold text-[#F5F5F7] tracking-wide uppercase text-sm">{plan.credits}</span>
              </div>
              
              <ul className="space-y-5 mb-12 flex-1">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-3 text-sm text-[#B8BCC4] font-light">
                    <div className={`p-1 rounded-full ${plan.popular ? 'bg-[#748FCC]/20 text-[#748FCC]' : 'bg-white/10 text-[#F5F5F7]'}`}>
                      <Check className="w-3.5 h-3.5" />
                    </div>
                    {feature}
                  </li>
                ))}
              </ul>

              <button className={`w-full py-5 rounded-2xl font-bold text-lg transition-all active:scale-95 ${
                plan.popular 
                  ? 'bg-[#748FCC] text-[#F5F5F7] hover:bg-[#5F7DB8] shadow-xl shadow-[#748FCC]/20' 
                  : 'bg-transparent border border-white/10 text-[#F5F5F7] hover:bg-white/5'
              }`}>
                {plan.button}
              </button>
            </motion.div>
          ))}
        </div>

        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="mt-20 flex flex-wrap justify-center gap-12 opacity-30 grayscale hover:grayscale-0 hover:opacity-100 transition-all duration-700"
        >
          <div className="flex items-center gap-2 text-xs font-bold tracking-widest text-[#B8BCC4]">
            <ShieldCheck className="w-4 h-4" /> Pagamento Seguro via Stripe
          </div>
          <div className="flex items-center gap-2 text-xs font-bold tracking-widest text-[#B8BCC4]">
            <Zap className="w-4 h-4" /> Ativação Instantânea
          </div>
        </motion.div>
      </div>
    </div>
  );
}
