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
  Image as ImageIcon
} from 'lucide-react';
import { useRouter } from 'next/navigation';

const STYLES = [
  { 
    id: 'gestante_outdoor', 
    name: 'Essência Natural', 
    category: 'Gestante',
    cover: '/ensaios/Gestante ao Ar Livre.png',
  },
  { 
    id: 'gestante_editorial', 
    name: 'Editorial Vogue', 
    category: 'Gestante',
    cover: '/ensaios/Capa de Revista.png',
  },
  { 
    id: 'gestante_minimal', 
    name: 'Minimalismo Studio', 
    category: 'Gestante',
    cover: '/ensaios/flux_1778631244_7078.png',
  },
  { 
    id: 'bebe_neutro', 
    name: 'Doce Ternura', 
    category: 'Infantil',
    cover: '/ensaios/flux_1778631244_7078.png',
  },
  { 
    id: 'bebe_fantasia', 
    name: 'Reino Encantado', 
    category: 'Infantil',
    cover: '/ensaios/Gestante ao Ar Livre.png',
  },
];

export default function GeneratePage() {
  const { user, token, updateUser } = useAuth();
  const router = useRouter();
  
  const [selectedStyle, setSelectedStyle] = useState<any>(STYLES[0]);
  const [imageFiles, setImageFiles] = useState<(File | null)[]>([null, null, null]);
  const [previewUrls, setPreviewUrls] = useState<(string | null)[]>([null, null, null]);
  const [generating, setGenerating] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  const handleGenerate = async () => {
    const activeFiles = imageFiles.filter(f => f !== null) as File[];
    if (activeFiles.length < 3) {
      setError("Por favor, envie ao menos 3 fotos para uma captura premium de identidade.");
      return;
    }
    if (!selectedStyle) return;
    
    setGenerating(true);
    setError(null);

    try {
      // 1. Upload all images
      const uploadedUrls: string[] = [];
      const apiUrl = (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000/api').replace(/\/api$/, '');

      for (const file of activeFiles) {
        const formData = new FormData();
        formData.append('file', file);
        
        const uploadRes = await fetch(`${apiUrl}/api/upload`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
          body: formData,
        });

        if (!uploadRes.ok) throw new Error("Falha no upload de uma das fotos.");
        const uploadData = await uploadRes.json();
        uploadedUrls.push(uploadData.file_url || uploadData.url);
      }
      
      // 2. Start generation with all URLs
      const genRes = await apiService.post('/generate', {
        image_urls: uploadedUrls, // Send as array
        style: selectedStyle.id
      }, token || undefined);

      if (genRes.success) {
        setSuccess(true);
        if (user) updateUser({ ...user, credits_balance: user.credits_balance - 25 });
        setTimeout(() => router.push('/history'), 3000);
      } else {
        throw new Error(genRes.error || "Erro ao iniciar a geração.");
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Erro de conexão com o servidor.");
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-onyx-950 text-white flex flex-col lg:flex-row font-inter overflow-hidden">
      
      {/* Coluna Esquerda: Controle de Produção (FIXA) */}
      <div className="w-full lg:w-[420px] bg-onyx-900 border-r border-white/5 p-6 lg:p-8 flex flex-col pt-24 lg:h-screen overflow-y-auto shrink-0">
        <div className="space-y-6">
          <div className="space-y-1">
            <h1 className="text-2xl font-display font-bold tracking-tighter">Estúdio de <span className="text-brand-purple">Produção</span></h1>
            <div className="flex items-center justify-between">
              <p className="text-zinc-500 text-xs">Crie seu ensaio em segundos.</p>
              <div className="px-3 py-1 bg-white/5 rounded-full border border-white/10 text-[10px] font-bold text-brand-lavender uppercase tracking-widest">
                {user?.credits_balance || 0} Créditos
              </div>
            </div>
          </div>

          {/* Área de Upload Múltipla */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-[10px] font-black text-zinc-500 uppercase tracking-[0.2em]">1. Captura de Identidade (Mín. 3 fotos)</label>
              <Sparkles className="w-3 h-3 text-brand-purple" />
            </div>
            
            <div className="grid grid-cols-3 gap-2">
              {[0, 1, 2].map((idx) => (
                <label key={idx} className="block group cursor-pointer aspect-square">
                  <input type="file" className="hidden" onChange={(e) => handleFileChange(idx, e)} accept="image/*" />
                  <div className={`w-full h-full rounded-2xl border-2 border-dashed transition-all duration-500 flex flex-col items-center justify-center relative overflow-hidden ${
                    previewUrls[idx] ? 'border-brand-purple' : 'border-white/10 hover:border-white/20 bg-white/[0.02]'
                  }`}>
                    {previewUrls[idx] ? (
                      <img src={previewUrls[idx]!} className="w-full h-full object-cover rounded-xl" />
                    ) : (
                      <Upload className="w-5 h-5 text-zinc-600 group-hover:text-white transition-colors" />
                    )}
                  </div>
                </label>
              ))}
            </div>
            <p className="text-[10px] text-zinc-600 leading-tight">Dica: Use fotos de ângulos diferentes para um resultado ultra-realista.</p>
          </div>

          {/* BOTÃO DE AÇÃO - AGORA MAIS ALTO E VISÍVEL */}
          <div className="space-y-3 pt-2">
            <button
              onClick={handleGenerate}
              disabled={generating || imageFiles.filter(f => f !== null).length < 3 || (user?.credits_balance || 0) < 25}
              className="w-full h-16 rounded-[20px] bg-white text-black font-bold text-base flex items-center justify-center gap-3 hover:bg-brand-lavender hover:text-white transition-all disabled:opacity-50 active:scale-95 shadow-[0_10px_30px_rgba(255,255,255,0.1)] premium-shadow"
            >
              {generating ? (
                <Loader2 className="w-6 h-6 animate-spin" />
              ) : (
                <>
                  <span>Produzir Ensaio</span>
                  <ChevronRight className="w-5 h-5" />
                </>
              )}
            </button>
            <div className="flex items-center justify-center gap-2 text-[10px] font-bold text-zinc-600 uppercase tracking-widest">
              <Zap className="w-3 h-3" />
              Custo de 25 moedas por geração
            </div>
          </div>

          <div className="h-[1px] bg-white/5 w-full" />

          {/* Resumo do Estilo Selecionado */}
          <div className="space-y-3">
            <label className="text-[10px] font-black text-zinc-500 uppercase tracking-[0.2em]">2. Estilo Selecionado</label>
            <div className="p-4 rounded-3xl bg-white/5 border border-white/10 flex items-center gap-4 group">
              <div className="w-14 h-14 rounded-2xl overflow-hidden ring-2 ring-transparent group-hover:ring-brand-purple/50 transition-all">
                <img src={selectedStyle.cover} className="w-full h-full object-cover" />
              </div>
              <div>
                <p className="text-sm font-bold text-white">{selectedStyle.name}</p>
                <p className="text-[10px] text-zinc-500 uppercase tracking-widest font-medium">{selectedStyle.category}</p>
              </div>
              <div className="ml-auto">
                <div className="w-8 h-8 rounded-full bg-brand-purple/10 text-brand-purple flex items-center justify-center">
                  <Check className="w-4 h-4" />
                </div>
              </div>
            </div>
          </div>

          {/* Dicas Pro */}
          <div className="p-5 rounded-3xl bg-brand-purple/5 border border-brand-purple/10">
            <p className="text-[10px] font-black text-brand-lavender uppercase tracking-widest mb-2 flex items-center gap-2">
              <Sparkles className="w-3 h-3" /> Dica de Especialista
            </p>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Para resultados cinematográficos, use fotos de rosto com boa iluminação e sem cabelos cobrindo os olhos.
            </p>
          </div>
        </div>
      </div>

      {/* Coluna Direita: Galeria de Estilos (SCROLL INDEPENDENTE) */}
      <div className="flex-1 lg:h-screen overflow-y-auto p-6 lg:p-12 bg-onyx-950 relative pt-24 lg:pt-32">
        <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-brand-purple/5 blur-[150px] rounded-full pointer-events-none" />
        
        <div className="max-w-5xl mx-auto space-y-10 relative z-10">
          <header className="space-y-3">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-brand-lavender text-[10px] font-bold tracking-[0.2em] uppercase">
              <ImageIcon className="w-3.5 h-3.5" /> Catálogo Editorial 2026
            </div>
            <h2 className="text-4xl md:text-5xl font-display font-bold text-white tracking-tighter">Escolha sua <span className="text-gradient">Ambientação.</span></h2>
          </header>

          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
            {STYLES.map((style) => (
              <motion.div
                key={style.id}
                whileHover={{ y: -8 }}
                onClick={() => setSelectedStyle(style)}
                className={`group cursor-pointer relative rounded-[36px] overflow-hidden border transition-all duration-500 aspect-[4/5] ${
                  selectedStyle?.id === style.id 
                    ? 'border-brand-purple shadow-[0_0_40px_rgba(152,87,203,0.3)]' 
                    : 'border-white/5 hover:border-white/20'
                }`}
              >
                <img 
                  src={style.cover} 
                  alt={style.name} 
                  className="w-full h-full object-cover transition-transform duration-[2s] group-hover:scale-110 opacity-50 group-hover:opacity-100" 
                />
                <div className="absolute inset-0 bg-gradient-to-t from-onyx-950 via-onyx-950/20 to-transparent" />
                
                <div className="absolute bottom-8 left-8 right-8">
                  <span className="text-[9px] font-black uppercase tracking-[0.2em] text-zinc-500 mb-1 block">{style.category}</span>
                  <h3 className="text-xl font-display font-bold text-white">{style.name}</h3>
                </div>

                <div className={`absolute top-6 right-6 w-10 h-10 rounded-full flex items-center justify-center transition-all duration-500 ${
                  selectedStyle?.id === style.id ? 'bg-white text-black scale-100' : 'bg-black/40 text-white scale-0 group-hover:scale-100'
                }`}>
                  <Check className="w-5 h-5" />
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Overlays de Estado */}
      <AnimatePresence>
        {(generating || success) && (
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-[200] bg-onyx-950/98 backdrop-blur-3xl flex flex-col items-center justify-center p-8 text-center"
          >
            <div className="relative w-32 h-32 mb-12">
              <div className="absolute inset-0 rounded-full border-4 border-white/5" />
              <motion.div 
                className="absolute inset-0 rounded-full border-4 border-t-brand-purple"
                animate={{ rotate: 360 }} transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
              />
              <Sparkles className="absolute inset-0 m-auto w-10 h-10 text-brand-purple animate-pulse" />
            </div>
            <h2 className="text-4xl md:text-5xl font-display font-bold tracking-tighter text-white mb-4">
              {success ? 'Produção Iniciada!' : 'Renderizando Estúdio...'}
            </h2>
            <p className="text-zinc-500 font-light text-lg max-w-sm">
              {success 
                ? 'Sua obra premium está na fila de renderização. Redirecionando para sua galeria...' 
                : 'Estamos aplicando iluminação volumétrica e texturas de alta definição à sua imagem.'}
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {error && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 20 }}
            className="fixed bottom-12 left-1/2 -translate-x-1/2 z-[300] bg-rose-600 text-white px-8 py-4 rounded-2xl font-bold shadow-2xl flex items-center gap-4"
          >
            <AlertCircle className="w-5 h-5" />
            <span className="text-sm">{error}</span>
            <button onClick={() => setError(null)} className="ml-4 p-1 hover:bg-white/20 rounded-full transition-colors">
              <X className="w-4 h-4" />
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
