import { apiService } from '@/services/api';

/**
 * Calls the backend to create a Stripe Checkout Session.
 * @param priceId The Stripe price ID for the credits package.
 * @param token The JWT authentication token of the user.
 */
export async function createCheckoutSession(priceId: string, token: string) {
  return await apiService.post('/create-checkout-session', { price_id: priceId }, token);
}
