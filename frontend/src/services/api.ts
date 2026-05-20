let _apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 
                     (process.env.NEXT_PUBLIC_BACKEND_URL ? `${process.env.NEXT_PUBLIC_BACKEND_URL}/api` : '/api');

// Remove barras no final
_apiBaseUrl = _apiBaseUrl.replace(/\/+$/, '');

// Garante que tenha /api no final se for uma URL completa
if (_apiBaseUrl.startsWith('http') && !_apiBaseUrl.endsWith('/api')) {
    _apiBaseUrl += '/api';
}

const API_BASE_URL = _apiBaseUrl;


export const apiService = {
  get: async (endpoint: string, token?: string) => {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'GET',
        headers,
        credentials: 'include',
      });
      
      if (response.status === 401) {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
          document.cookie = 'auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
          window.location.href = '/login?expired=true';
        }
        return { success: false, error: 'Sessão expirada. Por favor, faça login novamente.' };
      }
      
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.indexOf("application/json") !== -1) {
        return await response.json();
      } else {
        await response.text();
        return { success: false, error: `Indisponibilidade momentânea (${response.status}). Nossa equipe já foi notificada.` };
      }
    } catch (err: any) {
      console.error("Fetch error:", err);
      throw new Error('Não foi possível estabelecer conexão com o estúdio. Por favor, verifique sua rede.');
    }
  },

  post: async (endpoint: string, data: any, token?: string) => {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers,
        body: JSON.stringify(data),
        credentials: 'include',
      });
      
      if (response.status === 401) {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
          document.cookie = 'auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
          window.location.href = '/login?expired=true';
        }
        return { success: false, error: 'Sessão expirada. Por favor, faça login novamente.' };
      }
      
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.indexOf("application/json") !== -1) {
        return await response.json();
      } else {
        await response.text();
        return { success: false, error: `Ocorreu um imprevisto técnico (${response.status}). Por favor, tente novamente em alguns instantes.` };
      }
    } catch (err: any) {
      console.error("Fetch error:", err);
      throw new Error('Conexão com o estúdio interrompida. Certifique-se de que sua conexão está estável.');
    }
  },

  remove: async (endpoint: string, token?: string) => {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'DELETE',
      headers,
      credentials: 'include',
    });
    
    if (response.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token');
        document.cookie = 'auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
        window.location.href = '/login?expired=true';
      }
      return { success: false, error: 'Sessão expirada. Por favor, faça login novamente.' };
    }
    
    return response.json();
  }
};
