import { apiService } from '@/services/api';

const MP_PUBLIC_KEY = process.env.NEXT_PUBLIC_MP_PUBLIC_KEY || '';

let loaded = false;

function loadV1Script(): Promise<void> {
  return new Promise((resolve, reject) => {
    const src = 'https://secure.mlstatic.com/sdk/javascript/v1/mercadopago.js';
    if (document.querySelector(`script[src="${src}"]`)) {
      resolve();
      return;
    }
    const script = document.createElement('script');
    script.src = src;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Falha ao carregar MercadoPago V1 SDK'));
    document.body.appendChild(script);
  });
}

async function ensureMercadopago(): Promise<void> {
  if (loaded) return;
  await loadV1Script();
  const mp = (window as any).Mercadopago;
  if (!mp) throw new Error('MercadoPago SDK não disponível');
  mp.setPublishableKey(MP_PUBLIC_KEY);
  loaded = true;
}

export async function createCardToken(cardData: {
  cardNumber: string;
  cardExpirationMonth: string;
  cardExpirationYear: string;
  securityCode: string;
  cardholderName: string;
  docNumber?: string;
}): Promise<string> {
  await ensureMercadopago();
  const mp = (window as any).Mercadopago;
  return new Promise((resolve, reject) => {
    const payload: any = {
      cardNumber: cardData.cardNumber,
      cardExpirationMonth: cardData.cardExpirationMonth,
      cardExpirationYear: cardData.cardExpirationYear,
      securityCode: cardData.securityCode,
      cardholderName: cardData.cardholderName,
      cardholder: {
        identification: {
          type: 'CPF',
          number: cardData.docNumber || '12345678909',
        },
      },
    };
    mp.createCardToken(payload, (error: any, token: any) => {
      if (error) {
        reject(new Error(error.user_message || error.message || 'Erro ao tokenizar cartão'));
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
