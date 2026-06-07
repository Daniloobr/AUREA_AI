declare global {
  interface Window {
    fbq: (...args: unknown[]) => void;
    _fbq: unknown;
  }
}

export const FB_PIXEL_ID = '958814876737576';

export function pageView(): void {
  if (typeof window !== 'undefined' && window.fbq) {
    window.fbq('track', 'PageView');
  }
}

export function event(name: string, options: Record<string, unknown> = {}): void {
  if (typeof window !== 'undefined' && window.fbq) {
    window.fbq('track', name, options);
  }
}

export function purchase(value: number, transactionId: string): void {
  if (typeof window !== 'undefined' && window.fbq) {
    window.fbq('track', 'Purchase', {
      value,
      currency: 'BRL',
      transaction_id: transactionId,
    });
  }
}
