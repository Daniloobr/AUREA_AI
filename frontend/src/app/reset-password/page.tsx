'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { motion } from 'framer-motion';
import { useSearchParams, useRouter } from 'next/navigation';
import { apiService } from '@/services/api';
import { Lock, Loader2, CheckCircle2 } from 'lucide-react';

function ResetPasswordForm() {
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
    } catch (error) {
      console.error(error);
      setError('Erro de conexão.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-[#0A0A0A] flex flex-col items-center justify-center p-6 text-center">
        <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}>
          <div className="w-20 h-20 bg-emerald-500/20 rounded-full flex items-center justify-center text-emerald-500 mx-auto mb-6">
            <CheckCircle2 className="w-10 h-10" />
          </div>
          <h1 className="text-3xl font-serif font-bold text-[#F5F5F7] mb-2">Senha Alterada!</h1>
          <p className="text-[#B8BCC4]">Você será redirecionada para o login em instantes.</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-[#F5F5F7] flex items-center justify-center p-6 font-sans">
      <motion.div 
        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-[440px] space-y-8"
      >
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-serif font-bold tracking-tighter text-[#F5F5F7]">Nova Senha</h1>
          <p className="text-[#B8BCC4] font-light">Escolha uma senha forte para sua conta.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-[10px] font-bold text-[#B8BCC4] uppercase tracking-widest ml-1">Nova Senha</label>
              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#8A9099] group-focus-within:text-[#748FCC] transition-colors" />
                <input 
                  type="password" 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full h-16 px-6 pl-12 rounded-2xl border border-[#1F2329] bg-[#121417] text-[#F5F5F7] focus:border-[#748FCC]/50 focus:outline-none transition-all"
                  placeholder="••••••••"
                  required 
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-bold text-[#B8BCC4] uppercase tracking-widest ml-1">Confirmar Nova Senha</label>
              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#8A9099] group-focus-within:text-[#748FCC] transition-colors" />
                <input 
                  type="password" 
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full h-16 px-6 pl-12 rounded-2xl border border-[#1F2329] bg-[#121417] text-[#F5F5F7] focus:border-[#748FCC]/50 focus:outline-none transition-all"
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
            className="w-full h-16 bg-[#748FCC] text-[#F5F5F7] rounded-2xl font-bold text-lg hover:bg-[#5F7DB8] transition-all flex justify-center items-center gap-3 disabled:opacity-50 shadow-lg shadow-[#748FCC]/10"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Redefinir Senha'}
          </button>
        </form>
      </motion.div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-[#0A0A0A] flex items-center justify-center">
        <Loader2 className="w-10 h-10 text-[#748FCC] animate-spin" />
      </div>
    }>
      <ResetPasswordForm />
    </Suspense>
  );
}

