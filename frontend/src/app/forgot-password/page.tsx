'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { apiService } from '@/services/api';
import Link from 'next/link';
import { ArrowLeft, Mail, Loader2, Sparkles } from 'lucide-react';
import { usePageTitle } from '@/hooks/usePageTitle';

export default function ForgotPasswordPage() {
  usePageTitle('Recuperar Senha');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    try {
      const response = await apiService.post('/auth/forgot-password', { email });
      if (response.success) {
        setMessage(response.message);
      } else {
        setError(response.error || 'Falha ao enviar e-mail.');
      }
    } catch (error) {
      console.error(error);
      setError('Não foi possível conectar ao servidor. Verifique sua internet e tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-[#F5F5F7] flex items-center justify-center p-6 font-sans">
      <div className="absolute top-[-20%] right-[-20%] w-[600px] h-[600px] rounded-full bg-[#748FCC]/5 blur-[120px] pointer-events-none" />

      <motion.div 
        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-[440px] space-y-8"
      >
        <div className="text-center space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-[#748FCC]/10 flex items-center justify-center text-[#748FCC] mx-auto shadow-sm">
            <Sparkles className="w-6 h-6" />
          </div>
          <h1 className="text-3xl font-serif font-bold tracking-tighter text-[#F5F5F7]">Recuperar Senha</h1>
          <p className="text-[#B8BCC4] font-light">Enviaremos um link de acesso para o seu e-mail.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="text-[10px] font-bold text-[#B8BCC4] uppercase tracking-widest ml-1">Seu E-mail</label>
            <div className="relative group">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#8A9099] group-focus-within:text-[#748FCC] transition-colors" />
              <input 
                type="email" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full h-16 px-6 pl-12 rounded-2xl border border-[#1F2329] bg-[#121417] text-[#F5F5F7] focus:border-[#748FCC]/50 focus:outline-none transition-all"
                placeholder="exemplo@email.com"
                required 
              />
            </div>
          </div>

          {error && <p className="text-red-400 text-sm text-center font-medium">{error}</p>}
          {message && <p className="text-emerald-400 text-sm text-center font-medium">{message}</p>}

          <button 
            type="submit" 
            disabled={loading}
            className="w-full h-16 bg-[#748FCC] text-[#F5F5F7] rounded-2xl font-bold text-lg hover:bg-[#5F7DB8] transition-all flex justify-center items-center gap-3 disabled:opacity-50 shadow-lg shadow-[#748FCC]/10"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Enviar Link'}
          </button>
        </form>

        <div className="text-center">
          <Link href="/login" className="inline-flex items-center gap-2 text-[#B8BCC4] hover:text-[#748FCC] transition-colors text-sm">
            <ArrowLeft className="w-4 h-4" /> Voltar para o Login
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
