'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Check, Sparkles, ShieldCheck, Gem, Star, Zap,
  ArrowRight, Clock, Camera, Download, X, CheckCircle2
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useAuth } from '@/contexts/AuthContext';
import { useSearchParams, useRouter } from 'next/navigation';
import { usePageTitle } from '@/hooks/usePageTitle';

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
    description: 'Ideal para experimentar nossa qualidade e criar seus primeiros ensaios.',
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
    description: 'O equilíbrio perfeito para explorar múltiplos estilos com agilidade.',
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
    description: 'Para quem deseja a experiência completa de estúdio e suporte exclusivo.',
    features: [
      '16 ensaios completos',
      'Acesso a todos os estilos',
      'Download em alta resolução',
      'Créditos nunca expiram',
      'Suporte prioritário',
    ],
  },
];

function CreditsContent() {
  usePageTitle('Créditos');
  const { user, token, refreshUser } = useAuth();
  const searchParams = useSearchParams();
  const router = useRouter();
  const [notification, setNotification] = useState<{ message: string, type: 'success' | 'error' } | null>(null);

  // Detectar sucesso no pagamento e atualizar créditos
  useEffect(() => {
    if (searchParams.get('success') === 'true') {
      setNotification({ message: 'Pagamento confirmado! Atualizando saldo...', type: 'success' });
      refreshUser().then(() => {
        setNotification({ message: 'Créditos atualizados com sucesso!', type: 'success' });
      });
      // Limpar URL sem recarregar a página
      router.replace('/credits');
    }
  }, [searchParams, refreshUser, router]);

  // Limpar notificação
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  const handlePackageSelect = async (pkg: typeof PACKAGES[0]) => {
    if (!user) {
      setNotification({ message: 'Você precisa estar logado para comprar créditos.', type: 'error' });
      return;
    }

    if (!token) {
      setNotification({ message: 'Sessão inválida. Por favor, faça login novamente.', type: 'error' });
      return;
    }

    try {
      setNotification({ message: 'Iniciando pagamento seguro com Stripe...', type: 'success' });

      // Mapeamento dos pacotes locais para os price_ids do Stripe Dashboard
      const priceMap: { [key: string]: string } = {
        '100_credits': 'price_1TXBt5AXb2fn2YJDXDIF0iKk',
        '200_credits': 'price_1TXBtWAXb2fn2YJDZxm1s4Xz',
        '400_credits': 'price_1TaSlbAXb2fn2YJD21xOhXPs'
      };

      const priceId = priceMap[pkg.id];
      if (!priceId) {
        setNotification({ message: 'Pacote de créditos inválido.', type: 'error' });
        return;
      }

      const response = await fetch('/api/create-checkout-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ price_id: priceId }),
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        const errorMsg = data?.error || data?.message || 'Erro ao gerar sessão de pagamento.';
        setNotification({ message: errorMsg, type: 'error' });
        return;
      }

      if (data?.url) {
        window.location.assign(data.url);
        return;
      }

      setNotification({ message: 'Resposta inválida do servidor. Tente novamente.', type: 'error' });
    } catch (err: unknown) {
      console.error('Erro no checkout Stripe:', err);
      setNotification({ message: 'Conexão com o estúdio interrompida. Tente novamente.', type: 'error' });
    }
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
            className={`fixed top-4 left-1/2 z-[200] px-6 py-3 rounded-full shadow-2xl flex items-center gap-3 border ${notification.type === 'success'
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
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8 max-w-sm sm:max-w-none mx-auto">
          {PACKAGES.map((pkg, idx) => (
            <motion.div
              key={pkg.id}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="flex w-full"
            >
              <div className={`flex-1 flex flex-col rounded-[28px] overflow-hidden transition-all duration-500 relative ${pkg.popular
                  ? 'bg-gradient-to-b from-[#748FCC]/20 to-[#0D0D0D] border-2 border-[#748FCC]/50 shadow-2xl scale-[1.02]'
                  : 'bg-[#121417] border border-[#1F2329] hover:border-[#748FCC]/20'
                }`}>
                {pkg.badge && (
                  <div className={`absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 text-[10px] font-bold uppercase tracking-widest px-5 py-1.5 rounded-full z-10 ${pkg.popular ? 'bg-[#748FCC] text-[#F5F5F7]' : 'bg-white/10 text-[#F5F5F7]/80'
                    }`}>
                    {pkg.badge}
                  </div>
                )}
                <div className="p-10 flex flex-col flex-1">
                  <div className="mb-6 sm:mb-8">
                    <div className="w-14 h-14 rounded-2xl bg-[#748FCC]/10 border border-[#748FCC]/20 flex items-center justify-center mb-4">
                      <pkg.icon className="w-7 h-7 text-[#748FCC]" />
                    </div>
                    <h3 className="text-sm font-bold uppercase tracking-[0.25em] text-[#B8BCC4]">{pkg.name}</h3>
                    <p className="text-xl sm:text-2xl font-serif font-semibold text-[#F5F5F7] mt-1">{pkg.credits} Créditos</p>
                  </div>
                  <div className="mb-6 sm:mb-8">
                    <div className="flex items-baseline gap-1 mb-3">
                      <span className="text-2xl font-medium text-[#B8BCC4]">R$</span>
                      <span className="text-6xl sm:text-7xl font-bold tracking-tight text-[#F5F5F7] leading-none">{pkg.price}</span>
                    </div>
                    <p className="text-[13px] sm:text-sm text-[#B8BCC4] font-light leading-relaxed">
                      {pkg.description}
                    </p>
                  </div>
                  <div className="space-y-4 flex-1 mb-8 sm:mb-10">
                    {pkg.features.map((feature, i) => (
                      <div key={i} className="flex items-start gap-3">
                        <Check className="w-5 h-5 text-[#748FCC] shrink-0 mt-0.5" />
                        <span className="text-[13px] sm:text-sm font-light text-[#B8BCC4]">{feature}</span>
                      </div>
                    ))}
                  </div>
                  <Button
                    onClick={() => handlePackageSelect(pkg)}
                    variant={pkg.popular ? 'primary' : 'secondary'}
                    className={`w-full py-4 h-auto text-[13px] sm:text-sm font-bold tracking-[0.1em] rounded-xl sm:rounded-2xl group transition-all duration-300 ${pkg.popular
                        ? 'bg-[#748FCC] hover:bg-[#5F7DB8] hover:shadow-[0_0_30px_rgba(116,143,204,0.3)] text-white border-none'
                        : 'bg-white/5 hover:bg-white/10 text-[#F5F5F7] border border-white/10'
                      }`}
                  >
                    Adquirir Pacote
                    <ArrowRight className="w-4 h-4 ml-2 transition-transform group-hover:translate-x-1" />
                  </Button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Garantias */}
        <div className="bg-[#121417] border border-[#1F2329] rounded-[24px] sm:rounded-[32px] p-8 sm:p-14 text-center">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 sm:gap-10">
            <div className="space-y-3 sm:space-y-4">
              <ShieldCheck className="w-8 h-8 sm:w-10 sm:h-10 text-[#748FCC] mx-auto" />
              <h4 className="font-semibold text-sm sm:text-base">Pagamento Seguro</h4>
              <p className="text-[13px] sm:text-sm text-[#B8BCC4] font-light">Processado via Stripe</p>
            </div>
            <div className="space-y-3 sm:space-y-4">
              <Clock className="w-8 h-8 sm:w-10 sm:h-10 text-[#748FCC] mx-auto" />
              <h4 className="font-semibold text-sm sm:text-base">Entrega Instantânea</h4>
              <p className="text-[13px] sm:text-sm text-[#B8BCC4] font-light">Créditos liberados na hora</p>
            </div>
            <div className="space-y-3 sm:space-y-4">
              <Star className="w-8 h-8 sm:w-10 sm:h-10 text-[#748FCC] mx-auto" />
              <h4 className="font-semibold text-sm sm:text-base">Sem Validade</h4>
              <p className="text-[13px] sm:text-sm text-[#B8BCC4] font-light">Seus créditos nunca expiram</p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

export default function CreditsPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-[#0A0A0A] flex items-center justify-center text-[#F5F5F7]">Carregando...</div>}>
      <CreditsContent />
    </Suspense>
  );
}
