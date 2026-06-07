'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import { apiService } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import { Loader2 } from 'lucide-react';

export default function AuthCallback() {
  const router = useRouter();
  const { login } = useAuth();

  useEffect(() => {
    const handleCallback = async () => {
      const { data: { session }, error } = await supabase.auth.getSession();

      if (error || !session) {
        console.error('Erro na sessão Supabase:', error);
        router.push('/login?error=auth_failed');
        return;
      }

      const user = session.user;

      try {
        // Sync with Flask Backend
        const response = await apiService.post('/auth/google-login', {
          access_token: session.access_token
        });

        if (response.success) {
          // Use the login function from AuthContext to set tokens and redirect
          login(response.token, response.user);
        } else {
          router.push('/login?error=sync_failed');
        }
      } catch (err) {
        console.error('Erro de sincronização com backend:', err);
        router.push('/login?error=server_error');
      }
    };

    handleCallback();
  }, [router, login]);

  return (
    <div className="min-h-screen bg-onyx-950 flex flex-col items-center justify-center text-white space-y-4">
      <Loader2 className="w-12 h-12 text-brand-purple animate-spin" />
      <div className="text-center">
        <h2 className="text-2xl font-display font-bold">Autenticando...</h2>
        <p className="text-zinc-500">Sincronizando sua conta premium com o estúdio.</p>
      </div>
    </div>
  );
}
