"use client";

import { motion } from "framer-motion";
import { Download, Calendar, Image as ImageIcon, Sparkles, ChevronRight, AlertCircle, Loader2 } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { apiService } from "@/services/api";

export default function HistoryPage() {
  const { token, loading: authLoading } = useAuth();
  const [historyItems, setHistoryItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // ─── Helper: URL da imagem ─────────────────────────────────────────────────
  const getImageUrl = (imagePath: string) => {
    if (!imagePath) return '';
    if (imagePath.startsWith('http')) return imagePath;
    const base = (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000/api').replace(/\/api$/, '');
    return `${base}${imagePath}`;
  };

  const downloadImage = async (imagePath: string) => {
    if (!imagePath) return;
    
    try {
      // Resolve a URL absoluta da imagem
      const imageUrl = getImageUrl(imagePath);
      
      // Constrói a URL para o endpoint de proxy
      // O replace garante que não teremos /api/api/ caso a env já termine em /api
      const base = (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000/api').replace(/\/api$/, '');
      const downloadUrl = `${base}/api/download-image?url=${encodeURIComponent(imageUrl)}`;
      
      console.log('Original Image URL:', imageUrl);
      console.log('Download URL:', downloadUrl);
      
      // Faz uma requisição HEAD para verificar se a rota está acessível e se não retorna 403/404
      const headResponse = await fetch(downloadUrl, { method: 'HEAD' }).catch(() => null);
      if (headResponse && !headResponse.ok) {
        throw new Error(`Servidor retornou erro ${headResponse.status}`);
      }
      
      // Redireciona o navegador para forçar o download
      window.location.href = downloadUrl;
      
    } catch (error) {
      console.error('Erro ao acionar download:', error);
      alert('Não foi possível baixar a imagem. Verifique se ela ainda está disponível.');
    }
  };

  useEffect(() => {
    let interval: NodeJS.Timeout;

    const fetchGallery = async () => {
      if (token) {
        try {
          const response = await apiService.get('/gallery', token);
          if (response.gallery) {
            setHistoryItems(response.gallery);

            const hasPending = response.gallery.some((job: any) =>
              ['queued', 'generating', 'processing'].includes(job.status)
            );

            if (hasPending && !interval) {
              interval = setInterval(fetchGallery, 5000);
            } else if (!hasPending && interval) {
              clearInterval(interval);
            }
          }
        } catch (err) {
          console.error("Erro ao carregar histórico:", err);
        } finally {
          setLoading(false);
        }
      } else if (!authLoading) {
        setLoading(false);
      }
    };

    if (!authLoading) {
      fetchGallery();
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [token, authLoading]);

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-[#F5F5F7] font-sans relative overflow-hidden">

      <div className="max-w-[1400px] mx-auto px-6 md:px-12 py-12 md:py-24 relative z-10">

        {/* ── Cabeçalho ─────────────────────────────────────────────── */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-10 mb-24">
          <div className="space-y-6">
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/8 text-[#748FCC] font-bold text-[10px] tracking-[0.2em] uppercase"
            >
              <ImageIcon className="w-4 h-4" /> Seu Acervo Completo
            </motion.div>
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="text-5xl md:text-7xl font-serif font-medium tracking-tight text-[#F5F5F7]"
            >
              Minha <span className="italic text-[#748FCC]">Galeria</span>
            </motion.h1>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="text-lg text-[#B8BCC4] font-light max-w-2xl leading-relaxed"
            >
              Reveja cada momento eternizado pela nossa Inteligência Artística. 
              Seus retratos salvos em alta definição para sempre.
            </motion.p>
          </div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 }}
            className="flex items-center gap-6 bg-white/5 border border-white/8 p-2.5 rounded-[32px] shadow-sm"
          >
            <div className="px-10 py-4 text-center">
              <span className="block text-4xl font-medium text-[#F5F5F7] leading-none mb-1">
                {historyItems.length}
              </span>
              <span className="text-[10px] font-bold tracking-[0.2em] text-[#B8BCC4] uppercase">Obras</span>
            </div>
            <Link
              href="/generate"
              className="inline-flex items-center justify-center gap-2 bg-[#748FCC] text-[#F5F5F7] rounded-[24px] px-10 py-5 text-sm font-bold hover:bg-[#5F7DB8] transition-all shadow-lg shadow-[#748FCC]/10 hover:shadow-[0_0_40px_rgba(116,143,204,0.35)]"
            >
              Nova Obra <ChevronRight className="w-5 h-5" />
            </Link>
          </motion.div>
        </div>

        {/* ── Estado: Carregando ──────────────────────────────────────── */}
        {loading ? (
          <div className="flex flex-col items-center justify-center py-40 gap-6">
            <Loader2 className="w-12 h-12 text-[#748FCC] animate-spin" />
            <p className="text-[#B8BCC4] font-bold uppercase tracking-[0.3em] text-xs animate-pulse">
              Buscando suas obras-primas...
            </p>
          </div>

        ) : historyItems.length > 0 ? (
          /* ── Grid de imagens — 4 colunas em desktop ───────────────── */
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {historyItems.map((item, idx) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.08 }}
                className="group relative rounded-[32px] overflow-hidden bg-[#121417] border border-[#1F2329] aspect-[3/4] hover:shadow-2xl transition-all duration-700"
              >
                <div className="relative h-full w-full">
                  {/* Imagem concluída */}
                  {item.status === 'completed' && (item.result?.result_url || item.result_url || (item.images && item.images.length > 0)) ? (
                    <img
                      src={getImageUrl(item.result?.result_url || item.result_url || item.images[0])}
                      alt={item.tipo_ensaio || 'Obra de Arte'}
                      className="w-full h-full object-cover transition-transform duration-[1.5s] group-hover:scale-110 opacity-80 group-hover:opacity-100"
                    />
                  ) : item.status === 'failed' ? (
                    /* Falha */
                    <div className="w-full h-full flex flex-col items-center justify-center bg-red-500/5 text-red-500 p-6 text-center">
                      <AlertCircle className="w-10 h-10 mb-4 opacity-40" />
                      <p className="text-xs font-bold uppercase tracking-[0.2em]">Ocorreu um Imprevisto</p>
                      <p className="text-[9px] mt-4 font-bold text-[#748FCC] bg-[#748FCC]/10 px-3 py-1 rounded-full border border-[#748FCC]/20 uppercase tracking-widest">
                        Créditos Reembolsados ✦
                      </p>
                      <Link href="/generate" className="mt-4 text-[10px] font-bold text-[#748FCC] underline uppercase tracking-[0.2em]">
                        Tentar novamente
                      </Link>
                    </div>
                  ) : (
                    /* Em geração */
                    <div className="w-full h-full flex flex-col items-center justify-center bg-[#121417] p-6 text-center gap-4">
                      <Loader2 className="w-10 h-10 text-[#748FCC] animate-spin" />
                      <p className="text-xs font-bold text-[#F5F5F7] uppercase tracking-[0.2em] animate-pulse">
                        Pintando sua Obra...
                      </p>
                      <p className="text-[10px] text-[#B8BCC4] font-light">{item.message || 'Na fila...'}</p>
                    </div>
                  )}

                  {/* Overlay com info e download */}
                  {item.status === 'completed' && (
                    <div className="absolute inset-0 bg-gradient-to-t from-black via-black/20 to-transparent p-8 flex flex-col justify-end opacity-0 group-hover:opacity-100 transition-opacity duration-700">
                      <div className="translate-y-4 group-hover:translate-y-0 transition-transform duration-500">
                        <h3 className="text-xl font-medium text-white mb-2">
                          {item.tipo_ensaio?.replace(/_/g, ' ').toUpperCase() || 'OBRA DE ARTE'}
                        </h3>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2 text-[10px] text-[#B8BCC4] font-bold uppercase tracking-[0.1em]">
                            <Calendar className="w-3.5 h-3.5" />
                            {item.created_at}
                          </div>
                          <button
                            onClick={(e) => {
                              e.preventDefault();
                              e.stopPropagation();
                              downloadImage(item.result?.result_url || item.result_url || item.images?.[0]);
                            }}
                            title="Baixar em alta resolução"
                            className="p-3 bg-[#F5F5F7] text-black rounded-full opacity-90 hover:bg-[#748FCC] hover:text-[#F5F5F7] transition-all shadow-xl hover:scale-110 active:scale-95"
                          >
                            <Download className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </div>

        ) : (
          /* ── Estado vazio ────────────────────────────────────────── */
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center justify-center py-40 text-center space-y-12 bg-[#121417] rounded-[80px] border border-[#1F2329]"
          >
            <div className="w-28 h-28 rounded-[40px] bg-white/5 border border-white/8 flex items-center justify-center">
              <ImageIcon className="w-12 h-12 text-white/10" />
            </div>
            <div className="space-y-4">
              <h2 className="text-4xl md:text-5xl font-serif font-medium text-[#F5F5F7]">
                Seu acervo está em silêncio
              </h2>
              <p className="text-[#B8BCC4] font-light text-xl max-w-lg mx-auto">
                Dê vida às suas memórias e comece a construir sua herança visual hoje mesmo.
              </p>
            </div>
            <Link
              href="/generate"
              className="inline-flex items-center justify-center gap-3 bg-[#748FCC] text-[#F5F5F7] rounded-full px-16 py-6 text-xl font-bold hover:bg-[#5F7DB8] transition-all shadow-2xl shadow-[#748FCC]/20"
            >
              Criar minha primeira obra <Sparkles className="w-6 h-6" />
            </Link>
          </motion.div>
        )}
      </div>
    </div>
  );
}
