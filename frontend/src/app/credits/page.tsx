'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Check, Sparkles, ShieldCheck, Gem, Star, Zap, 
  ArrowRight, Clock, Camera, Download, X, Copy, 
  CheckCircle2, Loader2, QrCode 
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/services/api';
import { QRCodeSVG } from 'qrcode.react';

/* ═══════════════════════════════════════════════════════════════════════════
   PACOTES (Atualizados conforme PDR v1.1.0)
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
    features: [
      '16 ensaios completos',
      'Acesso a todos os estilos',
      'Download em alta resolução',
      'Créditos nunca expiram',
      'Suporte prioritário',
    ],
  },
];

interface PixData {
  transaction_id: string;
  pix_code: string;
  identifier_syncpay: string;
  package_name: string;
  amount: number;
}

export default function CreditsPage() {
  const { user, token, refreshUser } = useAuth();
  const [loadingPackageId, setLoadingPackageId] = useState<string | null>(null);
  const [showPixModal, setShowPixModal] = useState(false);
  const [pixData, setPixData] = useState<PixData | null>(null);
  const [copied, setCopied] = useState(false);
  const [paymentStatus, setPaymentStatus] = useState<'pending' | 'completed' | 'failed'>('pending');
  const [notification, setNotification] = useState<{message: string, type: 'success' | 'error'} | null>(null);

  // Função para copiar código PIX
  const copyPixCode = () => {
    if (pixData?.pix_code) {
      navigator.clipboard.writeText(pixData.pix_code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  // Iniciar compra
  const handleBuy = async (pkg: typeof PACKAGES[0]) => {
    if (!user) {
      setNotification({ message: 'Você precisa estar logado para comprar créditos.', type: 'error' });
      return;
    }
    console.log("Iniciando compra do pacote:", pkg.id);
    setLoadingPackageId(pkg.id);
    try {
      console.log("Chamando API createSession...");
      const response = await apiService.checkout.createSession(pkg.id, token || undefined);
      console.log("Resposta da API:", response);
      
      if (response.url) {
        // Redireciona para o Stripe Checkout
        window.location.href = response.url;
      } else {
        console.error("Erro retornado pela API:", response.error);
        setNotification({ message: response.error || 'Erro ao gerar checkout', type: 'error' });
      }
    } catch (error: any) {
      console.error("Erro catastrófico no handleBuy:", error);
      setNotification({ message: error.message || 'Erro de conexão com o servidor', type: 'error' });
    } finally {
      setLoadingPackageId(null);
    }
  };

  // Polling de status do pagamento
  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (showPixModal && pixData?.transaction_id && paymentStatus === 'pending') {
      interval = setInterval(async () => {
        try {
          const response = await apiService.checkout.getStatus(pixData.transaction_id, token || undefined);
          if (response.status === 'completed') {
            setPaymentStatus('completed');
            setNotification({ message: 'Pagamento confirmado com sucesso!', type: 'success' });
            if (refreshUser) refreshUser();
            
            // Fecha o modal após 3 segundos de sucesso
            setTimeout(() => {
              setShowPixModal(false);
              setPixData(null);
            }, 3000);
          }
        } catch (error) {
          console.error('Erro ao verificar status:', error);
        }
      }, 5000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [showPixModal, pixData, paymentStatus, refreshUser, token]);

  // Limpar notificação após 5s
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-[#F5F5F7] pt-24 pb-32 px-4 sm:px-6 relative overflow-x-hidden">
      
      {/* Notificação Customizada */}
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

        {/* ── Cabeçalho ──────────────────────────────────────────────── */}
        <motion.header
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center space-y-6 sm:space-y-8 max-w-3xl mx-auto pt-4 sm:pt-8"
        >
          <div className="inline-flex items-center gap-3 px-5 py-2 rounded-full bg-[#748FCC]/20 border border-[#748FCC]/30 text-[#F5F5F7] text-[10px] sm:text-[11px] font-bold tracking-[0.3em] uppercase">
            <Sparkles className="w-4 h-4" /> Preço justo, resultado de estúdio
          </div>

          <h1 className="text-4xl sm:text-6xl md:text-7xl font-serif font-semibold tracking-tight leading-[1.05] text-[#F5F5F7]">
            Invista em memórias<br />
            <span className="italic text-[#B8BCC4]">que duram para sempre.</span>
          </h1>

          <p className="text-base sm:text-xl text-[#B8BCC4] font-light leading-relaxed max-w-2xl mx-auto">
            Cada pacote dá acesso à nossa coleção editorial completa — 
            a mesma tecnologia de estúdio profissional, <span className="text-[#F5F5F7] font-medium">a partir de R$6 por ensaio.</span>
          </p>

          {/* Saldo atual */}
          {user && (
            <div className="inline-flex items-center gap-3 bg-white/5 border border-white/10 px-6 py-3 rounded-full">
              <span className="text-sm sm:text-base font-bold text-[#F5F5F7] tracking-wide">
                ✦ Seu saldo: {user.credits_balance} moedas
              </span>
            </div>
          )}
        </motion.header>

        {/* ── Grid de pacotes ─────────────────────────────────────────── */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8 items-stretch">
          {PACKAGES.map((pkg, idx) => (
            <motion.div
              key={pkg.id}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.12 }}
              className="flex"
            >
              <div className={`flex-1 flex flex-col rounded-[28px] overflow-hidden transition-all duration-500 relative ${
                pkg.popular
                  ? 'bg-gradient-to-b from-[#748FCC]/20 to-[#0D0D0D] border-2 border-[#748FCC]/50 shadow-2xl shadow-[#748FCC]/10 scale-[1.02]'
                  : 'bg-[#121417] border border-[#1F2329] hover:border-[#748FCC]/20'
              }`}>

                {/* Badge */}
                {pkg.badge && (
                  <div className={`absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 text-[10px] font-bold uppercase tracking-widest px-5 py-1.5 rounded-full whitespace-nowrap z-10 ${
                    pkg.popular ? 'bg-[#748FCC] text-[#F5F5F7]' : 'bg-white/10 text-[#F5F5F7]/80'
                  }`}>
                    {pkg.badge}
                  </div>
                )}

                {/* Conteúdo */}
                <div className="p-8 sm:p-10 flex flex-col flex-1">

                  {/* Ícone + Nome */}
                  <div className="mb-6 sm:mb-8">
                    <div className={`w-14 h-14 rounded-2xl flex items-center justify-center mb-4 ${
                      pkg.popular ? 'bg-[#748FCC]/40 border border-[#748FCC]/50' : 'bg-white/5 border border-[#1F2329]'
                    }`}>
                      <pkg.icon className="w-7 h-7 text-[#748FCC]" />
                    </div>
                    <h3 className="text-sm font-bold uppercase tracking-[0.25em] text-[#B8BCC4]">{pkg.name}</h3>
                    <p className="text-lg sm:text-xl font-serif font-semibold text-[#F5F5F7] mt-1">{pkg.credits} Créditos</p>
                  </div>

                  {/* Preço — GRANDE */}
                  <div className="mb-6 sm:mb-8 space-y-2">
                    <div className="flex items-baseline gap-1">
                      <span className="text-xl sm:text-2xl font-medium text-[#B8BCC4]">R$</span>
                      <span className="text-6xl sm:text-7xl font-bold tracking-tight text-[#F5F5F7] leading-none">{pkg.price}</span>
                    </div>
                    <div className="flex items-center gap-3 flex-wrap">
                      <span className="text-[12px] sm:text-sm text-[#B8BCC4] font-light">
                        = R$ {(pkg.priceValue / (pkg.credits / 25)).toFixed(2).replace('.', ',')} por ensaio
                      </span>
                    </div>
                  </div>

                  {/* O que está incluso */}
                  <div className="space-y-3 sm:space-y-4 flex-1 mb-8">
                    {pkg.features.map((feature, i) => (
                      <div key={i} className="flex items-start gap-3">
                        <Check className="w-5 h-5 text-[#748FCC] shrink-0 mt-0.5" />
                        <span className="text-sm sm:text-[15px] font-light text-[#B8BCC4] leading-snug">{feature}</span>
                      </div>
                    ))}
                  </div>

                  {/* CTA */}
                  <Button
                    onClick={() => handleBuy(pkg)}
                    disabled={loadingPackageId !== null}
                    variant={pkg.popular ? 'primary' : 'secondary'}
                    className={`w-full h-14 sm:h-16 font-bold text-sm sm:text-base tracking-[0.1em] rounded-2xl group ${
                      pkg.popular ? 'shadow-lg shadow-[#748FCC]/20 hover:shadow-[0_0_40px_rgba(116,143,204,0.35)]' : ''
                    }`}
                  >
                    {loadingPackageId === pkg.id ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin mr-2" />
                        Gerando PIX...
                      </>
                    ) : (
                      <>
                        Adquirir Pacote
                        <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* ── Modal PIX ────────────────────────────────────────────── */}
        <AnimatePresence>
          {showPixModal && (
            <div className="fixed inset-0 z-[150] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
              <motion.div
                initial={{ opacity: 0, scale: 0.9, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9, y: 20 }}
                className="bg-[#121417] border border-[#1F2329] rounded-[32px] w-full max-w-lg overflow-hidden relative shadow-2xl"
              >
                {/* Fechar */}
                <button 
                  onClick={() => setShowPixModal(false)}
                  className="absolute top-6 right-6 p-2 rounded-full bg-white/5 hover:bg-white/10 text-[#B8BCC4] transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>

                <div className="p-8 sm:p-12 text-center space-y-8">
                  <div className="space-y-2">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#748FCC]/10 border border-[#748FCC]/20 text-[#748FCC] text-[10px] font-bold uppercase tracking-widest">
                      <QrCode className="w-3 h-3" /> Pagamento Instantâneo
                    </div>
                    <h2 className="text-2xl sm:text-3xl font-serif font-semibold text-[#F5F5F7]">Pague com PIX</h2>
                    <p className="text-[#B8BCC4] font-light">
                      Pacote <span className="text-[#F5F5F7] font-medium">{pixData?.package_name}</span> · 
                      Valor: <span className="text-[#748FCC] font-bold">R$ {pixData?.amount.toFixed(2)}</span>
                    </p>
                  </div>

                  {/* QR Code */}
                  <div className="bg-white p-6 rounded-2xl inline-block shadow-[0_0_50px_rgba(116,143,204,0.15)]">
                    {pixData?.pix_code ? (
                      <QRCodeSVG 
                        value={pixData.pix_code} 
                        size={220}
                        level="M"
                        includeMargin={false}
                      />
                    ) : (
                      <div className="w-48 h-48 sm:w-56 sm:h-56 flex items-center justify-center bg-gray-100 rounded-xl">
                        <Loader2 className="w-8 h-8 animate-spin text-[#748FCC]" />
                      </div>
                    )}
                  </div>

                  {/* Status / Instruções */}
                  <div className="space-y-4">
                    {paymentStatus === 'pending' ? (
                      <div className="flex items-center justify-center gap-2 text-sm text-[#B8BCC4] animate-pulse">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Aguardando confirmação...
                      </div>
                    ) : (
                      <div className="flex items-center justify-center gap-2 text-emerald-400 font-bold">
                        <CheckCircle2 className="w-5 h-5" />
                        Pagamento Confirmado!
                      </div>
                    )}

                    <div className="space-y-3 pt-4">
                      <p className="text-[11px] text-[#B8BCC4] uppercase font-bold tracking-widest">Código PIX (Copia e Cola)</p>
                      <div className="flex gap-2">
                        <div className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-xs text-[#B8BCC4] truncate text-left font-mono">
                          {pixData?.pix_code}
                        </div>
                        <Button 
                          onClick={copyPixCode}
                          variant="secondary"
                          className="shrink-0 h-auto py-3 px-4 rounded-xl"
                        >
                          {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                        </Button>
                      </div>
                    </div>
                  </div>

                  <p className="text-[10px] text-[#B8BCC4]/40 font-light italic">
                    Abra o app do seu banco, selecione "Pagar com QR Code" ou "Pix Copia e Cola". 
                    Após o pagamento, seus créditos serão liberados instantaneamente.
                  </p>
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>

        {/* ── O que cada ensaio inclui ─────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="bg-[#121417] border border-[#1F2329] rounded-[32px] p-8 sm:p-14"
        >
          <h3 className="text-2xl sm:text-3xl font-serif font-semibold mb-8 sm:mb-10 text-center text-[#F5F5F7]">O que cada ensaio inclui?</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 sm:gap-8">
            {[
              { icon: Camera, title: '3 fotos de referência', desc: 'Envie fotos simples do celular' },
              { icon: Sparkles, title: 'Coleções editoriais', desc: 'Do clássico ao Vogue Style' },
              { icon: Clock, title: 'Pronto em segundos', desc: 'Resultado praticamente instantâneo' },
              { icon: Download, title: 'Alta resolução', desc: 'Para impressão e compartilhamento' },
            ].map((item, i) => (
              <div key={i} className="text-center space-y-3 sm:space-y-4 p-4 sm:p-6">
                <div className="w-14 h-14 rounded-2xl bg-[#748FCC]/10 border border-[#748FCC]/20 flex items-center justify-center mx-auto">
                  <item.icon className="w-6 h-6 text-[#748FCC]" />
                </div>
                <h4 className="text-base sm:text-lg font-semibold text-[#F5F5F7]">{item.title}</h4>
                <p className="text-sm text-[#B8BCC4] font-light">{item.desc}</p>
              </div>
            ))}
          </div>
        </motion.div>

        {/* ── Garantias ──────────────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-center space-y-6"
        >
          <div className="flex flex-col sm:flex-row items-center justify-center gap-6 sm:gap-10 text-[#B8BCC4]">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-[#748FCC]" />
              <span className="text-sm sm:text-base font-medium">Créditos nunca expiram</span>
            </div>
            <div className="hidden sm:block w-1 h-1 rounded-full bg-white/20" />
            <div className="flex items-center gap-2">
              <Star className="w-5 h-5 text-[#748FCC]" />
              <span className="text-sm sm:text-base font-medium">Satisfação garantida</span>
            </div>
            <div className="hidden sm:block w-1 h-1 rounded-full bg-white/20" />
            <div className="flex items-center gap-2">
              <Gem className="w-5 h-5 text-[#748FCC]" />
              <span className="text-sm sm:text-base font-medium">Pagamento 100% seguro</span>
            </div>
          </div>

          <div className="pt-6 space-y-4">
            <p className="text-xs sm:text-sm text-[#B8BCC4] font-light">
              Créditos insuficientes? Adquira mais e continue transformando memórias.
            </p>
            <p className="text-[10px] sm:text-[11px] uppercase tracking-[0.3em] text-[#B8BCC4]/30 font-bold">
              Ambiente de pagamento seguro · SyncPay Gateway · AureaIA™
            </p>
          </div>
        </motion.div>

      </div>
    </div>
  );
}
