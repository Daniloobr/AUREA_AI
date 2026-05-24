'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/Button';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Erro na aplicação:', error);
  }, [error]);

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-[#F5F5F7] flex items-center justify-center p-6">
      <div className="max-w-md text-center space-y-6">
        <div className="w-20 h-20 rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center mx-auto">
          <span className="text-4xl">⚠️</span>
        </div>
        <h1 className="text-3xl font-serif font-semibold">Algo deu errado</h1>
        <p className="text-[#B8BCC4] font-light leading-relaxed">
          Não se preocupe, nossa equipe já foi notificada. Tente novamente ou volte para o início.
        </p>
        <div className="flex items-center justify-center gap-4">
          <Button onClick={reset} variant="primary" className="px-8 py-3 rounded-xl">
            Tentar Novamente
          </Button>
          <a
            href="/"
            className="px-8 py-3 rounded-xl bg-white/5 border border-white/10 text-[#F5F5F7] hover:bg-white/10 transition-colors font-medium text-sm"
          >
            Voltar ao Início
          </a>
        </div>
      </div>
    </div>
  );
}
