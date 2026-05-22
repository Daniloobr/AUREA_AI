'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Sparkles, Menu, X, User, Image, CreditCard, HelpCircle, LogOut } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/Button";

export function Navbar() {
  const { user, logout } = useAuth();
  const pathname = usePathname();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [logoError, setLogoError] = useState(false);
  const isLanding = pathname === '/';

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  interface NavItem {
    name: string;
    href: string;
    icon?: React.ComponentType<any>;
  }

  const landingLinks: NavItem[] = [
    { name: 'Início', href: '#hero' },
    { name: 'Como Funciona', href: '#como-funciona' },
    { name: 'Galeria Editorial', href: '#exemplos' },
    { name: 'Planos', href: '/credits' },
  ];

  const authLinks: NavItem[] = [
    { name: 'Criar Ensaio', href: '/generate', icon: Sparkles },
    { name: 'Galeria Privada', href: '/gallery', icon: Image },
    { name: 'Adquirir Créditos', href: '/credits', icon: CreditCard },
    { name: 'Minha Conta', href: '/dashboard', icon: User },
  ];

  const navItems = isLanding && !user ? landingLinks : authLinks;

  return (
    <header className={`fixed top-0 left-0 right-0 z-[100] transition-all duration-500 h-20 border-b ${scrolled ? 'bg-[#0A0A0A]/95 backdrop-blur-xl border-white/8' : 'bg-transparent border-transparent'}`}>
      <div className="max-w-[1400px] mx-auto px-6 md:px-10 h-full flex items-center justify-between">

        {/* Logo */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-9 h-9 rounded-xl flex items-center justify-center transition-all duration-500 group-hover:scale-105">
            {!logoError ? (
              <img
                src="/logo-aurea.png"
                alt="AureaIA Logo"
                className="w-full h-full object-contain"
                onError={() => setLogoError(true)}
              />
            ) : (
              <div className="w-full h-full rounded-xl bg-[#748FCC] flex items-center justify-center text-[#F5F5F7] shadow-lg shadow-[#748FCC]/10">
                <Sparkles className="w-4 h-4" />
              </div>
            )}
          </div>
          <span className="font-serif font-bold text-xl tracking-widest text-[#F5F5F7] uppercase opacity-90 group-hover:opacity-100 transition-opacity">
            AureaIA
          </span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden lg:flex items-center gap-8">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`text-[13px] font-medium transition-all duration-300 hover:text-[#F5F5F7] ${pathname === item.href ? 'text-[#F5F5F7]' : 'text-[#B8BCC4]'
                }`}
            >
              {item.name}
            </Link>
          ))}
        </nav>

        {/* User / Auth */}
        <div className="flex items-center gap-5">
          {user ? (
            <div className="hidden md:flex items-center gap-5">
              <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-[#121417] border border-white/10">
                <span className="text-[11px] font-bold text-[#F5F5F7] tracking-[0.1em]">✦ {user.credits_balance} MOEDAS</span>
              </div>
              <button
                onClick={logout}
                className="text-[#B8BCC4] hover:text-[#748FCC] transition-all duration-300"
                title="Sair do Estúdio"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          ) : (
            <Link href="/login">
              <Button className="h-10 px-6 text-[12px] font-semibold rounded-full bg-[#748FCC] hover:bg-[#5F7DB8] flex items-center gap-2">
                <Sparkles className="w-3.5 h-3.5" />
                Acessar Studio
              </Button>
            </Link>
          )}

          {/* Mobile Menu Toggle */}
          <button
            className="lg:hidden text-white p-2 hover:bg-white/5 rounded-full transition-colors"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            aria-label="Menu de navegação"
          >
            {isMenuOpen ? <X className="w-7 h-7" /> : <Menu className="w-7 h-7" />}
          </button>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isMenuOpen && (
        <div className="lg:hidden absolute top-20 left-0 right-0 bg-[#0A0A0A] border-b border-white/10 shadow-2xl animate-fade-in h-[calc(100vh-80px)] overflow-y-auto">
          <nav className="flex flex-col p-6 gap-2">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setIsMenuOpen(false)}
                className={`text-base font-medium py-4 px-2 rounded-xl transition-colors flex items-center gap-3 ${pathname === item.href ? 'text-[#F5F5F7] bg-white/5' : 'text-[#B8BCC4] hover:bg-white/5 hover:text-[#F5F5F7]'
                  }`}
              >
                {item.icon && <item.icon className="w-5 h-5 text-[#748FCC]" />}
                {item.name}
              </Link>
            ))}
            {user && (
              <div className="mt-4 pt-4 border-t border-white/10 flex flex-col gap-2">
                <div className="py-4 px-2 flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-[#748FCC]/20 flex items-center justify-center">
                    <Sparkles className="w-4 h-4 text-[#748FCC]" />
                  </div>
                  <div>
                    <p className="text-xs text-[#B8BCC4]">Saldo atual</p>
                    <span className="text-sm font-bold text-[#F5F5F7] tracking-[0.05em] uppercase">{user.credits_balance} Moedas</span>
                  </div>
                </div>
                <button
                  onClick={() => {
                    logout();
                    setIsMenuOpen(false);
                  }}
                  className="text-base font-medium text-red-400 py-4 px-2 rounded-xl flex items-center gap-3 hover:bg-red-500/10 transition-colors w-full text-left"
                >
                  <LogOut className="w-5 h-5" />
                  Sair do Estúdio
                </button>
              </div>
            )}
            {!user && isLanding && (
              <div className="mt-4 pt-4 border-t border-white/10 px-2">
                <Link href="/login" onClick={() => setIsMenuOpen(false)}>
                  <Button className="w-full h-12 text-sm font-semibold rounded-xl bg-[#748FCC] hover:bg-[#5F7DB8] flex items-center justify-center gap-2">
                    <Sparkles className="w-4 h-4" />
                    Acessar Studio
                  </Button>
                </Link>
              </div>
            )}
          </nav>
        </div>
      )}
    </header>
  );
}
