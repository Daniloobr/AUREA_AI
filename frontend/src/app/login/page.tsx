'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/services/api';
import { supabase } from '@/lib/supabase';
import Link from 'next/link';
import { ArrowRight, Mail, Lock, Loader2, Sparkles, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();

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
        } catch (err) {
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
    } catch (err) {
      setError('Erro de conexão.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-[#F5F5F7] flex flex-col md:flex-row font-sans">
      
      {/* Image Column */}
      <div className="hidden lg:block w-1/2 relative overflow-hidden">
        <img 
          src="https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=1600&auto=format&fit=crop&grayscale=true" 
          alt="AureaIA Experience" 
          className="w-full h-full object-cover opacity-60 grayscale"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-[#0A0A0A] via-transparent to-transparent" />
        <div className="absolute bottom-20 left-20 space-y-4">
          <h2 className="text-6xl font-medium tracking-tight">Sua luz,<br /><span className="text-[#B8BCC4]">eternizada.</span></h2>
        </div>
      </div>

      {/* Form Column */}
      <div className="flex-1 flex items-center justify-center p-6">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-[400px] space-y-12"
        >
          <div className="space-y-4">
            <div className="w-12 h-12 rounded-[12px] bg-[#748FCC] flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-[#F5F5F7]" />
            </div>
            <h1 className="text-4xl font-serif font-medium tracking-tight text-[#F5F5F7]">Bem-vinda de volta.</h1>
            <p className="text-[#B8BCC4] font-light">Acesse seu estúdio particular e continue eternizando momentos únicos.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <label className="text-[11px] font-bold text-[#B8BCC4] uppercase tracking-widest">E-mail</label>
              <input 
                type="email" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full h-12 px-4 rounded-[12px] bg-[#121417] border border-[#1F2329] focus:border-[#748FCC] focus:outline-none transition-all text-[#F5F5F7] placeholder:text-[#8A9099]/30"
                placeholder="seu@email.com"
                required 
              />
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <label className="text-[11px] font-bold text-[#B8BCC4] uppercase tracking-widest">Senha</label>
                <Link href="/forgot-password" className="text-[11px] font-bold text-[#748FCC] hover:text-[#5F7DB8] transition-colors uppercase tracking-widest">Esqueci</Link>

              </div>
              <input 
                type="password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full h-12 px-4 rounded-[12px] bg-[#121417] border border-[#1F2329] focus:border-[#748FCC] focus:outline-none transition-all text-[#F5F5F7] placeholder:text-[#8A9099]/30"
                placeholder="••••••••"
                required 
              />
            </div>

            {error && (
              <div className="flex items-center gap-3 text-red-500 text-sm font-light bg-red-500/10 p-4 rounded-[12px]">
                <AlertCircle className="w-4 h-4" />
                <span>{error}</span>
              </div>
            )}
            
            <Button 
              type="submit" 
              isLoading={loading}
              className="w-full h-12"
            >
              Entrar
            </Button>
          </form>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-[#1F2329]"></div>
            </div>
            <div className="relative flex justify-center text-[11px] uppercase tracking-widest font-bold">
              <span className="bg-[#0A0A0A] px-4 text-[#8A9099]">Ou continue com</span>
            </div>
          </div>

          <button 
            type="button"
            onClick={handleGoogleLogin}
            disabled={loading}
            className="w-full h-12 flex items-center justify-center gap-3 bg-white text-[#0A0A0A] rounded-[12px] font-medium hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg viewBox="0 0 24 24" className="w-5 h-5">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
            </svg>
            Entrar com Google
          </button>

          <p className="text-center text-sm text-[#B8BCC4]">
            Primeira vez aqui?{' '}<Link href="/register" className="text-[#F5F5F7] hover:text-[#B8BCC4] transition-colors font-medium underline underline-offset-4">Criar sua conta</Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
}
