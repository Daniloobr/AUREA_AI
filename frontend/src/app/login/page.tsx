'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/services/api';
import Link from 'next/link';
import { ArrowRight, Mail, Lock, Loader2, Sparkles, AlertCircle, User } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { usePageTitle } from '@/hooks/usePageTitle';

export default function LoginPage() {
  usePageTitle('Entrar');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [logoError, setLogoError] = useState(false);
  const { login } = useAuth();

  React.useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      if (params.get('expired') === 'true') {
        setError('Sessão expirada. Por favor, faça login novamente.');
      }
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await apiService.post('/auth/login', { email, password });
      if (response.success) {
        login(response.token, response.user);
      } else {
        setError(response.error || 'Email ou senha inválidos.');
      }
    } catch (error) {
      console.error(error);
      setError('Erro de conexão com o servidor. Verifique sua internet.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-[#F5F5F7] flex items-center justify-center font-sans relative overflow-hidden">

      {/* Background Image with Overlay */}
      <div className="absolute inset-0 z-0">
        <img
          src="/images/login-bg.png"
          alt="AureaIA Experience"
          className="w-full h-full object-cover opacity-50"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-[#0A0A0A]/80 via-[#0A0A0A]/40 to-[#0A0A0A]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-transparent to-[#0A0A0A]/90" />
      </div>

      <div className="container relative z-10 flex items-center justify-center p-6">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="w-full max-w-[480px] bg-[#0D0D10]/80 backdrop-blur-2xl p-8 md:p-12 rounded-[32px] border border-white/10 shadow-2xl shadow-black/50"
        >
          <div className="space-y-4 mb-10 text-center">
            <motion.div
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring" }}
              className="w-16 h-16 rounded-[20px] flex items-center justify-center mx-auto transition-all"
            >
              {!logoError ? (
                <img
                  src="/images/logo-aurea.png"
                  alt="AureaIA Logo"
                  className="w-full h-full object-contain"
                  onError={() => setLogoError(true)}
                />
              ) : (
                <div className="w-full h-full rounded-[20px] bg-[#748FCC] flex items-center justify-center text-[#F5F5F7] shadow-lg shadow-[#748FCC]/20">
                  <Sparkles className="w-8 h-8" />
                </div>
              )}
            </motion.div>
            <h1 className="text-4xl font-serif font-medium tracking-tight text-[#F5F5F7]">Bem-vinda de volta</h1>
            <p className="text-[#B8BCC4] font-light italic">Acesse seu estúdio e eternize sua história.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2 group">
              <label className="text-[11px] font-bold text-[#B8BCC4] uppercase tracking-widest ml-1 transition-colors group-focus-within:text-[#748FCC]">E-mail</label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-[#B8BCC4]/40" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full h-13 pl-11 pr-4 rounded-[16px] bg-[#121417]/50 border border-[#1F2329] focus:border-[#748FCC] focus:bg-[#121417] focus:outline-none transition-all text-[#F5F5F7] placeholder:text-[#8A9099]/30"
                  placeholder="seu@email.com"
                  required
                />
              </div>
            </div>

            <div className="space-y-2 group">
              <div className="flex justify-between items-center ml-1">
                <label className="text-[11px] font-bold text-[#B8BCC4] uppercase tracking-widest transition-colors group-focus-within:text-[#748FCC]">Senha</label>
                <Link href="/forgot-password" className="text-[10px] font-bold text-[#748FCC]/80 hover:text-[#748FCC] transition-all uppercase tracking-widest hover:underline">Esqueci a senha</Link>
              </div>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-[#B8BCC4]/40" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full h-13 pl-11 pr-4 rounded-[16px] bg-[#121417]/50 border border-[#1F2329] focus:border-[#748FCC] focus:bg-[#121417] focus:outline-none transition-all text-[#F5F5F7] placeholder:text-[#8A9099]/30"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="flex items-center gap-3 text-red-400 text-sm font-light bg-red-400/10 p-4 rounded-[16px] border border-red-400/20"
                >
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{error}</span>
                </motion.div>
              )}
            </AnimatePresence>

            <Button
              type="submit"
              isLoading={loading}
              className="w-full h-14 rounded-[16px] bg-[#748FCC] hover:bg-[#5F7DB8] shadow-xl shadow-[#748FCC]/20 text-[15px] font-bold tracking-wide"
            >
              Entrar no Studio
            </Button>
          </form>

          <div className="mt-10 text-center">
            <p className="text-sm text-[#B8BCC4]">
              Ainda não tem conta?{' '}<Link href="/register" className="text-[#F5F5F7] hover:text-[#748FCC] transition-all font-medium border-b border-[#F5F5F7]/30 hover:border-[#748FCC]">Criar meu acesso</Link>
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
