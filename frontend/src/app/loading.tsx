import { Loader2 } from 'lucide-react';

export default function Loading() {
  return (
    <div className="min-h-screen bg-[#0A0A0A] flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <Loader2 className="w-10 h-10 animate-spin text-[#748FCC]" />
        <p className="text-[#B8BCC4] text-sm font-light">Carregando...</p>
      </div>
    </div>
  );
}
