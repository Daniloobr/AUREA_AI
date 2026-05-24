'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/services/api';
import { supabase } from '@/lib/supabase';
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

  React.useEffect(() => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (event === 'SIGNED_IN' && session) {
        setLoading(true);
        try {
          const response = await apiService.post('/auth/google-login', {
            access_token: session.access_token
          });
          if (response.success) {
            login(response.token, response.user);
          } else {
            setError(response.error || 'Erro ao autenticar com Google.');
            supabase.auth.signOut();
          }
        } catch (error) {
          console.error(error);
          setError('Erro de conexão ao processar Google Login.');
          supabase.auth.signOut();
        } finally {
          setLoading(false);
        }
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, [login]);

  const handleGoogleLogin = async () => {
    setError('');
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/dashboard`
      }
    });

    if (error) {
      setError('Não foi possível iniciar o login com Google.');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await apiService.post('/auth/login', { email, password });
      if (response.success) {
        login(response.token, response.user);
      } else {
        setError(response.error || 'Dados inválidos.');
      }
    } catch (error) {
      console.error(error);
      setError('Erro de conexão.');
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

          <div className="relative my-8">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-white/5"></div>
            </div>
            <div className="relative flex justify-center text-[10px] uppercase tracking-[0.2em] font-bold">
              <span className="bg-[#0D0D10]/0 px-4 text-[#B8BCC4]/60">ou acesse com</span>
            </div>
          </div>

          <button
            type="button"
            onClick={handleGoogleLogin}
            disabled={loading}
            className="w-full h-13 flex items-center justify-center gap-3 bg-white text-[#0A0A0A] rounded-[16px] font-bold text-[14px] hover:bg-gray-100 transition-all active:scale-[0.98] disabled:opacity-50"
          >
            <svg viewBox="0 0 24 24" className="w-5 h-5">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
            </svg>
            Entrar com Google
          </button>

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
