import { createClient } from '@supabase/supabase-js';

// Usamos placeholders para evitar que o build (prerender) quebre na Vercel 
// caso as variáveis não estejam configuradas no momento do build.
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://placeholder.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'placeholder';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
