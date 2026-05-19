'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/services/api';
import {
  Sparkles,
  Upload,
  Check,
  Loader2,
  AlertCircle,
  X,
  ChevronRight,
  Zap,
  Image as ImageIcon,
  Info
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';

// ─── Interface para os estilos ──────────────────────────────────────────────
interface Style {
  id: string;
  name: string;
  category?: string;
  description?: string;
  cover?: string;
  prompt?: string;
  [key: string]: any; // para outros campos opcionais que possam vir da API
}

// ─── Componente principal ─────────────────────────────────────────────────
export default function GeneratePage() {
  const { user, token, updateUser } = useAuth();
  const router = useRouter();

  const [styles, setStyles] = useState<Style[]>([]);
  const [selectedStyle, setSelectedStyle] = useState<Style | null>(null);
  const [loadingStyles, setLoadingStyles] = useState(true);
  const [imageFiles, setImageFiles] = useState<(File | null)[]>([null, null, null]);
  const [previewUrls, setPreviewUrls] = useState<(string | null)[]>([null, null, null]);
  const [prompt, setPrompt] = useState('');
  const [generating, setGenerating] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showCreditModal, setShowCreditModal] = useState(false);
  const { loading: authLoading } = useAuth();

  // ─── Proteger rota ────────────────────────────────────────────────────────
  React.useEffect(() => {
    if (!authLoading && !token) {
      router.push('/login');
    }
  }, [token, authLoading, router]);

  // ─── Carregar estilos do backend ──────────────────────────────────────────
  React.useEffect(() => {
    const fetchStyles = async () => {
      try {
        setLoadingStyles(true);
        // Usando a nova rota /api/styles conforme PDR 1.0.0
        const res = await apiService.get('/styles');
        if (res.styles) {
          const finalStyles = res.styles.map((s: Style) => {
            const coverUrl = s.cover?.startsWith('/thumbnails/')
              ? s.cover
              : (s.cover?.startsWith('http') && !s.cover.includes('picsum') ? s.cover : `/thumbnails/${s.id}.png`);
            return {
              ...s,
              cover: coverUrl
            };
          });

          setStyles(finalStyles);
          setSelectedStyle(finalStyles[0] || null);
        }
      } catch (err) {
        console.error("Erro ao carregar estilos:", err);
      } finally {
        setLoadingStyles(false);
      }
    };
    fetchStyles();
  }, []);

  // ─── Upload de imagem ─────────────────────────────────────────────────────
  const handleFileChange = (index: number, e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const newFiles = [...imageFiles];
      newFiles[index] = file;
      setImageFiles(newFiles);

      const newPreviews = [...previewUrls];
      newPreviews[index] = URL.createObjectURL(file);
      setPreviewUrls(newPreviews);
      setError(null);
    }
  };

  // ─── Gerar ensaio ────────────────────────────────────────────────────────
  const handleGenerate = async () => {
    const activeFiles = imageFiles.filter(f => f !== null) as File[];
    if (activeFiles.length < 3) {
      setError("Por favor, selecione 3 fotos para que possamos capturar sua essência com perfeição.");
      return;
    }
    if (!selectedStyle) return;

    // Verificação local de créditos (antes de chamar o backend)
    if ((user?.credits_balance || 0) < 25) {
      setShowCreditModal(true);
      return;
    }

    setGenerating(true);
    setError(null);

    try {
      const uploadedUrls: string[] = [];
      const apiUrl = (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000/api').replace(/\/api$/, '');

      // Upload das fotos da usuária
      for (const file of activeFiles) {
        const formData = new FormData();
        formData.append('file', file);

        const uploadRes = await fetch(`${apiUrl}/api/upload`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
          body: formData,
        });

        if (!uploadRes.ok) throw new Error("Não foi possível processar uma de suas fotos. Tente novamente.");
        const uploadData = await uploadRes.json();
        uploadedUrls.push(uploadData.file_url || uploadData.url);
      }

      // Solicitar geração ao backend
      const genRes = await apiService.post('/generate', {
        image_urls: uploadedUrls,
        style: selectedStyle.id,
        prompt: prompt
      }, token || undefined);

      if (genRes.success) {
        setSuccess(true);
        if (user) updateUser({ ...user, credits_balance: user.credits_balance - 25 });
        setTimeout(() => router.push('/gallery'), 3000);
      } else {
        // Tratar erro 402 — créditos insuficientes (resposta do backend)
        if (genRes.status === 402 || genRes.error?.includes('402') || genRes.error?.toLowerCase().includes('crédito')) {
          setShowCreditModal(true);
        } else {
          throw new Error(genRes.error || "Ocorreu um imprevisto em nosso estúdio.");
        }
      }
    } catch (err: any) {
      console.error(err);
      // Erro genérico com tom empático
      setError(err.message || "O estúdio está temporariamente ocupado. Por favor, tente novamente em breve.");
    } finally {
      setGenerating(false);
    }
  };

  // ─── Renderização ────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-[#0A0A0A] text-[#F5F5F7] flex flex-col lg:flex-row font-sans overflow-hidden">

      {/* ── Sidebar: Controles ─────────────────────────────────────────── */}
      <div className="w-full lg:w-[460px] bg-[#121417] border-r border-[#1F2329] p-6 md:p-8 lg:p-10 flex flex-col pt-24 lg:h-screen overflow-y-auto shrink-0 z-10">
        <div className="space-y-10">

          {/* Cabeçalho do painel */}
          <header className="space-y-4">
            <div className="flex items-center justify-between">
              <h1 className="text-3xl font-serif font-medium tracking-tight text-[#F5F5F7]">
                Ateliê de <span className="text-[#748FCC] italic">Criação</span>
              </h1>
              {/* Saldo de créditos com ícone elegante */}
              <div className="flex items-center gap-2 bg-white/5 px-4 py-1.5 rounded-full border border-white/8 shadow-sm" title="Seu saldo de moedas">
                <Zap className="w-3.5 h-3.5 text-[#748FCC]" />
                <span className="text-xs font-bold uppercase tracking-widest text-[#F5F5F7]/80">
                  ✦ {user?.credits_balance || 0}
                </span>
              </div>
            </div>
            <p className="text-sm text-[#B8BCC4] leading-relaxed font-light">
              Transforme seus traços em uma obra-prima editorial. Nossa inteligência artística cuidará de cada detalhe com a delicadeza que sua jornada merece.
            </p>
          </header>

          {/* Seção 1 — Fotos de referência */}
          <section className="space-y-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-6 h-6 rounded-full bg-white/5 border border-white/8 flex items-center justify-center text-[#748FCC] shadow-sm">
                <span className="text-xs font-bold">1</span>
              </div>
              <label className="text-[10px] font-bold text-[#B8BCC4] uppercase tracking-[0.2em]">
                Sua Essência (Mín. 3 fotos)
              </label>
            </div>

            {/* Grid de upload — layout preservado */}
            <div className="grid grid-cols-3 gap-4">
              {[0, 1, 2].map((idx) => (
                <label key={idx} className={`block group aspect-[3/4] ${generating ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}`}>
                  <input type="file" className="hidden" disabled={generating} onChange={(e) => handleFileChange(idx, e)} accept="image/*" />
                  <div className={`w-full h-full rounded-[24px] border-2 border-dashed transition-all duration-500 flex flex-col items-center justify-center relative overflow-hidden bg-black/20 ${previewUrls[idx] ? 'border-[#748FCC]' : 'border-[#1F2329] hover:border-[#748FCC]/50'
                    }`}>
                    {previewUrls[idx] ? (
                      <img src={previewUrls[idx]!} className="w-full h-full object-cover" alt={`Foto ${idx + 1}`} />
                    ) : (
                      <div className="flex flex-col items-center gap-2">
                        <Upload className="w-5 h-5 text-white/20 group-hover:text-[#748FCC] transition-colors" />
                        <span className="text-[9px] text-white/20 font-bold uppercase tracking-widest">Upload</span>
                      </div>
                    )}
                  </div>
                </label>
              ))}
            </div>

            {/* Dica */}
            <div className="flex items-start gap-2 p-4 bg-white/5 rounded-[16px] border border-white/8">
              <Info className="w-4 h-4 text-[#748FCC] shrink-0 mt-0.5" />
              <p className="text-[11px] text-[#B8BCC4] leading-relaxed italic font-light">
                Dica: Fotos de rosto bem iluminadas e naturais permitem uma criação mais fiel à sua beleza real.
              </p>
            </div>
          </section>

          {/* Seção 2 — Toque especial (Importante) */}
          <section className="space-y-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-6 h-6 rounded-full bg-white/5 border border-white/8 flex items-center justify-center text-[#748FCC] shadow-sm">
                <span className="text-xs font-bold">2</span>
              </div>
              <label className="text-[10px] font-bold text-[#B8BCC4] uppercase tracking-[0.2em]">
                Sua Descrição Física (Importante)
              </label>
            </div>

            <div className="flex items-start gap-2 p-3 bg-[#748FCC]/10 rounded-[12px] border border-[#748FCC]/20">
              <Info className="w-4 h-4 text-[#748FCC] shrink-0 mt-0.5" />
              <p className="text-[11px] text-[#B8BCC4] leading-relaxed">
                <strong className="text-[#F5F5F7]">Modelo Ultra Realista:</strong> Este novo motor gera resultados de altíssima qualidade, mas <strong>não preserva a identidade facial exata</strong> das fotos. Descreva suas características (cor do cabelo, pele, etnia) para um resultado mais parecido com você.
              </p>
            </div>

            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Ex: Mulher de pele morena, cabelos cacheados escuros, olhos castanhos..."
              className="w-full h-24 p-4 rounded-[16px] bg-[#0A0A0A] border border-[#1F2329] focus:border-[#748FCC] focus:outline-none text-sm placeholder:text-[#F5F5F7]/10 transition-all resize-none font-light"
            />
          </section>

          {/* Botão de ação principal */}
          <div className="pt-4 space-y-4">
            <Button
              onClick={handleGenerate}
              isLoading={generating}
              disabled={generating || imageFiles.filter(f => f !== null).length < 3}
              className="w-full h-16 text-lg bg-[#748FCC] hover:bg-[#5F7DB8] hover:shadow-[0_0_40px_rgba(116,143,204,0.35)]"
            >
              Criar Obra-prima
              <Sparkles className="w-5 h-5" />
            </Button>
            <div className="flex items-center justify-center gap-3 text-[9px] font-bold text-[#B8BCC4]/20 uppercase tracking-[0.3em]">
              <div className="h-[1px] w-8 bg-white/5" />
              <span>✦ Investimento: 25 Créditos</span>
              <div className="h-[1px] w-8 bg-white/5" />
            </div>
          </div>
        </div>
      </div>

      {/* ── Área principal: Seleção de estilo ─────────────────────────── */}
      {/* Layout de grid preservado integralmente */}
      <div className="flex-1 lg:h-screen overflow-y-auto p-6 md:p-10 lg:p-16 bg-[#0A0A0A] relative pt-12 lg:pt-32 z-10">
        <div className="max-w-5xl mx-auto space-y-12">
          <header className="space-y-4">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/5 border border-white/8 text-[#748FCC] font-bold text-[10px] tracking-[0.2em] uppercase">
              <ImageIcon className="w-3.5 h-3.5" /> Coleção Editorial 2026
            </div>
            <h2 className="text-4xl md:text-5xl font-serif font-medium tracking-tight text-[#F5F5F7]">
              Escolha sua <span className="text-[#748FCC] italic">Ambientação</span>
            </h2>
            <p className="text-[#B8BCC4] max-w-2xl font-light text-lg">
              Cada cenário foi cuidadosamente curado para exaltar a sofisticação e o amor desse momento sagrado.
            </p>
          </header>

          {/* Grid de estilos — layout e comportamento preservados */}
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-8">
            {loadingStyles ? (
              // Esqueleto de carregamento elegante
              Array(4).fill(0).map((_, i) => (
                <div key={i} className="aspect-[4/5] rounded-[32px] bg-[#121417] animate-pulse border border-[#1F2329]" />
              ))
            ) : (
              styles.map((style) => (
                <motion.div
                  key={style.id}
                  whileHover={!generating ? { y: -10 } : undefined}
                  onClick={() => !generating && setSelectedStyle(style)}
                  className={`group relative rounded-[32px] overflow-hidden border-2 transition-all duration-700 aspect-[4/5] ${generating ? 'cursor-not-allowed' : 'cursor-pointer'
                    } ${selectedStyle?.id === style.id
                      ? 'border-[#748FCC] shadow-2xl bg-[#121417]'
                      : 'border-[#1F2329] hover:border-[#748FCC]/30 bg-[#121417]'
                    }`}
                >
                  <div className="absolute inset-0 bg-white/5 opacity-0 group-hover:opacity-10 transition-opacity" />
                  <img
                    src={`/thumbnails/${style.id}.png`}
                    alt={style.name}
                    className={`w-full h-full object-cover transition-all duration-[2s] group-hover:scale-110 ${selectedStyle?.id === style.id ? 'opacity-100 scale-110' : 'opacity-40 scale-105 group-hover:opacity-80'
                      }`}
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black via-black/20 to-transparent" />

                  <div className="absolute bottom-8 left-8 right-8">
                    <span className="text-[9px] font-bold uppercase tracking-[0.3em] text-[#748FCC] mb-2 block">{style.category}</span>
                    <h3 className="text-xl font-medium text-[#F5F5F7] mb-2">{style.name}</h3>
                    <p className={`text-[11px] text-[#B8BCC4] leading-relaxed transition-all duration-500 line-clamp-2 font-light ${selectedStyle?.id === style.id ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'
                      }`}>
                      {style.description}
                    </p>
                  </div>

                  <div className={`absolute top-6 right-6 w-10 h-10 rounded-full flex items-center justify-center transition-all duration-500 ${selectedStyle?.id === style.id ? 'bg-[#748FCC] text-white scale-100' : 'bg-black/50 text-white scale-0 group-hover:scale-100'
                    }`}>
                    <Check className="w-5 h-5" />
                  </div>
                </motion.div>
              )))}
          </div>
        </div>
      </div>

      {/* ── Overlay de geração / sucesso ──────────────────────────────── */}
      <AnimatePresence>
        {(generating || success) && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-[200] bg-[#0A0A0A]/95 backdrop-blur-xl flex flex-col items-center justify-center p-8 text-center"
          >
            <Loader2 className="w-12 h-12 text-[#748FCC] animate-spin mb-8" />
            <h2 className="text-3xl font-serif font-medium text-[#F5F5F7] mb-4">
              {success ? 'Sua obra-prima está sendo preparada...' : 'Iniciando a Criação Artística'}
            </h2>
            <p className="text-[#B8BCC4] font-light text-lg max-w-lg leading-relaxed">
              {success
                ? 'Em breve você poderá contemplar seu ensaio em sua Galeria Privada.'
                : 'Estamos combinando sua essência com as texturas e luzes de nossa coleção editorial.'}
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Modal de créditos insuficientes (erro 402) ─────────────────── */}
      <AnimatePresence>
        {showCreditModal && (
          <div className="fixed inset-0 z-[300] bg-black/80 backdrop-blur-sm flex items-center justify-center p-6">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
              className="bg-[#121417] border border-[#1F2329] p-10 rounded-[24px] max-w-md w-full text-center space-y-8"
            >
              <div className="w-16 h-16 rounded-full bg-[#748FCC]/20 flex items-center justify-center mx-auto">
                <Sparkles className="w-8 h-8 text-[#748FCC]" />
              </div>
              <div className="space-y-4">
                <h3 className="text-2xl font-serif font-medium text-[#F5F5F7]">Créditos insuficientes</h3>
                {/* Mensagem obrigatória conforme briefing */}
                <p className="text-[#B8BCC4] font-light leading-relaxed">
                  Créditos insuficientes para criar esta obra.<br />
                  Adquira um pacote e continue eternizando momentos únicos.
                </p>
              </div>
              <div className="flex flex-col gap-4">
                <Button onClick={() => router.push('/credits')} className="h-12 bg-[#748FCC] hover:bg-[#5F7DB8]">
                  Adquirir Créditos ✦
                </Button>
                <button
                  onClick={() => setShowCreditModal(false)}
                  className="text-[#B8BCC4] hover:text-[#F5F5F7] transition-colors text-sm"
                >
                  Voltar ao Estúdio
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ── Toast de erro ─────────────────────────────────────────────── */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 20 }}
            className="fixed bottom-10 left-1/2 -translate-x-1/2 z-[300] bg-white text-black px-6 py-4 rounded-full flex items-center gap-4 shadow-2xl"
          >
            <AlertCircle className="w-5 h-5 text-red-500 shrink-0" />
            <span className="text-sm font-medium">{error}</span>
            <button onClick={() => setError(null)} aria-label="Fechar">
              <X className="w-4 h-4 text-[#8E8E93]" />
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}