'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { apiService } from '@/services/api';
import Link from 'next/link';
import { ArrowLeft, Mail, Loader2, Sparkles } from 'lucide-react';

export default function ForgotPasswordPage() {
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
    } catch (err) {
      setError('Erro de conexão.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-onyx-950 text-white flex items-center justify-center p-6 font-sans">
      <div className="absolute top-[-20%] right-[-20%] w-[600px] h-[600px] rounded-full bg-brand-purple/5 blur-[120px] pointer-events-none" />

      <motion.div 
        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-[440px] space-y-8"
      >
        <div className="text-center space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-brand-purple/20 flex items-center justify-center text-brand-lavender mx-auto">
            <Sparkles className="w-6 h-6" />
          </div>
          <h1 className="text-3xl font-display font-bold tracking-tighter">Recuperar Senha</h1>
          <p className="text-zinc-500 font-light">Enviaremos um link de acesso para o seu e-mail.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest ml-1">Seu E-mail</label>
            <div className="relative group">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-600 group-focus-within:text-brand-purple transition-colors" />
              <input 
                type="email" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full h-16 px-6 pl-12 rounded-2xl border border-white/5 bg-white/[0.03] text-white focus:border-brand-purple/50 focus:outline-none transition-all"
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
            className="w-full h-16 bg-white text-black rounded-2xl font-bold text-lg hover:bg-zinc-200 transition-all flex justify-center items-center gap-3 disabled:opacity-50"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Enviar Link'}
          </button>
        </form>

        <div className="text-center">
          <Link href="/login" className="inline-flex items-center gap-2 text-zinc-500 hover:text-white transition-colors text-sm">
            <ArrowLeft className="w-4 h-4" /> Voltar para o Login
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
