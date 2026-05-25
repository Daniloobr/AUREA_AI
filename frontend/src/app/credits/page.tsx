'use client';

import React, { useState, useEffect, Suspense, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Check, Sparkles, ShieldCheck, Gem, Star, Zap,
  ArrowRight, Clock, X, CheckCircle2, Copy, QrCode, CreditCard,
  Loader2, AlertCircle,
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

  const [cardNumber, setCardNumber] = useState('');
  const [cardName, setCardName] = useState('');
  const [cardExpiry, setCardExpiry] = useState('');
  const [cardCvv, setCardCvv] = useState('');
  const [cardDoc, setCardDoc] = useState('');

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
          setNotification({ message: 'PIX aprovado! Créditos adicionados.', type: 'success' });
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
    setCardNumber('');
    setCardName('');
    setCardExpiry('');
    setCardCvv('');
    setCardDoc('');
  };

  const handlePixPayment = async () => {
    if (!selectedPkg || !token) return;
    setLoading(true);
    try {
      const res = await apiService.post('/create-pix-payment', { package_id: selectedPkg.id }, token);
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
    if (!selectedPkg || !token) return;
    if (!cardNumber || !cardName || !cardExpiry || !cardCvv) {
      notify('Preencha todos os campos do cartão.', 'error');
      return;
    }
    setLoading(true);
    try {
      const [month, year] = cardExpiry.split('/').map(s => s.trim());
      const fullYear = year.length === 2 ? `20${year}` : year;
      const res = await apiService.post('/create-card-payment-direct', {
        package_id: selectedPkg.id,
        card_number: cardNumber.replace(/\s/g, ''),
        card_expiration_month: month,
        card_expiration_year: fullYear,
        card_cvv: cardCvv,
        card_holder_name: cardName,
      }, token);
      if (res?.success) {
        if (res.status === 'CONFIRMED') {
          setSelectedPkg(null);
          notify('Pagamento aprovado! Créditos adicionados.', 'success');
          await refreshUser();
        } else {
          notify(`Pagamento ${res.status}: tente novamente.`, 'error');
        }
      } else {
        notify(res?.error || 'Erro ao processar cartão.', 'error');
      }
    } catch (err: any) {
      notify(err?.message || 'Erro ao processar cartão.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const formatCardNumber = (v: string) => v.replace(/\D/g, '').replace(/(\d{4})(?=\d)/g, '$1 ').slice(0, 19);
  const formatExpiry = (v: string) => v.replace(/\D/g, '').replace(/^(\d{2})(\d)/, '$1/$2').slice(0, 5);

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

      {/* Payment Modal */}
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

              {/* Tabs */}
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

              {paymentTab === 'card' && (
                <div className="space-y-4">
                  <div>
                    <label className="text-[11px] font-bold text-[#B8BCC4] uppercase tracking-widest ml-1">Número do Cartão</label>
                    <input value={cardNumber} onChange={(e) => setCardNumber(formatCardNumber(e.target.value))}
                      placeholder="5031 4332 1540 7451"
                      className="w-full mt-1 h-12 px-4 rounded-xl bg-[#0A0A0A] border border-[#1F2329] focus:border-[#748FCC] focus:outline-none text-[#F5F5F7] placeholder:text-[#8A9099]/30" />
                  </div>
                  <div>
                    <label className="text-[11px] font-bold text-[#B8BCC4] uppercase tracking-widest ml-1">Nome no Cartão</label>
                    <input value={cardName} onChange={(e) => setCardName(e.target.value)}
                      placeholder="Nome como está no cartão"
                      className="w-full mt-1 h-12 px-4 rounded-xl bg-[#0A0A0A] border border-[#1F2329] focus:border-[#748FCC] focus:outline-none text-[#F5F5F7] placeholder:text-[#8A9099]/30" />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-[11px] font-bold text-[#B8BCC4] uppercase tracking-widest ml-1">Validade</label>
                      <input value={cardExpiry} onChange={(e) => setCardExpiry(formatExpiry(e.target.value))}
                        placeholder="MM/AA"
                        className="w-full mt-1 h-12 px-4 rounded-xl bg-[#0A0A0A] border border-[#1F2329] focus:border-[#748FCC] focus:outline-none text-[#F5F5F7] placeholder:text-[#8A9099]/30" />
                    </div>
                    <div>
                      <label className="text-[11px] font-bold text-[#B8BCC4] uppercase tracking-widest ml-1">CVV</label>
                      <input value={cardCvv} onChange={(e) => setCardCvv(e.target.value.replace(/\D/g, '').slice(0, 4))}
                        placeholder="123"
                        className="w-full mt-1 h-12 px-4 rounded-xl bg-[#0A0A0A] border border-[#1F2329] focus:border-[#748FCC] focus:outline-none text-[#F5F5F7] placeholder:text-[#8A9099]/30" />
                    </div>
                  </div>
                  <div>
                    <label className="text-[11px] font-bold text-[#B8BCC4] uppercase tracking-widest ml-1">CPF</label>
                    <input value={cardDoc} onChange={(e) => setCardDoc(e.target.value.replace(/\D/g, '').slice(0, 11))}
                      placeholder="000.000.000-00"
                      className="w-full mt-1 h-12 px-4 rounded-xl bg-[#0A0A0A] border border-[#1F2329] focus:border-[#748FCC] focus:outline-none text-[#F5F5F7] placeholder:text-[#8A9099]/30" />
                  </div>
                  <Button onClick={handleCardPayment} isLoading={loading}
                    className="w-full py-4 bg-[#748FCC] hover:bg-[#5F7DB8] text-white rounded-xl font-bold">
                    Pagar R$ {selectedPkg.price}
                  </Button>
                  <p className="text-[10px] text-[#8A9099] text-center">
                    Pagamento processado via Asaas. Seus dados são seguros.
                  </p>
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
