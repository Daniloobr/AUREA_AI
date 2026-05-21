'use client';

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Download, Calendar, Loader2, Image as ImageIcon, Sparkles, AlertCircle, ChevronRight } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/services/api';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import Image from 'next/image';

export default function GalleryPage() {
  const { token, loading: authLoading } = useAuth();
  const router = useRouter();
  const [historyItems, setHistoryItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // ─── Proteger rota ────────────────────────────────────────────────────────
  useEffect(() => {
    if (!authLoading && !token) {
      router.push('/login');
    }
  }, [token, authLoading, router]);

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;

    const fetchGallery = async () => {
      if (token) {
        try {
          const response = await apiService.get('/gallery', token);
          if (response.gallery) {
            const newItems = response.gallery;
            // Update state only if data changed
            setHistoryItems(prev => {
              const prevStr = JSON.stringify(prev);
              const newStr = JSON.stringify(newItems);
              return prevStr === newStr ? prev : newItems;
            });

            const hasPending = response.gallery.some((job: any) => 
              ['queued', 'generating', 'processing'].includes(job.status)
            );
            
            // Start polling only when there are pending jobs
            if (hasPending && !interval) {
              interval = setInterval(fetchGallery, 10000); // 10 seconds
            } else if (!hasPending && interval) {
              clearInterval(interval);
              interval = null;
            }
          }
        } catch (err) {
          console.error("Erro ao carregar galeria:", err);
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

  // ─── Helper: URL da imagem ────────────────────────────────────────────────
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
      
      // USA CAMINHO RELATIVO para que o rewrite do Vercel (vercel.json)
      // encaminhe automaticamente para o backend Render em produção.
      // Isso funciona tanto em dev (next.config.ts rewrites) quanto em prod (vercel.json rewrites).
      const downloadUrl = `/api/download-image?url=${encodeURIComponent(imageUrl)}`;
      
      console.log('[Download] Image URL original:', imageUrl);
      console.log('[Download] Proxy URL:', downloadUrl);
      
      const response = await fetch(downloadUrl);
      
      console.log('[Download] Response status:', response.status);
      console.log('[Download] Response Content-Type:', response.headers.get('Content-Type'));
      
      if (!response.ok) {
        const errorText = await response.text().catch(() => 'Erro desconhecido');
        console.error('[Download] Erro do servidor:', errorText);
        throw new Error(`Servidor retornou erro ${response.status}`);
      }
      
      const blob = await response.blob();
      console.log('[Download] Blob size:', blob.size, 'type:', blob.type);
      
      const blobUrl = window.URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = 'ensaio_aureaia.jpg';
      link.style.display = 'none';
      
      document.body.appendChild(link);
      link.click();
      
      // Limpeza
      setTimeout(() => {
        document.body.removeChild(link);
        window.URL.revokeObjectURL(blobUrl);
      }, 1000);
      
    } catch (error) {
      console.error('[Download] Falha completa:', error);
      alert('Não foi possível baixar a imagem. Verifique se ela ainda está disponível.');
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-[#F5F5F7] font-sans relative overflow-hidden">
      
      <div className="max-w-[1400px] mx-auto px-6 md:px-12 py-12 md:py-24 relative z-10">
        
        {/* ── Cabeçalho da Galeria ── layout preservado ─────────────────── */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-10 mb-24">
          <div className="space-y-6">
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/8 text-[#748FCC] font-bold text-[10px] tracking-[0.2em] uppercase"
            >
              <ImageIcon className="w-4 h-4" /> Seu Acervo Particular
            </motion.div>
            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="text-5xl md:text-7xl font-serif font-medium tracking-tight text-[#F5F5F7]"
            >
              Suas <span className="italic text-[#748FCC]">Memórias</span> Eternizadas
            </motion.h1>
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="text-lg text-[#B8BCC4] font-light max-w-2xl leading-relaxed"
            >
              Reveja cada capítulo de sua jornada transformado em poesia visual. 
              Suas obras-primas, salvas em altíssima definição para sempre.
            </motion.p>
          </div>
          
          {/* Contador + botão de novo ensaio — layout preservado */}
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 }}
            className="flex items-center gap-6 bg-white/5 border border-white/8 p-2.5 rounded-[32px] shadow-sm"
          >
            <div className="px-10 py-4 text-center">
              <span className="block text-4xl font-medium text-[#F5F5F7] leading-none mb-1">{historyItems.length}</span>
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
          /* ── Grid de obras — layout e cards preservados integralmente ── */
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-8 md:gap-12">
            {historyItems.map((item, idx) => (
              <motion.div 
                key={item.id}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="group relative rounded-[40px] overflow-hidden bg-[#121417] border border-[#1F2329] aspect-[3/4] shadow-sm hover:shadow-2xl hover:border-[#748FCC]/30 transition-all duration-700"
              >
                <div className="relative h-full w-full">
                  {/* Imagem concluída */}
                  {item.status === 'completed' && (item.result?.result_url || item.result_url || (item.images && item.images.length > 0)) ? (
                    <Image 
                      src={getImageUrl(item.result?.result_url || item.result_url || item.images[0])} 
                      alt={item.tipo_ensaio || 'Obra de Arte'} 
                      fill
                      sizes="(max-width: 768px) 50vw, 33vw"
                      loading="lazy"
                      className="object-cover transition-transform duration-[3s] group-hover:scale-110" 
                    />
                  ) : item.status === 'failed' ? (
                    /* Falha na geração */
                    <div className="w-full h-full flex flex-col items-center justify-center bg-red-500/5 text-red-500 p-10 text-center">
                      <AlertCircle className="w-12 h-12 mb-6 opacity-30" />
                      <p className="text-xs font-bold uppercase tracking-[0.2em]">Ocorreu um Imprevisto</p>
                      <Link href="/generate" className="mt-8 text-[10px] font-bold text-[#748FCC] underline uppercase tracking-[0.2em]">
                        Tentar novamente
                      </Link>
                    </div>
                  ) : (
                    /* Em geração */
                    <div className="w-full h-full flex flex-col items-center justify-center bg-[#121417] p-10 text-center gap-6">
                      <Loader2 className="w-12 h-12 text-[#748FCC] animate-spin" />
                      <p className="text-xs font-bold text-[#F5F5F7] uppercase tracking-[0.2em] animate-pulse">
                        Pintando sua Obra...
                      </p>
                    </div>
                  )}
                  
                  {/* Overlay com info + download — aparece no hover */}
                  {item.status === 'completed' && (
                    <div className="absolute inset-0 bg-gradient-to-t from-black via-black/20 to-transparent p-10 flex flex-col justify-end opacity-0 group-hover:opacity-100 transition-opacity duration-700">
                      <div className="translate-y-6 group-hover:translate-y-0 transition-transform duration-700">
                        <h3 className="text-2xl font-medium text-white mb-3">
                          {item.tipo_ensaio?.replace(/_/g, ' ').toUpperCase() || 'OBRA DE ARTE'}
                        </h3>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3 text-[#F5F5F7]/60 text-[10px] font-bold uppercase tracking-[0.2em]">
                            <Calendar className="w-3.5 h-3.5 text-[#B8BCC4]" />
                            {item.created_at}
                          </div>
                          {/* Botão de download */}
                          <button 
                            onClick={() => downloadImage(item.result?.result_url || item.result_url || item.images?.[0])}
                            title="Baixar em alta resolução"
                            className="flex items-center gap-2 bg-[#F5F5F7] text-black rounded-full px-4 py-2.5 text-[10px] font-bold uppercase tracking-[0.1em] shadow-2xl hover:bg-[#748FCC] hover:text-[#F5F5F7] transition-all transform hover:scale-105 active:scale-95"
                          >
                            <Download className="w-4 h-4" />
                            Alta Resolução
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
          /* ── Estado vazio ────────────────────────────────────────────── */
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center justify-center py-40 text-center space-y-12 bg-[#121417] rounded-[80px] border border-[#1F2329] shadow-sm"
          >
            <div className="w-28 h-28 rounded-[40px] bg-white/5 border border-white/8 flex items-center justify-center shadow-sm">
              <ImageIcon className="w-12 h-12 text-white/10" />
            </div>
            <div className="space-y-4">
              <h2 className="text-4xl md:text-5xl font-serif font-medium text-[#F5F5F7]">Seu acervo está em silêncio</h2>
              <p className="text-[#B8BCC4] font-light text-xl max-w-lg mx-auto">
                Dê o primeiro passo e comece a construir sua herança visual hoje mesmo.
              </p>
            </div>
            <Link
              href="/generate"
              className="inline-flex items-center justify-center gap-3 bg-[#748FCC] text-[#F5F5F7] rounded-full px-16 py-6 text-xl font-bold hover:bg-[#5F7DB8] transition-all shadow-2xl shadow-[#748FCC]/20 hover:shadow-[0_0_40px_rgba(116,143,204,0.35)]"
            >
              Criar minha primeira obra <Sparkles className="w-6 h-6" />
            </Link>
          </motion.div>
        )}
      </div>
    </div>
  );
}
