"use client";

import { motion } from "framer-motion";
import { Download, Clock, Image as ImageIcon, Sparkles, ChevronRight, AlertCircle } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { apiService } from "@/services/api";

export default function HistoryPage() {
  const router = useRouter();
  const { token, loading: authLoading } = useAuth();
  const [historyItems, setHistoryItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    const fetchGallery = async () => {
      if (token) {
        try {
          const response = await apiService.get('/gallery', token);
          if (response.gallery) {
            setHistoryItems(response.gallery);
            
            // If there are pending jobs, poll every 5 seconds
            const hasPending = response.gallery.some((job: any) => 
              job.status === 'queued' || job.status === 'generating' || job.status === 'processing'
            );
            
            if (hasPending && !interval) {
              interval = setInterval(fetchGallery, 5000);
            } else if (!hasPending && interval) {
              clearInterval(interval);
            }
          }
        } catch (err) {
          console.error("Erro ao carregar galeria:", err);
        } finally {
          setLoading(false);
        }
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
    <div className="min-h-screen bg-onyx-950 text-zinc-100 font-sans selection:bg-brand-purple selection:text-white relative overflow-hidden">
      
      {/* Background Gradients */}
      <div className="absolute top-0 left-0 w-[500px] h-[500px] bg-brand-purple/5 blur-[150px] rounded-full pointer-events-none" />

      <div className="max-w-[1400px] mx-auto px-6 md:px-12 py-12 md:py-24 relative z-10">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-10 mb-20">
          <div className="space-y-4">
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-brand-lavender text-[12px] font-bold tracking-[0.2em] uppercase backdrop-blur-md"
            >
              <ImageIcon className="w-4 h-4" /> Sua Coleção Pessoal
            </motion.div>
            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="text-5xl md:text-7xl font-display font-bold text-white tracking-tighter"
            >
              Minha <span className="text-gradient">Galeria</span>
            </motion.h1>
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="text-lg text-zinc-500 font-light max-w-2xl leading-relaxed"
            >
              Reveja cada momento eternizado pela nossa Inteligência Artificial. Seus retratos cinematográficos salvos em alta definição.
            </motion.p>
          </div>
          
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 }}
            className="flex items-center gap-4 bg-white/5 border border-white/10 p-2 rounded-3xl backdrop-blur-xl"
          >
            <div className="px-8 py-3 text-center">
              <span className="block text-3xl font-display font-bold text-white leading-none mb-1">{historyItems.length}</span>
              <span className="text-[10px] font-bold tracking-widest text-zinc-500 uppercase">Obras Criadas</span>
            </div>
            <Link href="/dashboard" className="h-full px-8 py-4 bg-white text-black rounded-2xl font-bold text-sm flex items-center gap-2 hover:bg-zinc-200 transition-colors">
              Novo Ensaio <ChevronRight className="w-5 h-5" />
            </Link>
          </motion.div>
        </div>

        {historyItems.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {historyItems.map((item, idx) => (
              <motion.div 
                key={item.id}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 + idx * 0.1 }}
                whileHover={{ y: -10 }}
                className="group relative rounded-[32px] overflow-hidden bg-onyx-900 border border-white/5 aspect-[3/4]"
              >
                <div className="relative aspect-[3/4]">
                  {item.status === 'completed' && item.images && item.images.length > 0 ? (
                    <img 
                      src={item.images[0].startsWith('http') ? item.images[0] : `${(process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000/api').replace(/\/api$/, '')}${item.images[0]}`} 
                      alt={item.tipo_ensaio} 
                      className="w-full h-full object-cover transition-transform duration-[1.5s] group-hover:scale-110 opacity-80 group-hover:opacity-100" 
                    />
                  ) : item.status === 'failed' ? (
                    <div className="w-full h-full flex flex-col items-center justify-center bg-rose-950/20 text-rose-500 p-6 text-center">
                      <AlertCircle className="w-10 h-10 mb-4" />
                      <p className="text-xs font-bold uppercase tracking-widest">Falha na Geração</p>
                      <p className="text-[10px] opacity-60 mt-2">{item.error || 'Erro desconhecido'}</p>
                    </div>
                  ) : (
                    <div className="w-full h-full flex flex-col items-center justify-center bg-brand-purple/5 p-6 text-center">
                      <div className="relative w-12 h-12 mb-4">
                        <div className="absolute inset-0 rounded-full border-2 border-white/5" />
                        <motion.div 
                          className="absolute inset-0 rounded-full border-2 border-t-brand-purple"
                          animate={{ rotate: 360 }} transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                        />
                        <Clock className="absolute inset-0 m-auto w-5 h-5 text-brand-purple" />
                      </div>
                      <p className="text-xs font-bold text-white uppercase tracking-widest animate-pulse">Processando...</p>
                      <div className="mt-4 w-full bg-white/5 h-1 rounded-full overflow-hidden">
                        <motion.div 
                          className="h-full bg-brand-purple"
                          initial={{ width: "0%" }}
                          animate={{ width: `${item.progress || 10}%` }}
                        />
                      </div>
                      <p className="text-[10px] text-zinc-500 mt-2 uppercase tracking-tighter">{item.message || 'Na fila...'}</p>
                    </div>
                  )}
                  
                  <div className="absolute inset-0 bg-gradient-to-t from-black via-black/20 to-transparent p-8 flex flex-col justify-end">
                    <div className="translate-y-4 group-hover:translate-y-0 transition-transform duration-500">
                      <h3 className="text-xl font-bold text-white mb-2">
                        {item.tipo_ensaio?.replace(/_/g, ' ').toUpperCase() || 'Ensaio'}
                      </h3>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 text-xs text-zinc-400 font-medium">
                          <Clock className="w-3.5 h-3.5" />
                          {item.created_at}
                        </div>
                        {item.status === 'completed' && (
                          <a 
                            href={item.images?.[0]?.startsWith('http') ? item.images?.[0] : `${(process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000/api').replace(/\/api$/, '')}${item.images?.[0]}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-3 bg-white/10 backdrop-blur-md text-white rounded-full opacity-0 group-hover:opacity-100 transition-all hover:bg-white hover:text-black shadow-xl"
                          >
                            <Download className="w-4 h-4" />
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        ) : (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center justify-center py-32 text-center space-y-8 glass rounded-[48px]"
          >
            <div className="w-24 h-24 rounded-full bg-white/5 border border-white/10 flex items-center justify-center shadow-inner">
              <ImageIcon className="w-10 h-10 text-zinc-700" />
            </div>
            <div className="space-y-4">
              <h2 className="text-3xl font-display font-bold text-white">Sua galeria está vazia</h2>
              <p className="text-zinc-500 font-light text-lg max-w-md mx-auto">
                Dê vida às suas memórias e comece sua jornada cinematográfica hoje mesmo.
              </p>
            </div>
            <Link href="/dashboard" className="h-14 px-10 bg-brand-purple text-white rounded-full font-bold text-lg hover:scale-105 transition-all flex items-center justify-center gap-3 shadow-[0_0_40px_rgba(152,87,203,0.3)]">
              Começar a Criar <Sparkles className="w-5 h-5" />
            </Link>
          </motion.div>
        )}
      </div>
    </div>
  );
}
