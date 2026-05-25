import { apiService } from '@/services/api';

const MP_PUBLIC_KEY = process.env.NEXT_PUBLIC_MP_PUBLIC_KEY || '';

let mpInstance: any = null;

function loadScript(src: string): Promise<void> {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${src}"]`)) {
      resolve();
      return;
    }
    const script = document.createElement('script');
    script.src = src;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error(`Falha ao carregar ${src}`));
    document.body.appendChild(script);
  });
}

export async function initMercadoPago(): Promise<any> {
  if (mpInstance) return mpInstance;
  await loadScript('https://sdk.mercadopago.dev/js/v2');
  if (typeof window !== 'undefined' && (window as any).MercadoPago) {
    mpInstance = new (window as any).MercadoPago(MP_PUBLIC_KEY);
    return mpInstance;
  }
  throw new Error('MercadoPago SDK não carregado');
}

export async function createCardToken(cardData: {
  cardNumber: string;
  cardExpirationMonth: string;
  cardExpirationYear: string;
  securityCode: string;
  cardholderName: string;
  docType?: string;
  docNumber?: string;
}): Promise<string> {
  const mp = await initMercadoPago();
  return new Promise((resolve, reject) => {
    mp.createCardToken({
      cardNumber: cardData.cardNumber,
      cardExpirationMonth: cardData.cardExpirationMonth,
      cardExpirationYear: cardData.cardExpirationYear,
      securityCode: cardData.securityCode,
      cardholderName: cardData.cardholderName,
      ...(cardData.docType && cardData.docNumber
        ? { cardholder: { identification: { type: cardData.docType, number: cardData.docNumber } } }
        : {}),
    }, (error: any, token: any) => {
      if (error) {
        reject(new Error(error.message || 'Erro ao tokenizar cartão'));
      } else {
        resolve(token.id);
      }
    });
  });
}

export async function createPixPayment(packageId: string, token: string) {
  return apiService.post('/create-pix-payment', { package_id: packageId }, token);
}

export async function createCardPayment(packageId: string, cardToken: string, authToken: string) {
  return apiService.post('/create-card-payment', {
    package_id: packageId,
    card_token: cardToken,
  }, authToken);
}

export async function checkPaymentStatus(paymentId: string, authToken: string) {
  return apiService.get(`/payment-status/${paymentId}`, authToken);
}
