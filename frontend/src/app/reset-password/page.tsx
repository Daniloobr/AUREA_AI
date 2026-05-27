'use client';

import React, { useState, useEffect, Suspense, useMemo } from 'react';
import { motion } from 'framer-motion';
import { useSearchParams, useRouter } from 'next/navigation';
import { apiService } from '@/services/api';
import { Lock, Loader2, CheckCircle2 } from 'lucide-react';
import { usePageTitle } from '@/hooks/usePageTitle';

const strengthConfig = [
  { label: 'Fraca', color: 'bg-red-500', bars: 1 },
  { label: 'Média', color: 'bg-yellow-500', bars: 2 },
  { label: 'Forte', color: 'bg-green-500', bars: 3 },
  { label: 'Segura', color: 'bg-emerald-500', bars: 4 },
];

function passwordStrength(pw: string): number {
  let score = 0;
  if (pw.length >= 8) score++;
  if (/[a-z]/.test(pw) && /[A-Z]/.test(pw)) score++;
  if (/\d/.test(pw)) score++;
  if (/[^a-zA-Z0-9]/.test(pw)) score++;
  return score;
}

function ResetPasswordForm() {
  usePageTitle('Redefinir Senha');
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get('token');

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const strength = useMemo(() => passwordStrength(password), [password]);
  const strengthInfo = strengthConfig[Math.min(strength, strengthConfig.length - 1)];

  useEffect(() => {
    if (!token) {
      router.push('/login');
    }
  }, [token, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (password.length < 8) {
      setError('A senha deve ter pelo menos 8 caracteres.');
      return;
    }

    if (strength < 2) {
      setError('Crie uma senha mais forte com letras maiúsculas, números ou caracteres especiais.');
      return;
    }

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
      setError('Não foi possível conectar ao servidor. Verifique sua internet e tente novamente.');
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
                {password.length > 0 && (
                  <div className="mt-2 space-y-1.5">
                    <div className="flex gap-1">
                      {[1, 2, 3, 4].map((i) => (
                        <div key={i} className={`h-1 flex-1 rounded-full transition-colors ${i <= strength ? strengthInfo.color : 'bg-white/10'}`} />
                      ))}
                    </div>
                    <p className={`text-[10px] font-bold uppercase tracking-widest ${strength >= 3 ? 'text-green-500' : strength >= 2 ? 'text-yellow-500' : 'text-red-500'}`}>
                      {strengthInfo.label}
                    </p>
                  </div>
                )}
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

