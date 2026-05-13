'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/services/api';
import Link from 'next/link';
import { ArrowRight, Mail, Lock, User, Loader2, Sparkles, CheckCircle2 } from 'lucide-react';

export default function RegisterPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (password !== confirmPassword) {
      setError('As senhas não coincidem.');
      setLoading(false);
      return;
    }

    try {
      const response = await apiService.post('/auth/register', { name, email, password });
      if (response.success) {
        login(response.token, response.user);
      } else {
        setError(response.error || 'Falha ao criar conta.');
      }
    } catch (err) {
      setError('Erro de conexão com o servidor.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-onyx-950 text-white flex selection:bg-brand-purple selection:text-white font-sans overflow-x-hidden">
      {/* Coluna da Esquerda: Branding (Oculta em mobile) */}
      <div className="hidden lg:flex w-[48%] relative bg-onyx-900 overflow-hidden flex-col justify-end p-20 border-r border-white/5">
        <div className="absolute inset-0 z-0">
          <img 
            src="https://images.unsplash.com/photo-1551248429-40975aa4de74?auto=format&fit=crop&q=80&w=1600" 
            alt="Maternidade Realista" 
            className="w-full h-full object-cover opacity-30 scale-110"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-onyx-950 via-onyx-950/40 to-transparent" />
        </div>
        
        <div className="relative z-10 max-w-lg space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }}
            className="w-14 h-14 rounded-2xl bg-brand-purple/20 backdrop-blur-xl border border-brand-purple/30 flex items-center justify-center text-brand-lavender shadow-2xl"
          >
            <Sparkles className="w-7 h-7" />
          </motion.div>
          <motion.h2 
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.1 }}
            className="text-5xl font-display font-bold tracking-tighter leading-[1.1]"
          >
            A nova era da <span className="text-gradient">Maternidade.</span>
          </motion.h2>
          <motion.p 
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.2 }}
            className="text-zinc-400 text-xl font-light leading-relaxed"
          >
            Comece sua jornada hoje e ganhe 100 créditos para criar seus primeiros retratos cinematográficos.
          </motion.p>
        </div>
      </div>

      {/* Coluna da Direita: Formulário */}
      <div className="w-full lg:w-[52%] flex items-center justify-center p-8 relative overflow-hidden bg-onyx-950">
        <div className="absolute bottom-[-10%] left-[-10%] w-[600px] h-[600px] rounded-full bg-brand-purple/5 blur-[120px] pointer-events-none" />

        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.8, ease: "easeOut" }}
          className="w-full max-w-[480px]"
        >
          <div className="flex items-center gap-3 mb-12">
            <div className="w-10 h-10 rounded-xl bg-brand-purple flex items-center justify-center text-white shadow-[0_0_20px_rgba(152,87,203,0.4)]">
              <Sparkles className="w-5 h-5" />
            </div>
            <span className="font-display font-bold text-2xl tracking-tighter uppercase">Lumière</span>
          </div>

          <div className="space-y-3 mb-10">
            <h1 className="text-4xl font-display font-bold tracking-tighter text-white">Criar Conta.</h1>
            <p className="text-zinc-500 text-lg font-light">Seja bem-vinda ao círculo exclusivo de arte por IA.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest ml-1">Nome de Artista</label>
              <div className="relative group">
                <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-600 group-focus-within:text-brand-purple transition-colors" />
                <input 
                  type="text" 
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full h-14 px-6 pl-12 rounded-2xl border border-white/5 bg-white/[0.03] text-white focus:border-brand-purple/50 focus:bg-white/[0.05] focus:outline-none transition-all placeholder:text-zinc-700"
                  placeholder="Seu nome completo"
                  required 
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest ml-1">E-mail Profissional</label>
              <div className="relative group">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-600 group-focus-within:text-brand-purple transition-colors" />
                <input 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full h-14 px-6 pl-12 rounded-2xl border border-white/5 bg-white/[0.03] text-white focus:border-brand-purple/50 focus:bg-white/[0.05] focus:outline-none transition-all placeholder:text-zinc-700"
                  placeholder="nome@email.com"
                  required 
                />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest ml-1">Senha</label>
                <div className="relative group">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-600 group-focus-within:text-brand-purple transition-colors" />
                  <input 
                    type="password" 
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full h-14 px-6 pl-11 rounded-2xl border border-white/5 bg-white/[0.03] text-white focus:border-brand-purple/50 focus:bg-white/[0.05] focus:outline-none transition-all placeholder:text-zinc-700 text-sm"
                    placeholder="••••••••"
                    required 
                  />
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest ml-1">Confirmar</label>
                <div className="relative group">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-600 group-focus-within:text-brand-purple transition-colors" />
                  <input 
                    type="password" 
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full h-14 px-6 pl-11 rounded-2xl border border-white/5 bg-white/[0.03] text-white focus:border-brand-purple/50 focus:bg-white/[0.05] focus:outline-none transition-all placeholder:text-zinc-700 text-sm"
                    placeholder="••••••••"
                    required 
                  />
                </div>
              </div>
            </div>

            {error && (
              <motion.div 
                initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}
                className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-2xl text-[13px] font-semibold flex items-center gap-2"
              >
                <CheckCircle2 className="w-4 h-4 text-red-400" />
                {error}
              </motion.div>
            )}
            
            <button 
              type="submit" 
              disabled={loading}
              className="w-full h-16 mt-4 bg-white text-black rounded-2xl font-bold text-lg hover:bg-zinc-200 transition-all active:scale-[0.98] flex justify-center items-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed premium-shadow"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : (
                <>Criar Conta VIP <ArrowRight className="w-5 h-5" /></>
              )}
            </button>
          </form>

          <div className="mt-10 pt-8 border-t border-white/5 text-center">
            <p className="text-[14px] text-zinc-600 font-medium">
              Já faz parte do estúdio? <Link href="/login" className="text-white font-bold hover:text-brand-lavender transition-colors">Fazer Login.</Link>
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

