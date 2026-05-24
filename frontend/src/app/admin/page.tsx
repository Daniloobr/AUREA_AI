import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Painel Administrativo | AureaIA™',
  robots: { index: false, follow: false },
};

export default function AdminPage() {
  return <div className="p-8">Painel Administrativo (em construção)</div>;
}
