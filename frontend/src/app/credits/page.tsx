'use client';

import React, { useState, useEffect, Suspense, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Check, Sparkles, ShieldCheck, Gem, Star, Zap,
  ArrowRight, Clock, X, CheckCircle2, Copy, QrCode, CreditCard,
  Loader2,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useAuth } from '@/contexts/AuthContext';
import { useSearchParams, useRouter } from 'next/navigation';
import { usePageTitle } from '@/hooks/usePageTitle';
import { apiService } from '@/services/api';

const PACKAGES = [
  {
    id: '100_credits', name: 'Essencial', credits: 100, price: '25',
    priceValue: 25.00, icon: Zap, badge: null,
    description: 'Ideal para experimentar nossa qualidade e criar seus primeiros ensaios.',
    features: ['4 ensaios completos', 'Acesso a todos os estilos', 'Download em alta resolução', 'Créditos nunca expiram'],
  },
  {
    id: '200_credits', name: 'Ateliê', credits: 200, price: '50',
    priceValue: 50.00, popular: true, icon: Sparkles, badge: '✦ Mais Escolhido',
    description: 'O equilíbrio perfeito para explorar múltiplos estilos com agilidade.',
    features: ['8 ensaios completos', 'Acesso a todos os estilos', 'Download em alta resolução', 'Créditos nunca expiram', 'Prioridade na fila'],
  },
  {
    id: '400_credits', name: 'Maison', credits: 400, price: '120',
    priceValue: 120.00, icon: Gem, badge: 'VIP',
    description: 'Para quem deseja a experiência completa de estúdio e suporte exclusivo.',
    features: ['16 ensaios completos', 'Acesso a todos os estilos', 'Download em alta resolução', 'Créditos nunca expiram', 'Suporte prioritário'],
  },
];

type PaymentTab = 'pix' | 'card';

function CreditsContent() {
  usePageTitle('Créditos');
  const { user, token, refreshUser } = useAuth();
  const searchParams = useSearchParams();
  const router = useRouter();
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  const [selectedPkg, setSelectedPkg] = useState<typeof PACKAGES[0] | null>(null);
  const [paymentTab, setPaymentTab] = useState<PaymentTab>('pix');
  const [loading, setLoading] = useState(false);
  const [qrCodeBase64, setQrCodeBase64] = useState('');
  const [qrCodeText, setQrCodeText] = useState('');
  const [pixPaymentId, setPixPaymentId] = useState<string | null>(null);
  const [pixCopied, setPixCopied] = useState(false);
  const [checkoutUrl, setCheckoutUrl] = useState<string | null>(null);

  useEffect(() => {
    if (searchParams.get('success') === 'true') {
      setNotification({ message: 'Pagamento confirmado! Atualizando saldo...', type: 'success' });
      refreshUser().then(() => {
        setNotification({ message: 'Créditos atualizados com sucesso!', type: 'success' });
      });
      router.replace('/credits');
    }
  }, [searchParams, refreshUser, router]);

  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  useEffect(() => {
    if (!pixPaymentId) return;
    const interval = setInterval(async () => {
      try {
        const res = await apiService.get(`/payment-status/${pixPaymentId}`, token || '');
        if (res?.status === 'RECEIVED' || res?.status === 'CONFIRMED') {
          clearInterval(interval);
          setSelectedPkg(null);
          setPixPaymentId(null);
          setQrCodeBase64('');
          setNotification({ message: 'Pagamento aprovado! Créditos adicionados.', type: 'success' });
          await refreshUser();
        }
      } catch { }
    }, 3000);
    return () => clearInterval(interval);
  }, [pixPaymentId, token, refreshUser]);



  const notify = useCallback((msg: string, type: 'success' | 'error') => {
    setNotification({ message: msg, type });
  }, []);

  const handleSelectPkg = (pkg: typeof PACKAGES[0]) => {
    if (!user) { notify('Você precisa estar logado para comprar créditos.', 'error'); return; }
    if (!token) { notify('Sessão inválida. Faça login novamente.', 'error'); return; }
    setSelectedPkg(pkg);
    setPaymentTab('pix');
    setQrCodeBase64('');
    setQrCodeText('');
    setPixPaymentId(null);
    setPixCopied(false);
    setCheckoutUrl(null);
  };

  const handlePixPayment = async () => {
    if (!selectedPkg || !user || !token) return;
    setLoading(true);
    try {
      const externalRef = `${user.id}:${selectedPkg.id}`;
      const res = await apiService.post('/create-pix-payment', {
        external_reference: externalRef,
        value: selectedPkg.priceValue,
        description: selectedPkg.name,
      }, token);
      if (res?.success) {
        setQrCodeBase64(res.qr_code_base64 || '');
        setQrCodeText(res.qr_code || '');
        setPixPaymentId(res.payment_id);
        notify('QR Code gerado! Escaneie com seu banco.', 'success');
      } else {
        notify(res?.error || 'Erro ao gerar PIX.', 'error');
      }
    } catch {
      notify('Erro de conexão ao gerar PIX.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const copyPixCode = () => {
    if (qrCodeText) {
      navigator.clipboard.writeText(qrCodeText);
      setPixCopied(true);
      setTimeout(() => setPixCopied(false), 2000);
    }
  };

  const handleCardPayment = async () => {
    if (!selectedPkg || !user || !token) return;
    setLoading(true);
    try {
      const externalRef = `${user.id}:${selectedPkg.id}`;
      const res = await apiService.post('/create-card-payment', {
        external_reference: externalRef,
        value: selectedPkg.priceValue,
        description: selectedPkg.name,
      }, token);
      if (res?.success && res.checkout_url) {
        setCheckoutUrl(res.checkout_url);
        window.open(res.checkout_url, '_blank');
        notify('Redirecionando para o Asaas...', 'success');
      } else {
        notify(res?.error || 'Erro ao gerar checkout.', 'error');
      }
    } catch {
      notify('Erro ao processar cartão.', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-[#F5F5F7] pt-24 pb-32 px-4 sm:px-6 relative overflow-x-hidden">
      <AnimatePresence>
        {notification && (
          <motion.div
            initial={{ opacity: 0, y: -50, x: '-50%' }}
            animate={{ opacity: 1, y: 20, x: '-50%' }}
            exit={{ opacity: 0, y: -50, x: '-50%' }}
            className={`fixed top-4 left-1/2 z-[200] px-6 py-3 rounded-full shadow-2xl flex items-center gap-3 border ${notification.type === 'success'
              ? 'bg-emerald-500/90 border-emerald-400 text-white'
              : 'bg-red-500/90 border-red-400 text-white'}`}
          >
            {notification.type === 'success' ? <CheckCircle2 className="w-5 h-5" /> : <X className="w-5 h-5" />}
            <span className="text-sm font-bold">{notification.message}</span>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="max-w-[1300px] mx-auto space-y-16 sm:space-y-24">
        <motion.header initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
          className="text-center space-y-6 max-w-3xl mx-auto pt-8">
          <div className="inline-flex items-center gap-3 px-5 py-2 rounded-full bg-[#748FCC]/20 border border-[#748FCC]/30 text-[#F5F5F7] text-[10px] font-bold tracking-[0.3em] uppercase">
            <Sparkles className="w-4 h-4" /> Preço justo, resultado de estúdio
          </div>
          <h1 className="text-4xl sm:text-7xl font-serif font-semibold tracking-tight leading-[1.05]">
            Invista em memórias<br /><span className="italic text-[#B8BCC4]">que duram para sempre.</span>
          </h1>
          {user && (
            <div className="inline-flex items-center gap-3 bg-white/5 border border-white/10 px-6 py-3 rounded-full">
              <span className="text-sm font-bold text-[#F5F5F7] tracking-wide">✦ Seu saldo: {user.credits_balance} moedas</span>
            </div>
          )}
        </motion.header>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8 max-w-sm sm:max-w-none mx-auto">
          {PACKAGES.map((pkg, idx) => (
            <motion.div key={pkg.id} initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }} className="flex w-full">
              <div className={`flex-1 flex flex-col rounded-[28px] overflow-hidden transition-all duration-500 relative ${pkg.popular
                ? 'bg-gradient-to-b from-[#748FCC]/20 to-[#0D0D0D] border-2 border-[#748FCC]/50 shadow-2xl scale-[1.02]'
                : 'bg-[#121417] border border-[#1F2329] hover:border-[#748FCC]/20'}`}>
                {pkg.badge && (
                  <div className={`absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 text-[10px] font-bold uppercase tracking-widest px-5 py-1.5 rounded-full z-10 ${pkg.popular ? 'bg-[#748FCC] text-[#F5F5F7]' : 'bg-white/10 text-[#F5F5F7]/80'}`}>
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
                    <p className="text-[13px] sm:text-sm text-[#B8BCC4] font-light leading-relaxed">{pkg.description}</p>
                  </div>
                  <div className="space-y-4 flex-1 mb-8 sm:mb-10">
                    {pkg.features.map((feat, i) => (
                      <div key={i} className="flex items-start gap-3">
                        <Check className="w-5 h-5 text-[#748FCC] shrink-0 mt-0.5" />
                        <span className="text-[13px] sm:text-sm font-light text-[#B8BCC4]">{feat}</span>
                      </div>
                    ))}
                  </div>
                  <Button onClick={() => handleSelectPkg(pkg)}
                    variant={pkg.popular ? 'primary' : 'secondary'}
                    className={`w-full py-4 h-auto text-[13px] sm:text-sm font-bold tracking-[0.1em] rounded-xl sm:rounded-2xl group transition-all duration-300 ${pkg.popular
                      ? 'bg-[#748FCC] hover:bg-[#5F7DB8] hover:shadow-[0_0_30px_rgba(116,143,204,0.3)] text-white border-none'
                      : 'bg-white/5 hover:bg-white/10 text-[#F5F5F7] border border-white/10'}`}>
                    Adquirir Pacote
                    <ArrowRight className="w-4 h-4 ml-2 transition-transform group-hover:translate-x-1" />
                  </Button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        <div className="bg-[#121417] border border-[#1F2329] rounded-[24px] sm:rounded-[32px] p-8 sm:p-14 text-center">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 sm:gap-10">
            <div className="space-y-3 sm:space-y-4">
              <ShieldCheck className="w-8 h-8 sm:w-10 sm:h-10 text-[#748FCC] mx-auto" />
              <h4 className="font-semibold text-sm sm:text-base">Pagamento Seguro</h4>
              <p className="text-[13px] sm:text-sm text-[#B8BCC4] font-light">Processado via Asaas</p>
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

      <AnimatePresence>
        {selectedPkg && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[500] bg-black/70 backdrop-blur-sm flex items-center justify-center p-4"
            onClick={() => { if (!loading) setSelectedPkg(null); }}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e: React.MouseEvent) => e.stopPropagation()}
              className="bg-[#121417] border border-[#1F2329] rounded-[28px] max-w-lg w-full max-h-[90vh] overflow-y-auto p-6 sm:p-8"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold">{selectedPkg.name} — {selectedPkg.credits} créditos</h2>
                <button onClick={() => { if (!loading) setSelectedPkg(null); }}
                  className="text-[#B8BCC4] hover:text-white transition-colors">
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="text-center mb-6">
                <span className="text-3xl font-bold">R$ {selectedPkg.price}</span>
              </div>

              <div className="flex gap-2 mb-6">
                <button onClick={() => setPaymentTab('pix')}
                  className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-bold transition-all ${paymentTab === 'pix' ? 'bg-[#748FCC] text-white' : 'bg-white/5 text-[#B8BCC4] hover:bg-white/10'}`}>
                  <QrCode className="w-4 h-4" /> PIX
                </button>
                <button onClick={() => setPaymentTab('card')}
                  className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-bold transition-all ${paymentTab === 'card' ? 'bg-[#748FCC] text-white' : 'bg-white/5 text-[#B8BCC4] hover:bg-white/10'}`}>
                  <CreditCard className="w-4 h-4" /> Cartão
                </button>
              </div>

              {paymentTab === 'pix' && (
                <div className="space-y-4">
                  {!qrCodeBase64 ? (
                    <Button onClick={handlePixPayment} isLoading={loading}
                      className="w-full py-4 bg-[#748FCC] hover:bg-[#5F7DB8] text-white rounded-xl font-bold">
                      Gerar QR Code PIX
                    </Button>
                  ) : (
                    <div className="text-center space-y-4">
                      <img src={`data:image/png;base64,${qrCodeBase64}`} alt="QR Code PIX"
                        className="w-56 h-56 mx-auto rounded-xl bg-white p-2" />
                      <p className="text-sm text-[#B8BCC4]">Escaneie o QR Code com seu banco ou copie o código:</p>
                      <div className="flex gap-2">
                        <input readOnly value={qrCodeText}
                          className="flex-1 bg-[#0A0A0A] border border-[#1F2329] rounded-xl px-4 py-3 text-xs text-[#B8BCC4] truncate" />
                        <Button onClick={copyPixCode}
                          className="bg-white/5 hover:bg-white/10 border border-white/10 text-white px-4 rounded-xl">
                          {pixCopied ? <CheckCircle2 className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                        </Button>
                      </div>
                      <div className="flex items-center justify-center gap-2 text-sm text-emerald-400">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Aguardando pagamento...
                      </div>
                    </div>
                  )}
                </div>
              )}

              {paymentTab === 'card' && !checkoutUrl && (
                <div className="space-y-5">
                  <div className="bg-gradient-to-br from-[#1a1d24] to-[#0D0D0D] border border-[#2a2f38] rounded-2xl p-5 overflow-hidden relative">
                    <div className="absolute -top-10 -right-10 w-32 h-32 bg-[#748FCC]/10 rounded-full blur-3xl" />
                    <div className="absolute -bottom-8 -left-8 w-24 h-24 bg-[#748FCC]/5 rounded-full blur-2xl" />
                    <div className="relative z-10">
                      <div className="flex items-center justify-between mb-5">
                        <span className="text-[10px] font-bold uppercase tracking-[0.25em] text-[#8A9099]">Pagamento Seguro</span>
                        <div className="flex gap-1.5">
                          <div className="w-6 h-4 rounded bg-gradient-to-br from-red-400 to-red-600" />
                          <div className="w-6 h-4 rounded bg-gradient-to-br from-yellow-300 to-yellow-500" />
                        </div>
                      </div>
                      <div className="flex items-center gap-4 mb-4">
                        <div className="w-12 h-12 rounded-full bg-[#748FCC]/15 border border-[#748FCC]/20 flex items-center justify-center shrink-0">
                          <ShieldCheck className="w-6 h-6 text-[#748FCC]" />
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-white">Checkout Asaas</p>
                          <p className="text-xs text-[#8A9099]">Ambiente certificado PCI</p>
                        </div>
                      </div>
                      <p className="text-xs text-[#8A9099] leading-relaxed">
                        Você será redirecionado para o ambiente seguro do Asaas. 
                        Seus dados bancários serão preenchidos diretamente lá — 
                        <span className="text-emerald-400 font-semibold"> nós nunca armazenamos</span> números de cartão ou CVV.
                      </p>
                    </div>
                  </div>

                  <Button onClick={handleCardPayment} isLoading={loading}
                    className="w-full py-4 bg-gradient-to-r from-[#748FCC] to-[#5F7DB8] hover:from-[#5F7DB8] hover:to-[#4D6BA8] text-white rounded-xl font-bold shadow-lg shadow-[#748FCC]/20 hover:shadow-[#748FCC]/30 transition-all duration-300">
                    Pagar R$ {selectedPkg.price} com Cartão
                  </Button>

                  <div className="flex items-center justify-center gap-3 text-[10px] text-[#8A9099]">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    Dados protegidos — ambiente Asaas
                  </div>
                </div>
              )}
              {paymentTab === 'card' && checkoutUrl && (
                <div className="text-center space-y-4 py-8">
                  <div className="w-16 h-16 rounded-full bg-[#748FCC]/10 border border-[#748FCC]/20 flex items-center justify-center mx-auto">
                    <Loader2 className="w-7 h-7 text-[#748FCC] animate-spin" />
                  </div>
                  <p className="text-sm font-medium text-[#F5F5F7]">Aguardando pagamento...</p>
                  <p className="text-xs text-[#8A9099]">Finalize o pagamento na nova aba. Esta página será atualizada automaticamente.</p>
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
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
