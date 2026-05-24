import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { usePageTitle } from '@/hooks/usePageTitle';

describe('usePageTitle', () => {
  beforeEach(() => {
    document.title = 'AureaIA™ | Seu ensaio de maternidade. Em casa. Em minutos.';
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should set document title with suffix', () => {
    const { unmount } = renderHook(() => usePageTitle('Teste'));
    expect(document.title).toBe('Teste | AureaIA™');
    unmount();
  });

  it('should restore previous title on unmount', () => {
    const previousTitle = 'AureaIA™ | Seu ensaio de maternidade. Em casa. Em minutos.';
    const { unmount } = renderHook(() => usePageTitle('Dashboard'));
    expect(document.title).toBe('Dashboard | AureaIA™');
    unmount();
    expect(document.title).toBe(previousTitle);
  });

  it('should update title when argument changes', () => {
    const { rerender, unmount } = renderHook(
      (title: string) => usePageTitle(title),
      { initialProps: 'Início' },
    );
    expect(document.title).toBe('Início | AureaIA™');
    rerender('Perfil');
    expect(document.title).toBe('Perfil | AureaIA™');
    unmount();
  });

  it('should handle empty string', () => {
    const { unmount } = renderHook(() => usePageTitle(''));
    expect(document.title).toBe('| AureaIA™');
    unmount();
  });

  it('should handle special characters', () => {
    const { unmount } = renderHook(() => usePageTitle('Criar Conta! @#$'));
    expect(document.title).toBe('Criar Conta! @#$ | AureaIA™');
    unmount();
  });
});
