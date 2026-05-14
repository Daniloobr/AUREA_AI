'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/services/api';
import { 
  Users, Image as ImageIcon, CreditCard, Activity, 
  Trash2, Plus, Loader2, AlertCircle, ChevronRight,
  TrendingUp, Clock, CheckCircle, Sparkles
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
      const res = await apiService.remove(`/admin/users/${userId}`, token!);

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
      <div className="min-h-screen bg-aurea-bg flex items-center justify-center text-aurea-text">
        <div className="text-center space-y-6">
          <AlertCircle className="w-16 h-16 text-aurea-primary mx-auto" />
          <h1 className="text-3xl font-serif font-medium">Acesso Restrito</h1>
          <p className="text-aurea-text/40">Esta área é exclusiva para a curadoria da AureaIA.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-aurea-bg text-aurea-text font-sans p-8 md:p-12">
      <div className="max-w-7xl mx-auto space-y-12">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-8">
          <div className="space-y-2">
            <h1 className="text-4xl font-serif font-medium text-aurea-text">Admin <span className="italic text-aurea-primary">Panel</span></h1>
            <p className="text-aurea-text/40 font-medium">Gestão centralizada da AureaIA.</p>
          </div>
          <div className="flex bg-white/40 p-1.5 rounded-2xl border border-aurea-primary/10 backdrop-blur-md shadow-sm">
            {(['overview', 'users', 'jobs'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-6 py-2.5 rounded-xl text-xs font-bold uppercase tracking-widest transition-all ${
                  activeTab === tab ? 'bg-aurea-primary text-white shadow-md' : 'text-aurea-text/40 hover:text-aurea-text'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="h-96 flex flex-col items-center justify-center gap-4">
            <Loader2 className="w-12 h-12 text-aurea-primary animate-spin" />
            <p className="text-aurea-text/40 font-bold uppercase tracking-widest text-[10px]">Sincronizando Dados...</p>
          </div>
        ) : (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-12">
            {activeTab === 'overview' && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                <StatCard icon={<Users />} label="Usuárias" value={stats.total_users} trend="+12%" />
                <StatCard icon={<ImageIcon />} label="Criações" value={stats.total_jobs} trend="+5.4%" />
                <StatCard icon={<CheckCircle />} label="Concluídos" value={stats.completed_jobs} />
                <StatCard icon={<Clock />} label="Últimas 24h" value={stats.jobs_24h} color="text-aurea-primary" />
              </div>
            )}

            {activeTab === 'users' && (
              <div className="bg-white/40 border border-aurea-primary/10 rounded-[40px] overflow-hidden backdrop-blur-md shadow-sm">
                <table className="w-full text-left">
                  <thead className="bg-aurea-primary/5 text-aurea-text/40 text-[10px] uppercase tracking-[0.2em] font-bold">
                    <tr>
                      <th className="px-8 py-6">Usuária</th>
                      <th className="px-8 py-6 text-center">Saldo</th>
                      <th className="px-8 py-6">Status</th>
                      <th className="px-8 py-6 text-right">Gestão</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-aurea-primary/5">
                    {users.map((u) => (
                      <tr key={u.id} className="hover:bg-white/40 transition-colors">
                        <td className="px-8 py-6">
                          <div className="font-bold text-aurea-text">{u.name}</div>
                          <div className="text-xs text-aurea-text/40">{u.email}</div>
                        </td>
                        <td className="px-8 py-6 text-center">
                          <span className="bg-aurea-primary/10 text-aurea-primary px-4 py-1.5 rounded-full text-xs font-bold border border-aurea-primary/20">
                            {u.credits_balance} 🪙
                          </span>
                        </td>
                        <td className="px-8 py-6">
                          {u.is_active ? 
                            <span className="text-emerald-600 text-[10px] font-bold uppercase tracking-widest flex items-center gap-2"><Activity className="w-3 h-3" /> Ativa</span> : 
                            <span className="text-red-400 text-[10px] font-bold uppercase tracking-widest flex items-center gap-2"><AlertCircle className="w-3 h-3" /> Suspensa</span>
                          }
                        </td>
                        <td className="px-8 py-6 text-right space-x-3">
                          <button onClick={() => handleAddCredits(u.id)} className="p-3 bg-white/50 hover:bg-aurea-primary hover:text-white rounded-xl transition-all shadow-sm">
                            <Plus className="w-5 h-5" />
                          </button>
                          <button onClick={() => handleDeleteUser(u.id)} className="p-3 bg-white/50 hover:bg-red-500 hover:text-white rounded-xl transition-all shadow-sm">
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
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {jobs.map((job) => (
                  <div key={job.id} className="bg-white/40 border border-aurea-primary/10 p-8 rounded-[36px] flex flex-col gap-6 group hover:border-aurea-primary/30 transition-all backdrop-blur-md shadow-sm">
                    <div className="flex items-center justify-between">
                      <div className={`w-3 h-3 rounded-full ${job.status === 'completed' ? 'bg-emerald-500' : 'bg-aurea-primary animate-pulse'}`} />
                      <div className="text-[10px] font-bold text-aurea-text/30 uppercase tracking-widest">{job.status}</div>
                    </div>
                    <div className="space-y-1">
                      <div className="font-bold text-aurea-text truncate">{job.user_email}</div>
                      <div className="text-[10px] text-aurea-text/40 font-bold uppercase tracking-[0.2em]">{job.tipo_ensaio}</div>
                    </div>
                    <div className="flex items-center justify-between pt-4 border-t border-aurea-primary/5">
                      <div className="text-xl font-serif font-medium">{job.progress}%</div>
                      <ChevronRight className="text-aurea-text/20 group-hover:text-aurea-primary transition-colors" />
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

function StatCard({ icon, label, value, trend, color = "text-aurea-text" }: any) {
  return (
    <div className="bg-white/40 border border-aurea-primary/10 p-8 rounded-[40px] space-y-6 hover:border-aurea-primary/30 transition-all backdrop-blur-md shadow-sm">
      <div className="flex justify-between items-start">
        <div className="p-4 bg-aurea-primary/5 rounded-2xl text-aurea-primary">{icon}</div>
        {trend && (
          <div className="flex items-center gap-1 text-emerald-600 text-[10px] font-bold bg-emerald-50 px-3 py-1.5 rounded-full border border-emerald-100">
            <TrendingUp className="w-3 h-3" /> {trend}
          </div>
        )}
      </div>
      <div>
        <div className="text-aurea-text/40 text-xs font-bold uppercase tracking-[0.2em] mb-1">{label}</div>
        <div className={`text-4xl font-serif font-medium ${color}`}>{value}</div>
      </div>
    </div>
  );
}
