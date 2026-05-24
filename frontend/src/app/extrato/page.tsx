'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/services/api';
import { CreditCard, Loader2, ArrowUpRight, ArrowDownLeft, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import type { Transaction } from '@/types';
import { usePageTitle } from '@/hooks/usePageTitle';

export default function ExtratoPage() {
  usePageTitle('Extrato');
  const { user, token } = useAuth();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTransactions = async () => {
      if (!token) return;
      try {
        setLoading(true);
        setError(null);
        const res = await apiService.get('/auth/user/transactions', token);
        if (res.transactions) {
          setTransactions(res.transactions);
        } else if (res.error) {
          setError(res.error);
        }
      } catch (err) {
        console.error('Erro ao buscar transações:', err);
        setError('Não foi possível carregar o extrato.');
      } finally {
        setLoading(false);
      }
    };
    fetchTransactions();
  }, [token]);

  const translateType = (type: string) => {
    const types: Record<string, string> = {
      purchase: 'Compra',
      generation_cost: 'Uso em ensaio',
      credit_refund: 'Reembolso',
      admin_credit: 'Bônus administrativo'
    };
    return types[type] || type;
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-[#F5F5F7] p-6 md:p-12 font-sans">
      <div className="max-w-5xl mx-auto space-y-10 pt-8">

        {/* ── Cabeçalho ──────────────────────────────────────────────── */}
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
            className="space-y-2"
          >
            <Link href="/dashboard" className="inline-flex items-center gap-2 text-[#B8BCC4] hover:text-[#F5F5F7] transition-colors mb-4 text-sm">
              <ArrowLeft className="w-4 h-4" />
              Voltar ao Painel
            </Link>
            <p className="text-[10px] font-bold uppercase tracking-[0.4em] text-[#B8BCC4]">
              AureaIA™ • Minha Conta
            </p>
            <h1 className="text-4xl md:text-5xl font-serif font-medium tracking-tight text-[#F5F5F7] flex items-center gap-4">
              <CreditCard className="w-10 h-10 text-[#748FCC]" />
              Extrato de Moedas
            </h1>
            <p className="text-[#B8BCC4] font-light">
              Histórico detalhado das suas movimentações de créditos.
            </p>
          </motion.div>
        </header>

        {/* ── Tabela ─────────────────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-[#121417] border border-[#1F2329] rounded-[32px] overflow-hidden shadow-[0_0_40px_rgba(116,143,204,0.05)]"
        >
          {loading ? (
            <div className="py-24 flex flex-col items-center justify-center text-[#B8BCC4] gap-4">
              <Loader2 className="w-10 h-10 animate-spin text-[#748FCC]" />
              <p>Carregando extrato...</p>
            </div>
          ) : error ? (
            <div className="py-24 flex flex-col items-center justify-center text-red-400 gap-4">
              <p>{error}</p>
              <button 
                onClick={() => window.location.reload()}
                className="px-6 py-2 bg-red-400/10 hover:bg-red-400/20 rounded-xl transition-colors font-medium text-sm"
              >
                Tentar Novamente
              </button>
            </div>
          ) : transactions.length === 0 ? (
            <div className="py-24 flex flex-col items-center justify-center text-[#B8BCC4]">
              <CreditCard className="w-16 h-16 opacity-20 mb-4 text-[#748FCC]" />
              <p>Você ainda não possui movimentações de moedas.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse min-w-[700px]">
                <thead>
                  <tr className="border-b border-[#1F2329] bg-[#1A1D24]">
                    <th className="p-6 text-[11px] uppercase tracking-wider text-[#B8BCC4] font-bold whitespace-nowrap">Data / Hora</th>
                    <th className="p-6 text-[11px] uppercase tracking-wider text-[#B8BCC4] font-bold">Tipo</th>
                    <th className="p-6 text-[11px] uppercase tracking-wider text-[#B8BCC4] font-bold">Descrição</th>
                    <th className="p-6 text-[11px] uppercase tracking-wider text-[#B8BCC4] font-bold text-right whitespace-nowrap">Valor</th>
                    <th className="p-6 text-[11px] uppercase tracking-wider text-[#B8BCC4] font-bold text-right whitespace-nowrap">Saldo Atual</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1F2329]">
                  {transactions.map((txn) => (
                    <tr key={txn.id} className="hover:bg-white/[0.02] transition-colors">
                      <td className="p-6 text-sm text-[#B8BCC4] whitespace-nowrap">
                        {new Date(txn.created_at).toLocaleString('pt-BR', {
                          day: '2-digit', month: '2-digit', year: 'numeric',
                          hour: '2-digit', minute: '2-digit'
                        })}
                      </td>
                      <td className="p-6 text-sm text-[#F5F5F7]">
                        <span className="inline-flex items-center px-2.5 py-1 rounded-md bg-[#1F2329] text-xs font-medium border border-white/5">
                          {translateType(txn.type)}
                        </span>
                      </td>
                      <td className="p-6 text-sm text-[#F5F5F7] max-w-xs truncate" title={txn.description}>
                        {txn.description}
                      </td>
                      <td className="p-6 text-sm font-bold text-right whitespace-nowrap">
                        <div className={`flex items-center justify-end gap-1.5 ${txn.amount > 0 ? 'text-emerald-400' : 'text-[#B8BCC4]'}`}>
                          {txn.amount > 0 ? (
                            <ArrowDownLeft className="w-4 h-4 shrink-0" />
                          ) : (
                            <ArrowUpRight className="w-4 h-4 shrink-0" />
                          )}
                          {txn.amount > 0 ? '+' : ''}{txn.amount}
                        </div>
                      </td>
                      <td className="p-6 text-sm font-medium text-[#748FCC] text-right whitespace-nowrap">
                        {txn.balance_after}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
