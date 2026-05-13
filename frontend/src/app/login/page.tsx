'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/services/api';
import Link from 'next/link';
import { ArrowRight, Mail, Lock, Loader2, Sparkles, Camera } from 'lucide-react';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await apiService.post('/auth/login', { email, password });
      if (response.success) {
        login(response.token, response.user);
      } else {
        setError(response.error || 'Falha no login. Verifique suas credenciais.');
      }
    } catch (err) {
      setError('Erro de conexão com o servidor.');
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="min-h-screen bg-onyx-950 text-white flex selection:bg-brand-purple selection:text-white font-sans">
      {/* Coluna da Esquerda: Imagem/Branding */}
      <div className="hidden lg:flex w-[48%] relative bg-onyx-900 overflow-hidden flex-col justify-end p-20">
        <div className="absolute inset-0 z-0">
          <img 
            src="https://images.unsplash.com/photo-1531983412531-1f49a365ffed?auto=format&fit=crop&q=80&w=1600" 
            alt="Retrato Cinematográfico" 
            className="w-full h-full object-cover opacity-40 scale-105"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-onyx-950 via-onyx-950/40 to-transparent" />
        </div>
        
        <div className="relative z-10 max-w-lg space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }}
            className="w-14 h-14 rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 flex items-center justify-center text-brand-lavender shadow-2xl"
          >
            <Camera className="w-7 h-7" />
          </motion.div>
          <motion.h2 
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.1 }}
            className="text-5xl font-display font-bold tracking-tighter leading-[1.1]"
          >
            A excelência em cada <span className="text-gradient">Pixel.</span>
          </motion.h2>
          <motion.p 
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.2 }}
            className="text-zinc-400 text-xl font-light leading-relaxed"
          >
            Acesse o estúdio para criar retratos hiper-realistas baseados na sua verdadeira essência cinematográfica.
          </motion.p>
        </div>
      </div>

      {/* Coluna da Direita: Formulário */}
      <div className="w-full lg:w-[52%] flex items-center justify-center p-8 relative overflow-hidden bg-onyx-950">
        {/* Glow */}
        <div className="absolute top-[-20%] right-[-20%] w-[600px] h-[600px] rounded-full bg-brand-purple/5 blur-[120px] pointer-events-none" />

        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.8, ease: "easeOut" }}
          className="w-full max-w-[440px]"
        >
          <div className="flex items-center gap-3 mb-16">
            <div className="w-10 h-10 rounded-xl bg-brand-purple flex items-center justify-center text-white shadow-[0_0_20px_rgba(152,87,203,0.4)]">
              <Sparkles className="w-5 h-5" />
            </div>
            <span className="font-display font-bold text-2xl tracking-tighter uppercase">Lumière</span>
          </div>

          <div className="space-y-4 mb-12">
            <h1 className="text-4xl font-display font-bold tracking-tighter text-white">Bem-vinda.</h1>
            <p className="text-zinc-500 text-lg font-light leading-relaxed">Insira suas credenciais exclusivas para acessar o estúdio premium.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-3">
              <label className="text-xs font-bold text-zinc-500 uppercase tracking-widest ml-1">E-mail Profissional</label>
              <div className="relative group">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-600 group-focus-within:text-brand-purple transition-colors" />
                <input 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full h-16 px-6 pl-12 rounded-2xl border border-white/5 bg-white/[0.03] text-white focus:border-brand-purple/50 focus:bg-white/[0.05] focus:outline-none transition-all placeholder:text-zinc-700 text-lg"
                  placeholder="nome@email.com"
                  required 
                />
              </div>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between ml-1">
                <label className="text-xs font-bold text-zinc-500 uppercase tracking-widest">Senha de Acesso</label>
                <Link href="/forgot-password" stroke="currentColor" className="text-xs font-bold text-brand-lavender hover:text-white transition-colors uppercase tracking-widest">Esqueceu?</Link>
              </div>
              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-600 group-focus-within:text-brand-purple transition-colors" />
                <input 
                  type="password" 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full h-16 px-6 pl-12 rounded-2xl border border-white/5 bg-white/[0.03] text-white focus:border-brand-purple/50 focus:bg-white/[0.05] focus:outline-none transition-all placeholder:text-zinc-700 text-lg"
                  placeholder="••••••••"
                  required 
                />
              </div>
            </div>

            {error && (
              <motion.div 
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-2xl text-sm font-semibold flex items-center gap-2"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-red-400" />
                {error}
              </motion.div>
            )}
            
            <button 
              type="submit" 
              disabled={loading}
              className="w-full h-16 mt-6 bg-white text-black rounded-2xl font-bold text-lg hover:bg-zinc-200 transition-all active:scale-[0.98] flex justify-center items-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed premium-shadow"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : (
                <>Entrar no Estúdio <ArrowRight className="w-5 h-5" /></>
              )}
            </button>
          </form>

          <div className="mt-16 pt-8 border-t border-white/5 text-center">
            <p className="text-[14px] text-zinc-600 font-medium">
              Ainda não tem convite? <Link href="/register" className="text-white font-bold hover:text-brand-lavender transition-colors">Solicite acesso VIP.</Link>
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
