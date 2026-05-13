'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/services/api';
import { 
  Users, Image as ImageIcon, CreditCard, Activity, 
  Trash2, Plus, Loader2, AlertCircle, ChevronRight,
  TrendingUp, Clock, CheckCircle
} from 'lucide-react';

export default function AdminDashboard() {
  const { token, user } = useAuth();
  const [stats, setStats] = useState<any>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'jobs'>('overview');

  useEffect(() => {
    if (!token) return;
    fetchData();
  }, [token]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [sRes, uRes, jRes] = await Promise.all([
        apiService.get('/admin/stats', token!),
        apiService.get('/admin/users', token!),
        apiService.get('/admin/jobs', token!)
      ]);
      setStats(sRes.stats);
      setUsers(uRes.users);
      setJobs(jRes.jobs);
    } catch (err) {
      console.error("Failed to fetch admin data", err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddCredits = async (userId: string) => {
    const amount = prompt("Quantidade de créditos a adicionar:");
    if (!amount) return;
    
    try {
      const res = await apiService.post(`/admin/users/${userId}/credits`, { 
        amount: parseInt(amount),
        reason: "Bônus administrativo" 
      }, token!);
      if (res.success) {
        alert("Créditos adicionados!");
        fetchData();
      }
    } catch (err) {
      alert("Erro ao adicionar créditos");
    }
  };

  const handleDeleteUser = async (userId: string) => {
    if (!confirm("Tem certeza que deseja desativar este usuário?")) return;
    try {
      const res = await apiService.delete(`/admin/users/${userId}`, token!);
      if (res.success) {
        alert("Usuário desativado.");
        fetchData();
      }
    } catch (err) {
      alert("Erro ao desativar usuário");
    }
  };

  if (!user?.is_admin) {
    return (
      <div className="min-h-screen bg-onyx-950 flex items-center justify-center text-white">
        <div className="text-center space-y-4">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto" />
          <h1 className="text-2xl font-bold">Acesso Negado</h1>
          <p className="text-zinc-500">Você não tem permissão para acessar esta área.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-onyx-950 text-white font-sans p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex justify-between items-end">
          <div>
            <h1 className="text-4xl font-display font-bold tracking-tighter">Admin <span className="text-gradient">Dashboard</span></h1>
            <p className="text-zinc-500">Gestão centralizada do Lumière Studios.</p>
          </div>
          <div className="flex bg-white/5 p-1 rounded-xl border border-white/10">
            {(['overview', 'users', 'jobs'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-6 py-2 rounded-lg text-sm font-bold transition-all ${
                  activeTab === tab ? 'bg-brand-purple text-white shadow-lg' : 'text-zinc-500 hover:text-white'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="h-96 flex items-center justify-center">
            <Loader2 className="w-12 h-12 text-brand-purple animate-spin" />
          </div>
        ) : (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">
            {activeTab === 'overview' && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard icon={<Users />} label="Usuários Ativos" value={stats.total_users} trend="+12%" />
                <StatCard icon={<ImageIcon />} label="Total Gerações" value={stats.total_jobs} trend="+5.4%" />
                <StatCard icon={<CheckCircle />} label="Jobs Concluídos" value={stats.completed_jobs} />
                <StatCard icon={<Clock />} label="Jobs (24h)" value={stats.jobs_24h} color="text-brand-lavender" />
              </div>
            )}

            {activeTab === 'users' && (
              <div className="bg-white/[0.02] border border-white/5 rounded-3xl overflow-hidden">
                <table className="w-full text-left">
                  <thead className="bg-white/5 text-zinc-500 text-xs uppercase tracking-widest font-bold">
                    <tr>
                      <th className="px-6 py-4">Usuário</th>
                      <th className="px-6 py-4">Créditos</th>
                      <th className="px-6 py-4">Status</th>
                      <th className="px-6 py-4 text-right">Ações</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {users.map((u) => (
                      <tr key={u.id} className="hover:bg-white/[0.01] transition-colors">
                        <td className="px-6 py-4">
                          <div className="font-bold">{u.name}</div>
                          <div className="text-xs text-zinc-500">{u.email}</div>
                        </td>
                        <td className="px-6 py-4">
                          <span className="bg-brand-purple/10 text-brand-lavender px-3 py-1 rounded-full text-xs font-bold border border-brand-purple/20">
                            {u.credits_balance} 🪙
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          {u.is_active ? 
                            <span className="text-emerald-400 text-xs flex items-center gap-1"><Activity className="w-3 h-3" /> Ativo</span> : 
                            <span className="text-red-400 text-xs flex items-center gap-1"><AlertCircle className="w-3 h-3" /> Suspenso</span>
                          }
                        </td>
                        <td className="px-6 py-4 text-right space-x-2">
                          <button onClick={() => handleAddCredits(u.id)} className="p-2 hover:bg-white/5 rounded-lg text-brand-lavender transition-colors">
                            <Plus className="w-5 h-5" />
                          </button>
                          <button onClick={() => handleDeleteUser(u.id)} className="p-2 hover:bg-red-500/10 rounded-lg text-red-400 transition-colors">
                            <Trash2 className="w-5 h-5" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {activeTab === 'jobs' && (
              <div className="space-y-4">
                {jobs.map((job) => (
                  <div key={job.id} className="bg-white/[0.02] border border-white/5 p-6 rounded-2xl flex items-center justify-between group hover:border-brand-purple/20 transition-all">
                    <div className="flex items-center gap-4">
                      <div className={`w-2 h-2 rounded-full ${job.status === 'completed' ? 'bg-emerald-500' : 'bg-brand-purple animate-pulse'}`} />
                      <div>
                        <div className="font-bold text-sm">{job.user_email}</div>
                        <div className="text-xs text-zinc-500 uppercase tracking-tighter">{job.tipo_ensaio} — {job.id}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-8">
                      <div className="text-right">
                        <div className="text-sm font-bold">{job.progress}%</div>
                        <div className="text-[10px] text-zinc-600 uppercase">{job.status}</div>
                      </div>
                      <ChevronRight className="text-zinc-700 group-hover:text-white transition-colors" />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, trend, color = "text-white" }: any) {
  return (
    <div className="bg-white/[0.02] border border-white/5 p-6 rounded-3xl space-y-4 hover:border-white/10 transition-colors">
      <div className="flex justify-between items-start">
        <div className="p-3 bg-white/5 rounded-2xl text-brand-lavender">{icon}</div>
        {trend && (
          <div className="flex items-center gap-1 text-emerald-400 text-xs font-bold bg-emerald-500/10 px-2 py-1 rounded-lg">
            <TrendingUp className="w-3 h-3" /> {trend}
          </div>
        )}
      </div>
      <div>
        <div className="text-zinc-500 text-sm font-medium">{label}</div>
        <div className={`text-3xl font-display font-bold ${color}`}>{value}</div>
      </div>
    </div>
  );
}
