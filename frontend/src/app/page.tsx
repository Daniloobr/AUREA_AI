"use client";

import { motion } from "framer-motion";
import { ArrowRight, Sparkles, Camera, Image as ImageIcon, Lock } from "lucide-react";
import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col items-center bg-[#09090B] text-white min-h-screen selection:bg-[#9857CB] selection:text-white">
      
      {/* Background Orbs */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
        <div className="absolute top-[-10%] right-[-5%] w-[40vw] h-[40vw] rounded-full bg-gradient-to-br from-[#9857CB]/20 to-[#AAA7EB]/10 blur-[120px]" />
        <div className="absolute bottom-[-10%] left-[-5%] w-[50vw] h-[50vw] rounded-full bg-gradient-to-tr from-[#81E386]/10 to-[#AAA7EB]/10 blur-[100px]" />
      </div>

      {/* Hero Section */}
      <section className="w-full relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden flex flex-col items-center text-center px-6 z-10">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          className="max-w-[1000px] w-full"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-zinc-300 font-medium text-sm mb-8 backdrop-blur-md">
            <Sparkles className="w-4 h-4 text-[#AAA7EB]" />
            <span>A Revolução da Fotografia Materna</span>
          </div>
          
          <h1 className="text-[56px] md:text-[80px] lg:text-[96px] font-bold tracking-tighter leading-[1.05] text-white mb-8">
            Estúdio Cinematográfico <br className="hidden md:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#9857CB] via-[#AAA7EB] to-[#81E386]">
              no seu Bolso.
            </span>
          </h1>
          
          <p className="text-[20px] md:text-[24px] text-zinc-400 font-light max-w-3xl mx-auto leading-relaxed mb-12">
            Esqueça estúdios caros e cansativos. Envie selfies do seu celular e nossa Inteligência Artificial renderizará obras de arte em resolução de capa de revista.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-6">
            <Link href="/login" className="w-full sm:w-auto h-[64px] px-10 bg-white text-[#09090B] rounded-full text-[18px] font-bold hover:scale-105 transition-all flex items-center justify-center gap-3">
              Entrar no Estúdio <ArrowRight className="w-5 h-5" />
            </Link>
            <Link href="#preview" className="w-full sm:w-auto h-[64px] px-10 bg-white/5 border border-white/10 text-white rounded-full text-[18px] font-medium hover:bg-white/10 transition-all flex items-center justify-center">
              Veja a Mágica
            </Link>
          </div>
        </motion.div>
      </section>

      {/* Bento Grid Features */}
      <section id="preview" className="w-full py-32 px-6 z-10">
        <div className="max-w-[1400px] mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-[40px] md:text-[56px] font-bold tracking-tight mb-6">Projetado para impressionar.</h2>
            <p className="text-zinc-400 text-[20px] max-w-2xl mx-auto">Apenas três passos separam suas fotos comuns de um ensaio editorial premiado.</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Card 1 */}
            <motion.div whileHover={{ y: -8 }} className="p-10 rounded-[32px] bg-white/5 border border-white/10 backdrop-blur-xl flex flex-col justify-between aspect-[4/5] relative overflow-hidden group">
              <div className="absolute inset-0 bg-gradient-to-b from-[#9857CB]/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="w-16 h-16 rounded-[24px] bg-white/10 text-white flex items-center justify-center mb-8 border border-white/5">
                <Camera className="w-8 h-8" />
              </div>
              <div>
                <h3 className="text-[28px] font-bold tracking-tight mb-4">1. Captura Simples</h3>
                <p className="text-zinc-400 text-[18px] leading-relaxed">Faça upload de pelo menos 3 selfies nítidas feitas em qualquer lugar.</p>
              </div>
            </motion.div>
            
            {/* Card 2 */}
            <motion.div whileHover={{ y: -8 }} className="p-10 rounded-[32px] bg-white/5 border border-white/10 backdrop-blur-xl flex flex-col justify-between aspect-[4/5] relative overflow-hidden group">
              <div className="absolute inset-0 bg-gradient-to-b from-[#AAA7EB]/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="w-16 h-16 rounded-[24px] bg-white/10 text-white flex items-center justify-center mb-8 border border-white/5">
                <Sparkles className="w-8 h-8" />
              </div>
              <div>
                <h3 className="text-[28px] font-bold tracking-tight mb-4">2. Direção de Arte</h3>
                <p className="text-zinc-400 text-[18px] leading-relaxed">Escolha entre estúdios luxuosos, praia, natureza ou editoriais de alta moda.</p>
              </div>
            </motion.div>
            
            {/* Card 3 */}
            <motion.div whileHover={{ y: -8 }} className="p-10 rounded-[32px] bg-[#9857CB]/10 border border-[#9857CB]/30 backdrop-blur-xl flex flex-col justify-between aspect-[4/5] relative overflow-hidden group">
              <div className="absolute inset-0 bg-gradient-to-b from-[#81E386]/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="w-16 h-16 rounded-[24px] bg-[#9857CB]/20 text-[#81E386] flex items-center justify-center mb-8 border border-[#9857CB]/30 shadow-[0_0_20px_rgba(152,87,203,0.5)]">
                <ImageIcon className="w-8 h-8" />
              </div>
              <div>
                <h3 className="text-[28px] font-bold tracking-tight mb-4 text-white">3. A Mágica Acontece</h3>
                <p className="text-[#AAA7EB] text-[18px] leading-relaxed">Em menos de 1 minuto, nosso cluster de GPUs renderiza suas imagens perfeitas.</p>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="w-full py-32 px-6 z-10 border-t border-white/5">
        <div className="max-w-[1000px] mx-auto text-center bg-white/5 border border-white/10 p-16 md:p-24 rounded-[48px] backdrop-blur-2xl relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-[#9857CB]/20 to-[#AAA7EB]/20" />
          <div className="relative z-10">
            <Lock className="w-12 h-12 text-[#AAA7EB] mx-auto mb-8" />
            <h2 className="text-[40px] md:text-[56px] font-bold tracking-tight mb-8">Acesso Exclusivo.</h2>
            <p className="text-[20px] text-zinc-300 mb-12 max-w-xl mx-auto">A qualidade inigualável dos nossos ensaios requer um ambiente fechado. Autentique-se para começar.</p>
            <Link href="/login" className="inline-flex h-[64px] px-12 bg-white text-[#09090B] rounded-full text-[18px] font-bold hover:scale-105 transition-all items-center justify-center shadow-[0_0_40px_rgba(255,255,255,0.3)]">
              Entrar no Estúdio
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
