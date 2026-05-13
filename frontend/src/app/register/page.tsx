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
            Comece sua jornada hoje e ganhe 25 créditos para criar seu primeiro retrato cinematográfico.
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

            {/* Checkbox LGPD */}
            <div className="flex items-start gap-3 ml-1">
              <input 
                type="checkbox" 
                id="lgpd" 
                required 
                className="mt-1 w-4 h-4 rounded border-white/10 bg-white/5 text-brand-purple focus:ring-brand-purple"
              />
              <label htmlFor="lgpd" className="text-xs text-zinc-500 leading-relaxed">
                Eu li e aceito os <Link href="/terms" className="text-brand-lavender hover:underline">Termos de Uso</Link> e a <Link href="/privacy" className="text-brand-lavender hover:underline">Política de Privacidade</Link> (LGPD).
              </label>
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
            
            <div className="relative flex items-center py-4">
              <div className="flex-grow border-t border-white/10"></div>
              <span className="flex-shrink-0 mx-4 text-zinc-500 text-xs font-medium uppercase tracking-widest">Ou</span>
              <div className="flex-grow border-t border-white/10"></div>
            </div>

            <button 
              type="button"
              className="w-full h-14 bg-white/[0.03] border border-white/10 hover:bg-white/[0.08] text-white rounded-2xl font-semibold text-sm transition-all flex justify-center items-center gap-3"
            >
              <svg viewBox="0 0 24 24" className="w-5 h-5" xmlns="http://www.w3.org/2000/svg">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                <path d="M1 1h22v22H1z" fill="none"/>
              </svg>
              Continuar com Google
            </button>
          </form>

          <div className="mt-8 pt-8 border-t border-white/5 text-center space-y-4">
            <p className="text-[14px] text-zinc-600 font-medium">
              Já faz parte do estúdio? <Link href="/login" className="text-white font-bold hover:text-brand-lavender transition-colors">Fazer Login.</Link>
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

