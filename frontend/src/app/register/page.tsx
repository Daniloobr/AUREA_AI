'use client';

import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/services/api';
import Link from 'next/link';
import { ArrowRight, Mail, Lock, User, Loader2, Sparkles, AlertCircle, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
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

export default function RegisterPage() {
  usePageTitle('Criar Conta');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const [logoError, setLogoError] = useState(false);
  const strength = useMemo(() => passwordStrength(password), [password]);
  const strengthInfo = strengthConfig[Math.min(strength, strengthConfig.length - 1)];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!acceptedTerms) {
      setError('Você precisa aceitar os termos de uso e LGPD.');
      return;
    }

    if (password.length < 8) {
      setError('A senha deve ter pelo menos 8 caracteres.');
      return;
    }

    if (strength < 2) {
      setError('Crie uma senha mais forte com letras maiúsculas, números ou caracteres especiais.');
      return;
    }

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
        setError(response.error || 'Erro no cadastro.');
      }
    } catch (err: unknown) {
      console.error(err);
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
          src="/images/register-bg.png" 
          alt="AureaIA Registration Background" 
          className="w-full h-full object-cover opacity-40 lg:opacity-50"
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
                  src="/images/LOGO aurea.png" 
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
            <h1 className="text-4xl font-serif font-medium tracking-tight text-[#F5F5F7]">Criar Acesso</h1>
            <p className="text-[#B8BCC4] font-light italic">Eternize a luz da sua nova história.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
             <div className="space-y-2 group">
              <label className="text-[11px] font-bold text-[#B8BCC4] uppercase tracking-widest ml-1 transition-colors group-focus-within:text-[#748FCC]">Nome Completo</label>
              <div className="relative">
                <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-[#B8BCC4]/40" />
                <input 
                  type="text" 
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full h-13 pl-11 pr-4 rounded-[16px] bg-[#121417]/50 border border-[#1F2329] focus:border-[#748FCC] focus:bg-[#121417] focus:outline-none transition-all text-[#F5F5F7] placeholder:text-[#8A9099]/30"
                  placeholder="Como gostaria de ser chamada"
                  required 
                />
              </div>
            </div>

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
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2 group">
                <label className="text-[11px] font-bold text-[#B8BCC4] uppercase tracking-widest ml-1 transition-colors group-focus-within:text-[#748FCC]">Senha</label>
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
              <div className="space-y-2 group">
                <label className="text-[11px] font-bold text-[#B8BCC4] uppercase tracking-widest ml-1 transition-colors group-focus-within:text-[#748FCC]">Confirmar</label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-[#B8BCC4]/40" />
                  <input 
                    type="password" 
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full h-13 pl-11 pr-4 rounded-[16px] bg-[#121417]/50 border border-[#1F2329] focus:border-[#748FCC] focus:bg-[#121417] focus:outline-none transition-all text-[#F5F5F7] placeholder:text-[#8A9099]/30"
                    placeholder="••••••••"
                    required 
                  />
                </div>
              </div>
            </div>

            {/* Terms & LGPD */}
            <div className="flex items-start gap-3 py-2">
              <div className="relative flex items-center h-5">
                <input
                  id="terms"
                  type="checkbox"
                  checked={acceptedTerms}
                  onChange={(e) => setAcceptedTerms(e.target.checked)}
                  className="w-5 h-5 rounded-[6px] border-[#1F2329] bg-[#121417] text-[#748FCC] focus:ring-[#748FCC]/20 focus:ring-offset-0 cursor-pointer transition-all"
                />
              </div>
              <label htmlFor="terms" className="text-[13px] text-[#B8BCC4] leading-tight cursor-pointer hover:text-[#F5F5F7] transition-colors">
                Aceito os <Link href="/terms" className="text-[#748FCC] hover:underline">Termos de Uso</Link> e autorizo o tratamento de dados (LGPD).
              </label>
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
              Criar Conta e Iniciar
            </Button>
          </form>

          <div className="mt-8 text-center">
            <p className="text-sm text-[#B8BCC4]">
              Já possui uma conta? <Link href="/login" className="text-[#F5F5F7] hover:text-[#748FCC] transition-all font-medium border-b border-[#F5F5F7]/30 hover:border-[#748FCC]">Entrar no Studio</Link>
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

