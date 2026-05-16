'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Check, Sparkles, ShieldCheck, Gem, Star, Zap, 
  ArrowRight, Clock, Camera, Download, X, Copy, 
  CheckCircle2, Loader2, QrCode, CreditCard
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/services/api';
import { QRCodeSVG } from 'qrcode.react';

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
  order_id: string;
  qr_code_text: string;
  qr_code_image: string;
  package_name: string;
  amount: number;
}

export default function CreditsPage() {
  const { user, token, refreshUser } = useAuth();
  const [loading, setLoading] = useState(false);
  const [showPixModal, setShowPixModal] = useState(false);
  const [showCpfModal, setShowCpfModal] = useState(false);
  const [selectedPkg, setSelectedPkg] = useState<typeof PACKAGES[0] | null>(null);
  const [cpf, setCpf] = useState('');
  const [pixData, setPixData] = useState<PixData | null>(null);
  const [copied, setCopied] = useState(false);
  const [paymentStatus, setPaymentStatus] = useState<'pending' | 'completed' | 'failed'>('pending');
  const [notification, setNotification] = useState<{message: string, type: 'success' | 'error'} | null>(null);

  // Carregar CPF do usuário se existir
  useEffect(() => {
    if (user?.cpf) setCpf(user.cpf);
  }, [user]);

  // Função para copiar código PIX
  const copyPixCode = () => {
    if (pixData?.qr_code_text) {
      navigator.clipboard.writeText(pixData.qr_code_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  // Iniciar fluxo de compra
  const handlePackageSelect = (pkg: typeof PACKAGES[0]) => {
    if (!user) {
      setNotification({ message: 'Você precisa estar logado para comprar créditos.', type: 'error' });
      return;
    }
    setSelectedPkg(pkg);
    setShowCpfModal(true);
  };

  const handleGeneratePix = async () => {
    if (!selectedPkg || !cpf) return;
    
    // Validação básica de CPF (apenas números)
    const cleanCpf = cpf.replace(/\D/g, '');
    if (cleanCpf.length !== 11) {
      setNotification({ message: 'Por favor, informe um CPF válido.', type: 'error' });
      return;
    }

    setLoading(true);
    try {
      const response = await apiService.checkout.createPixPayment({
        amount: Math.round(selectedPkg.priceValue * 100),
        customer_name: user!.name,
        customer_email: user!.email,
        customer_tax_id: cleanCpf,
        package_id: selectedPkg.id
      }, token || undefined);
      
      if (response.success) {
        setPixData({
          order_id: response.order_id,
          qr_code_text: response.qr_code_text,
          qr_code_image: response.qr_code_image,
          package_name: selectedPkg.name,
          amount: selectedPkg.priceValue
        });
        setPaymentStatus('pending');
        setShowCpfModal(false);
        setShowPixModal(true);
      } else {
        setNotification({ message: response.error || 'Erro ao gerar PIX', type: 'error' });
      }
    } catch (error: any) {
      setNotification({ message: error.message || 'Erro de conexão', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // Polling de status do pagamento
  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (showPixModal && pixData?.order_id && paymentStatus === 'pending') {
      interval = setInterval(async () => {
        try {
          const response = await apiService.checkout.getOrderStatus(pixData.order_id, token || undefined);
          if (response.status === 'PAID') {
            setPaymentStatus('completed');
            setNotification({ message: 'Pagamento confirmado com sucesso!', type: 'success' });
            if (refreshUser) refreshUser();
            
            setTimeout(() => {
              setShowPixModal(false);
              setPixData(null);
              setSelectedPkg(null);
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

  // Limpar notificação
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

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

        {/* Modal CPF */}
        <AnimatePresence>
          {showCpfModal && (
            <div className="fixed inset-0 z-[150] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="bg-[#121417] border border-[#1F2329] rounded-[32px] w-full max-w-md p-8 sm:p-10 relative shadow-2xl"
              >
                <button onClick={() => setShowCpfModal(false)} className="absolute top-6 right-6 text-[#B8BCC4] hover:text-white"><X /></button>
                <div className="text-center space-y-6">
                  <div className="w-16 h-16 bg-[#748FCC]/10 rounded-full flex items-center justify-center mx-auto">
                    <CreditCard className="w-8 h-8 text-[#748FCC]" />
                  </div>
                  <h2 className="text-2xl font-serif font-semibold">Dados de Faturamento</h2>
                  <p className="text-sm text-[#B8BCC4] font-light">Para gerar o PIX com segurança, precisamos do seu CPF.</p>
                  <div className="space-y-4">
                    <input 
                      type="text" 
                      placeholder="000.000.000-00"
                      value={cpf}
                      onChange={(e) => setCpf(e.target.value)}
                      className="w-full h-14 bg-white/5 border border-white/10 rounded-xl px-6 text-center text-lg focus:border-[#748FCC] focus:ring-1 focus:ring-[#748FCC] outline-none transition-all"
                    />
                    <Button 
                      onClick={handleGeneratePix} 
                      disabled={loading || cpf.length < 11}
                      className="w-full h-14 rounded-xl"
                    >
                      {loading ? <Loader2 className="animate-spin mr-2" /> : null}
                      Gerar PIX Agora
                    </Button>
                  </div>
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>

        {/* Modal PIX */}
        <AnimatePresence>
          {showPixModal && (
            <div className="fixed inset-0 z-[150] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="bg-[#121417] border border-[#1F2329] rounded-[32px] w-full max-w-lg p-10 text-center space-y-8 relative shadow-2xl"
              >
                <button onClick={() => setShowPixModal(false)} className="absolute top-6 right-6 text-[#B8BCC4] hover:text-white"><X /></button>
                <div className="space-y-2">
                  <h2 className="text-2xl font-serif font-semibold">Finalize seu Pagamento</h2>
                  <p className="text-[#B8BCC4] font-light">Pacote {pixData?.package_name} · R$ {pixData?.amount.toFixed(2)}</p>
                </div>
                
                <div className="bg-white p-4 rounded-2xl inline-block">
                  {pixData?.qr_code_image ? (
                    <img src={pixData.qr_code_image} alt="PIX" className="w-[220px] h-[220px]" />
                  ) : (
                    <QRCodeSVG value={pixData?.qr_code_text || ''} size={220} />
                  )}
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-center gap-2 text-sm text-[#B8BCC4]">
                    {paymentStatus === 'pending' ? (
                      <><Loader2 className="animate-spin w-4 h-4" /> Aguardando pagamento...</>
                    ) : (
                      <span className="text-emerald-400 font-bold flex items-center gap-2"><CheckCircle2 /> Pagamento Confirmado!</span>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <div className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-xs text-[#B8BCC4] truncate font-mono">
                      {pixData?.qr_code_text}
                    </div>
                    <Button onClick={copyPixCode} variant="secondary" className="px-4">
                      {copied ? <Check className="text-emerald-400" /> : <Copy className="w-4 h-4" />}
                    </Button>
                  </div>
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>

        {/* Garantias */}
        <div className="bg-[#121417] border border-[#1F2329] rounded-[32px] p-14 text-center">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-10">
            <div className="space-y-4">
              <ShieldCheck className="w-10 h-10 text-[#748FCC] mx-auto" />
              <h4 className="font-semibold">Pagamento Seguro</h4>
              <p className="text-sm text-[#B8BCC4] font-light">Processado via PagSeguro PIX</p>
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
