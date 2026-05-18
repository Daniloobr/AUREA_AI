'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Check, Sparkles, ShieldCheck, Gem, Star, Zap, 
  ArrowRight, Clock, Camera, Download, X, CheckCircle2
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useAuth } from '@/contexts/AuthContext';

/* ═══════════════════════════════════════════════════════════════════════════
   PACOTES
   ═══════════════════════════════════════════════════════════════════════════ */
const PACKAGES = [
  {
    id: '100_credits',
    name: 'Essencial',
    credits: 100,
    price: '25',
    priceValue: 25.00,
    icon: Zap,
    badge: null,
    link: 'https://syncpay.link/9nyBou',
    features: [
      '4 ensaios completos',
      'Acesso a todos os estilos',
      'Download em alta resolução',
      'Créditos nunca expiram',
    ],
  },
  {
    id: '200_credits',
    name: 'Ateliê',
    credits: 200,
    price: '50',
    priceValue: 50.00,
    popular: true,
    icon: Sparkles,
    badge: '✦ Mais Escolhido',
    link: 'https://syncpay.link/8IH7fr',
    features: [
      '8 ensaios completos',
      'Acesso a todos os estilos',
      'Download em alta resolução',
      'Créditos nunca expiram',
      'Prioridade na fila',
    ],
  },
  {
    id: '400_credits',
    name: 'Maison',
    credits: 400,
    price: '120',
    priceValue: 120.00,
    icon: Gem,
    badge: 'VIP',
    link: 'https://syncpay.link/Gyu2QM',
    features: [
      '16 ensaios completos',
      'Acesso a todos os estilos',
      'Download em alta resolução',
      'Créditos nunca expiram',
      'Suporte prioritário',
    ],
  },
];

export default function CreditsPage() {
  const { user } = useAuth();
  const [notification, setNotification] = useState<{message: string, type: 'success' | 'error'} | null>(null);

  // Limpar notificação
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  const handlePackageSelect = (pkg: typeof PACKAGES[0]) => {
    if (!user) {
      setNotification({ message: 'Você precisa estar logado para comprar créditos.', type: 'error' });
      return;
    }
    // Redireciona para o link de checkout do SyncPay
    window.location.href = pkg.link;
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-[#F5F5F7] pt-24 pb-32 px-4 sm:px-6 relative overflow-x-hidden">
      
      {/* Notificação */}
      <AnimatePresence>
        {notification && (
          <motion.div
            initial={{ opacity: 0, y: -50, x: '-50%' }}
            animate={{ opacity: 1, y: 20, x: '-50%' }}
            exit={{ opacity: 0, y: -50, x: '-50%' }}
            className={`fixed top-4 left-1/2 z-[200] px-6 py-3 rounded-full shadow-2xl flex items-center gap-3 border ${
              notification.type === 'success' 
                ? 'bg-emerald-500/90 border-emerald-400 text-white' 
                : 'bg-red-500/90 border-red-400 text-white'
            }`}
          >
            {notification.type === 'success' ? <CheckCircle2 className="w-5 h-5" /> : <X className="w-5 h-5" />}
            <span className="text-sm font-bold">{notification.message}</span>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="max-w-[1300px] mx-auto space-y-16 sm:space-y-24">

        {/* Cabeçalho */}
        <motion.header
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center space-y-6 max-w-3xl mx-auto pt-8"
        >
          <div className="inline-flex items-center gap-3 px-5 py-2 rounded-full bg-[#748FCC]/20 border border-[#748FCC]/30 text-[#F5F5F7] text-[10px] font-bold tracking-[0.3em] uppercase">
            <Sparkles className="w-4 h-4" /> Preço justo, resultado de estúdio
          </div>
          <h1 className="text-4xl sm:text-7xl font-serif font-semibold tracking-tight leading-[1.05]">
            Invista em memórias<br />
            <span className="italic text-[#B8BCC4]">que duram para sempre.</span>
          </h1>
          {user && (
            <div className="inline-flex items-center gap-3 bg-white/5 border border-white/10 px-6 py-3 rounded-full">
              <span className="text-sm font-bold text-[#F5F5F7] tracking-wide">
                ✦ Seu saldo: {user.credits_balance} moedas
              </span>
            </div>
          )}
        </motion.header>

        {/* Grid de Pacotes */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {PACKAGES.map((pkg, idx) => (
            <motion.div
              key={pkg.id}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="flex"
            >
              <div className={`flex-1 flex flex-col rounded-[28px] overflow-hidden transition-all duration-500 relative ${
                pkg.popular
                  ? 'bg-gradient-to-b from-[#748FCC]/20 to-[#0D0D0D] border-2 border-[#748FCC]/50 shadow-2xl scale-[1.02]'
                  : 'bg-[#121417] border border-[#1F2329] hover:border-[#748FCC]/20'
              }`}>
                {pkg.badge && (
                  <div className={`absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 text-[10px] font-bold uppercase tracking-widest px-5 py-1.5 rounded-full z-10 ${
                    pkg.popular ? 'bg-[#748FCC] text-[#F5F5F7]' : 'bg-white/10 text-[#F5F5F7]/80'
                  }`}>
                    {pkg.badge}
                  </div>
                )}
                <div className="p-10 flex flex-col flex-1">
                  <div className="mb-8">
                    <div className="w-14 h-14 rounded-2xl bg-[#748FCC]/10 border border-[#748FCC]/20 flex items-center justify-center mb-4">
                      <pkg.icon className="w-7 h-7 text-[#748FCC]" />
                    </div>
                    <h3 className="text-sm font-bold uppercase tracking-[0.25em] text-[#B8BCC4]">{pkg.name}</h3>
                    <p className="text-xl font-serif font-semibold text-[#F5F5F7] mt-1">{pkg.credits} Créditos</p>
                  </div>
                  <div className="mb-8">
                    <div className="flex items-baseline gap-1">
                      <span className="text-2xl font-medium text-[#B8BCC4]">R$</span>
                      <span className="text-7xl font-bold tracking-tight text-[#F5F5F7] leading-none">{pkg.price}</span>
                    </div>
                  </div>
                  <div className="space-y-4 flex-1 mb-10">
                    {pkg.features.map((feature, i) => (
                      <div key={i} className="flex items-start gap-3">
                        <Check className="w-5 h-5 text-[#748FCC] shrink-0 mt-0.5" />
                        <span className="text-sm font-light text-[#B8BCC4]">{feature}</span>
                      </div>
                    ))}
                  </div>
                  <Button
                    onClick={() => handlePackageSelect(pkg)}
                    variant={pkg.popular ? 'primary' : 'secondary'}
                    className="w-full h-16 font-bold tracking-[0.1em] rounded-2xl group"
                  >
                    Adquirir Pacote
                    <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                  </Button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Garantias */}
        <div className="bg-[#121417] border border-[#1F2329] rounded-[32px] p-14 text-center">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-10">
            <div className="space-y-4">
               <ShieldCheck className="w-10 h-10 text-[#748FCC] mx-auto" />
              <h4 className="font-semibold">Pagamento Seguro</h4>
              <p className="text-sm text-[#B8BCC4] font-light">Processado via SyncPay</p>
            </div>
            <div className="space-y-4">
              <Clock className="w-10 h-10 text-[#748FCC] mx-auto" />
              <h4 className="font-semibold">Entrega Instantânea</h4>
              <p className="text-sm text-[#B8BCC4] font-light">Créditos liberados na hora</p>
            </div>
            <div className="space-y-4">
              <Star className="w-10 h-10 text-[#748FCC] mx-auto" />
              <h4 className="font-semibold">Sem Validade</h4>
              <p className="text-sm text-[#B8BCC4] font-light">Seus créditos nunca expiram</p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
