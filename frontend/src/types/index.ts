export interface Transaction {
  id: string;
  type: string;
  amount: number;
  balance_before: number;
  balance_after: number;
  description: string;
  created_at: string;
}

export interface GalleryItem {
  id: string;
  status: string;
  progress: number;
  message: string;
  images: string[];
  result_url: string | null;
  result?: { result_url?: string };
  tipo_ensaio: string;
  created_at: string;
  error: string | null;
  metadata: Record<string, unknown>;
  cost_moedas: number;
}
