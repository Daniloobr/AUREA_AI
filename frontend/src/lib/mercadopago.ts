import { apiService } from '@/services/api';

export async function createCheckoutPreference(
  packageId: string,
  token: string,
) {
  return await apiService.post(
    '/create-checkout-preference',
    { package_id: packageId },
    token,
  );
}
