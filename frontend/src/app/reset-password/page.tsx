'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useSearchParams, useRouter } from 'next/navigation';
import { apiService } from '@/services/api';
import { Lock, Loader2, CheckCircle2 } from 'lucide-react';

export default function ResetPasswordPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get('token');

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) {
      router.push('/login');
    }
  }, [token, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError('As senhas não coincidem.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await apiService.post('/auth/reset-password', { token, password });
      if (response.success) {
        setSuccess(true);
        setTimeout(() => router.push('/login'), 3000);
      } else {
        setError(response.error || 'Falha ao redefinir senha.');
      }
    } catch (err) {
      setError('Erro de conexão.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-onyx-950 flex flex-col items-center justify-center p-6 text-center">
        <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}>
          <div className="w-20 h-20 bg-emerald-500/20 rounded-full flex items-center justify-center text-emerald-500 mx-auto mb-6">
            <CheckCircle2 className="w-10 h-10" />
          </div>
          <h1 className="text-3xl font-display font-bold text-white mb-2">Senha Alterada!</h1>
          <p className="text-zinc-500">Você será redirecionada para o login em instantes.</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-onyx-950 text-white flex items-center justify-center p-6 font-sans">
      <motion.div 
        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-[440px] space-y-8"
      >
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-display font-bold tracking-tighter">Nova Senha</h1>
          <p className="text-zinc-500 font-light">Escolha uma senha forte para sua conta.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest ml-1">Nova Senha</label>
              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-600 group-focus-within:text-brand-purple transition-colors" />
                <input 
                  type="password" 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full h-16 px-6 pl-12 rounded-2xl border border-white/5 bg-white/[0.03] text-white focus:border-brand-purple/50 focus:outline-none transition-all"
                  placeholder="••••••••"
                  required 
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest ml-1">Confirmar Nova Senha</label>
              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-600 group-focus-within:text-brand-purple transition-colors" />
                <input 
                  type="password" 
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full h-16 px-6 pl-12 rounded-2xl border border-white/5 bg-white/[0.03] text-white focus:border-brand-purple/50 focus:outline-none transition-all"
                  placeholder="••••••••"
                  required 
                />
              </div>
            </div>
          </div>

          {error && <p className="text-red-400 text-sm text-center font-medium">{error}</p>}

          <button 
            type="submit" 
            disabled={loading}
            className="w-full h-16 bg-white text-black rounded-2xl font-bold text-lg hover:bg-zinc-200 transition-all flex justify-center items-center gap-3 disabled:opacity-50"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Redefinir Senha'}
          </button>
        </form>
      </motion.div>
    </div>
  );
}
