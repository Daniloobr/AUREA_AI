'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/services/api';
import { Sparkles, Camera, CreditCard, ChevronRight, Loader2, ArrowUpRight, ArrowDownLeft } from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
  const { user, token } = useAuth();
  const [jobCount, setJobCount] = useState(0);
  const [transactions, setTransactions] = useState<any[]>([]);
  const [loadingTxns, setLoadingTxns] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      if (!token) return;
      try {
        const [galleryRes, txnsRes] = await Promise.all([
          apiService.get('/gallery', token),
          apiService.get('/auth/user/transactions', token),
        ]);

        if (galleryRes.gallery) {
          setJobCount(galleryRes.count || galleryRes.gallery.length);
        }
        if (txnsRes.transactions) {
          setTransactions(txnsRes.transactions.slice(0, 5));
        }
      } catch (err) {
        console.error('Erro ao buscar dados do painel:', err);
      } finally {
        setLoadingTxns(false);
      }
    };
    fetchStats();
  }, [token, user]);

  const stats = [
    {
      label: 'Moedas Disponíveis',
      value: `✦ ${user?.credits_balance ?? 0}`,
      icon: CreditCard,
      href: '/credits',
    },
    {
      label: 'Ensaios Criados',
      value: jobCount,
      icon: Camera,
      href: '/gallery',
    },
    {
      label: 'Imagens Geradas',
      value: jobCount * 4,
      icon: Sparkles,
      href: '/gallery',
    },
  ];

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-[#F5F5F7] p-6 md:p-12 font-sans">
      <div className="max-w-5xl mx-auto space-y-14 pt-8">

        {/* ── Cabeçalho ──────────────────────────────────────────────── */}
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-8">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
            className="space-y-2"
          >
            <p className="text-[10px] font-bold uppercase tracking-[0.4em] text-[#B8BCC4]">
              AureaIA™ • Minha Conta
            </p>
            <h1 className="text-4xl md:text-5xl font-serif font-medium tracking-tight text-[#F5F5F7]">
              Olá, <span className="italic text-[#748FCC]">{user?.name?.split(' ')[0] ?? 'Artista'}</span>
            </h1>
            <p className="text-[#B8BCC4] font-light">
              Bem-vinda ao seu estúdio fotográfico particular.
            </p>
          </motion.div>

          <Link
            href="/generate"
            className="group inline-flex items-center gap-3 px-8 py-4 bg-[#748FCC] text-[#F5F5F7] rounded-[16px] font-bold hover:bg-[#5F7DB8] transition-all shadow-lg shadow-[#748FCC]/20 hover:shadow-[0_0_40px_rgba(116,143,204,0.35)] shrink-0"
          >
            <Sparkles className="w-5 h-5" />
            Acessar Ateliê
            <ChevronRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </Link>
        </header>

        {/* ── Stats ──────────────────────────────────────────────────── */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {stats.map((stat, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
            >
              <Link href={stat.href}>
                <div className="bg-[#121417] border border-[#1F2329] p-8 rounded-[24px] group hover:border-[#748FCC]/40 transition-all duration-500 cursor-pointer hover:shadow-[0_0_40px_rgba(116,143,204,0.15)]">
                  <div className="w-12 h-12 rounded-2xl bg-[#748FCC]/10 border border-[#748FCC]/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                    <stat.icon className="w-6 h-6 text-[#748FCC]" />
                  </div>
                  <p className="text-[#B8BCC4] font-bold text-[10px] uppercase tracking-[0.2em] mb-2">
                    {stat.label}
                  </p>
                  <h3 className="text-4xl font-medium text-[#F5F5F7] tracking-tight">{stat.value}</h3>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>

        {/* ── Extrato + Acesso rápido ─────────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

          {/* Extrato de créditos */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-[#121417] border border-[#1F2329] rounded-[32px] p-10 flex flex-col gap-8"
          >
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-serif font-medium flex items-center gap-3 text-[#F5F5F7]">
                <CreditCard className="w-5 h-5 text-[#748FCC]" />
                Extrato de Moedas
              </h2>
              <Link href="/extrato" className="text-sm font-medium text-[#748FCC] hover:text-[#5F7DB8] transition-colors">
                Ver tudo
              </Link>
            </div>

            <div className="space-y-3 flex-1">
              {loadingTxns ? (
                <div className="py-12 flex justify-center">
                  <Loader2 className="w-8 h-8 animate-spin text-[#748FCC]" />
                </div>
              ) : transactions.length > 0 ? (
                transactions.map((txn) => (
                  <div
                    key={txn.id}
                    className="flex items-center justify-between p-4 rounded-[16px] bg-white/[0.02] border border-white/5 hover:border-[#748FCC]/20 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      {txn.amount > 0 ? (
                        <ArrowDownLeft className="w-4 h-4 text-emerald-400 shrink-0" />
                      ) : (
                        <ArrowUpRight className="w-4 h-4 text-[#8A9099] shrink-0" />
                      )}
                      <div>
                        <span className="text-sm font-medium text-[#F5F5F7] block leading-tight line-clamp-1">
                          {txn.description}
                        </span>
                        <span className="text-[10px] text-[#B8BCC4] uppercase tracking-widest">
                          {new Date(txn.created_at).toLocaleDateString('pt-BR')}
                        </span>
                      </div>
                    </div>
                    <span className={`text-sm font-bold shrink-0 ml-4 ${txn.amount > 0 ? 'text-emerald-400' : 'text-[#B8BCC4]'}`}>
                      {txn.amount > 0 ? '+' : ''}{txn.amount}
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-[#B8BCC4] text-center py-12 font-light">
                  Nenhuma transação encontrada ainda.
                </p>
              )}
            </div>

            <Link
              href="/credits"
              className="w-full bg-[#748FCC] text-[#F5F5F7] rounded-[16px] py-4 font-bold hover:bg-[#5F7DB8] transition-all flex items-center justify-center gap-2 text-sm shadow-lg shadow-[#748FCC]/10"
            >
              Adquirir Moedas ✦
            </Link>
          </motion.div>

          {/* Acesso rápido */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-[#121417] border border-[#1F2329] rounded-[32px] p-10 flex flex-col gap-8"
          >
            <h2 className="text-2xl font-serif font-medium flex items-center gap-3 text-[#F5F5F7]">
              <Sparkles className="w-5 h-5 text-[#748FCC]" />
              Acesso Rápido
            </h2>

            <div className="flex flex-col gap-4 flex-1">
              {[
                { label: 'Ateliê de Criação', desc: 'Transforme suas fotos em obra-prima', href: '/generate' },
                { label: 'Sua Galeria', desc: 'Reveja seus ensaios eternizados', href: '/gallery' },
                { label: 'Adquirir Moedas', desc: 'Expanda seu acervo de memórias', href: '/credits' },
                { label: 'Extrato Completo', desc: 'Histórico de movimentação de moedas', href: '/extrato' },
                { label: 'Suporte & Ajuda', desc: 'Tire suas dúvidas com nossa equipe', href: '/help' },
              ].map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="group flex items-center justify-between p-5 rounded-[16px] bg-white/[0.02] border border-white/5 hover:border-[#748FCC]/30 hover:bg-[#748FCC]/5 transition-all duration-300"
                >
                  <div>
                    <p className="text-sm font-medium text-[#F5F5F7]">{item.label}</p>
                    <p className="text-[11px] text-[#B8BCC4] font-light mt-0.5">{item.desc}</p>
                  </div>
                  <ChevronRight className="w-4 h-4 text-[#B8BCC4] group-hover:text-[#748FCC] group-hover:translate-x-1 transition-all" />
                </Link>
              ))}
            </div>

            <p className="text-[10px] uppercase tracking-[0.3em] text-[#B8BCC4]/30 text-center font-bold">
              Seu momento. Eternizado.
            </p>
          </motion.div>
        </div>

      </div>
    </div>
  );
}
