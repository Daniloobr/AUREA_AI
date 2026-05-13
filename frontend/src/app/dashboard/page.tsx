'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/services/api';
import { Sparkles, Camera, History, CreditCard, ChevronRight, Wand2 } from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
  const { user, token } = useAuth();
  const [stats, setStats] = useState({ jobs: 0, credits: 0 });

  useEffect(() => {
    const fetchStats = async () => {
      if (token) {
        const response = await apiService.get('/gallery', token);
        if (response.gallery) {
          setStats({
            jobs: response.count,
            credits: user?.credits_balance || 0
          });
        }
      }
    };
    fetchStats();
  }, [token, user]);

  return (
    <div className="min-h-screen bg-onyx-950 p-6 md:p-12 font-inter">
      <div className="max-w-7xl mx-auto space-y-12">
        
        {/* Header Section */}
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-4xl md:text-5xl font-bold text-white font-sora tracking-tight mb-2">
              Olá, <span className="text-brand-purple">{user?.name.split(' ')[0]}</span>
            </h1>
            <p className="text-zinc-400 font-medium">Bem-vinda ao seu estúdio fotográfico de elite.</p>
          </motion.div>

          <Link 
            href="/generate"
            className="group relative px-8 py-4 bg-white text-black rounded-2xl font-bold flex items-center gap-3 hover:scale-[1.02] active:scale-[0.98] transition-all overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-brand-purple/20 to-brand-lavender/20 opacity-0 group-hover:opacity-100 transition-opacity" />
            <Wand2 className="w-5 h-5" />
            Novo Ensaio IA
            <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Link>
        </header>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { label: 'Créditos Disponíveis', value: user?.credits_balance, icon: CreditCard, color: 'text-brand-emerald', bg: 'bg-brand-emerald/10' },
            { label: 'Ensaios Realizados', value: stats.jobs, icon: Camera, color: 'text-brand-purple', bg: 'bg-brand-purple/10' },
            { label: 'Fotos Geradas', value: stats.jobs * 4, icon: Sparkles, color: 'text-brand-lavender', bg: 'bg-brand-lavender/10' },
          ].map((stat, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="bg-white/5 border border-white/10 p-8 rounded-[32px] group hover:border-white/20 transition-all"
            >
              <div className={`${stat.bg} ${stat.color} w-12 h-12 rounded-2xl flex items-center justify-center mb-6`}>
                <stat.icon className="w-6 h-6" />
              </div>
              <p className="text-zinc-500 font-bold text-xs uppercase tracking-[0.2em] mb-1">{stat.label}</p>
              <h3 className="text-4xl font-bold text-white tracking-tighter">{stat.value}</h3>
            </motion.div>
          ))}
        </div>

        {/* Quick Actions / Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white/5 border border-white/10 rounded-[40px] p-10 overflow-hidden relative group">
            <div className="absolute top-0 right-0 w-64 h-64 bg-brand-purple/10 blur-[80px] rounded-full pointer-events-none group-hover:bg-brand-purple/20 transition-all" />
            <h2 className="text-2xl font-bold text-white mb-8 flex items-center gap-3 font-sora">
              <Sparkles className="text-brand-lavender w-6 h-6" />
              Recém Criadas
            </h2>
            <div className="flex flex-col items-center justify-center py-12 text-center space-y-4">
              <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center border border-white/10">
                <History className="text-zinc-600 w-8 h-8" />
              </div>
              <p className="text-zinc-500 font-medium max-w-[280px]">
                Suas gerações recentes aparecerão aqui. Comece um novo ensaio agora!
              </p>
              <Link href="/history" className="text-brand-purple font-bold hover:underline">Ver galeria completa</Link>
            </div>
          </div>

          <div className="bg-gradient-to-br from-brand-purple/20 to-brand-lavender/10 border border-white/10 rounded-[40px] p-10 flex flex-col justify-between">
            <div>
              <h2 className="text-3xl font-bold text-white mb-4 font-sora tracking-tight">Vire Pro</h2>
              <p className="text-zinc-300 font-medium leading-relaxed mb-8">
                Desbloqueie estilos exclusivos, gerações ilimitadas e resolução 4K para suas memórias mais preciosas.
              </p>
            </div>
            <button className="w-full bg-white/10 backdrop-blur-md border border-white/20 text-white rounded-2xl py-5 font-bold hover:bg-white/20 transition-all flex items-center justify-center gap-2">
              <Crown className="w-5 h-5 text-brand-lavender" />
              Ver Planos Premium
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

const Crown = ({ className }: { className?: string }) => (
  <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m2 4 3 12h14l3-12-6 7-4-7-4 7-6-7zm3 16h14"/></svg>
);
