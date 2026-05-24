import { describe, it, expect, vi, beforeEach } from 'vitest';

const API_BASE_URL = 'http://127.0.0.1:5000/api';

const apiService = {
  get: async (endpoint: string, token?: string) => {
    try {
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;
      const response = await fetch(`${API_BASE_URL}${endpoint}`, { headers, credentials: 'include' });
      if (response.status === 401) {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
          window.location.href = '/login?expired=true';
        }
        return { success: false, error: 'Sessão expirada. Por favor, faça login novamente.' };
      }
      return response.json();
    } catch {
      throw new Error('Não foi possível estabelecer conexão com o estúdio. Por favor, verifique sua rede.');
    }
  },

  post: async (endpoint: string, data: unknown, token?: string) => {
    try {
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST', headers, body: JSON.stringify(data), credentials: 'include',
      });
      if (response.status === 401) {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
          window.location.href = '/login?expired=true';
        }
        return { success: false, error: 'Sessão expirada.' };
      }
      return response.json();
    } catch {
      throw new Error('Não foi possível estabelecer conexão com o estúdio.');
    }
  },

  remove: async (endpoint: string, token?: string) => {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, { method: 'DELETE', headers, credentials: 'include' });
      if (response.status === 401) {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
          window.location.href = '/login?expired=true';
        }
        return { success: false, error: 'Sessão expirada.' };
      }
      return response.json();
    } catch {
      throw new Error('Conexão com o estúdio interrompida.');
    }
  },
};

describe('apiService', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    localStorage.clear();
  });

  describe('GET', () => {
    it('should make a successful request', async () => {
      const mockData = { success: true, data: 'test' };
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockData),
      });

      const result = await apiService.get('/test');
      expect(result).toEqual(mockData);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://127.0.0.1:5000/api/test',
        expect.objectContaining({
          headers: expect.objectContaining({ 'Content-Type': 'application/json' }),
          credentials: 'include',
        }),
      );
    });

    it('should include auth header when token provided', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve({}),
      });

      await apiService.get('/test', 'my-token');
      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({ Authorization: 'Bearer my-token' }),
        }),
      );
    });

    it('should redirect on 401', async () => {
      delete (window as any).location;
      window.location = { href: '' } as any;
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 401,
        json: () => Promise.resolve({}),
      });

      const result = await apiService.get('/test', 'invalid-token');
      expect(result.error).toContain('Sessão expirada');
      expect(window.location.href).toBe('/login?expired=true');
    });

    it('should return error object on non-401 HTTP error', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ error: 'Erro interno' }),
      });

      const result = await apiService.get('/test');
      expect(result.error).toBe('Erro interno');
    });

    it('should return error object when no error message', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        json: () => Promise.resolve({}),
      });

      const result = await apiService.get('/test');
      expect(result).toEqual({});
    });

    it('should throw on network failure', async () => {
      global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

      await expect(apiService.get('/test')).rejects.toThrow('Não foi possível estabelecer conexão');
    });
  });

  describe('POST', () => {
    it('should send JSON body', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ success: true }),
      });

      const body = { name: 'Teste', email: 'test@teste.com' };
      await apiService.post('/auth/register', body);

      expect(global.fetch).toHaveBeenCalledWith(
        'http://127.0.0.1:5000/api/auth/register',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(body),
        }),
      );
    });

    it('should return error object on error response', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 409,
        json: () => Promise.resolve({ error: 'Email já cadastrado' }),
      });

      const result = await apiService.post('/auth/register', {});
      expect(result.error).toBe('Email já cadastrado');
    });
  });

  describe('DELETE', () => {
    it('should make DELETE request', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ success: true }),
      });

      const result = await apiService.remove('/auth/user/account', 'token');
      expect(result).toEqual({ success: true });
      expect(global.fetch).toHaveBeenCalledWith(
        'http://127.0.0.1:5000/api/auth/user/account',
        expect.objectContaining({ method: 'DELETE' }),
      );
    });

    it('should throw on network failure', async () => {
      global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));
      await expect(apiService.remove('/auth/user/account')).rejects.toThrow('Conexão com o estúdio interrompida');
    });
  });
});
