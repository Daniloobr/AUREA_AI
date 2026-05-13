'use client';

import React from 'react';
import Link from 'next/link';
import { Sparkles, Crown, LogOut } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

export function Navbar() {
  const { user, logout } = useAuth();

  return (
    <header className="w-full fixed top-0 z-[100] transition-all duration-300 bg-onyx-950/60 backdrop-blur-xl border-b border-white/5">
      <div className="max-w-[1400px] mx-auto px-6 md:px-10 h-16 flex items-center justify-between">
        
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-purple to-brand-lavender flex items-center justify-center text-white shadow-lg group-hover:shadow-brand-purple/25 transition-all duration-500">
            <Sparkles className="w-4 h-4" />
          </div>
          <span className="font-display font-bold text-xl tracking-tight text-white">
            Lumière
          </span>
        </Link>
        
        {/* Navigation */}
        <nav className="hidden md:flex items-center gap-8">
          <Link href="/generate" className="text-sm font-medium text-zinc-400 hover:text-white transition-colors">
            Estúdio
          </Link>
          <Link href="/history" className="text-sm font-medium text-zinc-400 hover:text-white transition-colors">
            Galeria
          </Link>
          <Link href="/pricing" className="text-sm font-medium text-brand-lavender hover:text-white transition-colors flex items-center gap-1.5">
            <Crown className="w-3.5 h-3.5" /> Planos
          </Link>
        </nav>
        
        {/* User Actions */}
        <div className="flex items-center gap-4">
          {user ? (
            <>
              <div className="hidden sm:flex items-center gap-2 bg-white/5 px-3 py-1.5 rounded-full border border-white/10">
                <div className="w-1.5 h-1.5 rounded-full bg-brand-emerald shadow-[0_0_8px_rgba(129,227,134,0.5)]" />
                <span className="font-display font-semibold text-[11px] tracking-wider text-zinc-300 uppercase">
                  {user.credits_balance} Créditos
                </span>
              </div>
              
              <div className="h-4 w-[1px] bg-white/10 hidden sm:block" />
              
              <button 
                onClick={logout}
                className="text-sm font-medium text-zinc-400 hover:text-rose-400 transition-colors flex items-center gap-2 group"
              >
                <LogOut className="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" />
                <span className="hidden sm:inline">Sair</span>
              </button>
            </>
          ) : (
            <Link 
              href="/login" 
              className="bg-white text-black px-5 py-2 rounded-full text-sm font-bold hover:bg-brand-lavender transition-all"
            >
              Entrar
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}
