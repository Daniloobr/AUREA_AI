'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/services/api';
import Link from 'next/link';
import { ArrowRight, Mail, Lock, Loader2, Sparkles, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/Button';

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
          src="https://images.unsplash.com/photo-1594434296621-507bc67a78c1?auto=format&fit=crop&q=80&w=1600" 
          alt="AureaIA Experience" 
          className="w-full h-full object-cover opacity-50"
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

          <p className="text-center text-sm text-[#B8BCC4]">
            Primeira vez aqui?{' '}<Link href="/register" className="text-[#F5F5F7] hover:text-[#B8BCC4] transition-colors font-medium underline underline-offset-4">Criar sua conta</Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
}
