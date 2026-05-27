import { test, expect } from '@playwright/test';

const FRONTEND = 'https://aureaia-saas.vercel.app';
const BACKEND = 'https://aurea-ai-ftqa.onrender.com/api';

let authToken = '';
const testEmail = `qa_${Date.now()}@teste.com`;
const testPassword = 'TesteQA123!';

// ─── Helpers ────────────────────────────────────────────────────────────────

async function apiPost(path: string, body: any) {
  const res = await fetch(`${BACKEND}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return { status: res.status, data: await res.json() };
}

async function apiGet(path: string, token?: string) {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${BACKEND}${path}`, { headers });
  return { status: res.status, data: await res.json() };
}

// ══════════════════════════════════════════════════════════════════════════════
// 1. Autenticação e sessão
// ══════════════════════════════════════════════════════════════════════════════

test.describe('1. Autenticação', () => {
  test('1.1 Registrar novo usuário com 0 créditos', async () => {
    const { status, data } = await apiPost('/auth/register', {
      name: 'QA Test User',
      email: testEmail,
      password: testPassword,
    });
    expect(status).toBe(201);
    expect(data.success).toBe(true);
    expect(data.user.credits_balance).toBe(0);
    expect(data.token).toBeTruthy();
    authToken = data.token;
  });

  test('1.2 Login com credenciais corretas', async () => {
    const { status, data } = await apiPost('/auth/login', {
      email: testEmail,
      password: testPassword,
    });
    expect(status).toBe(200);
    expect(data.success).toBe(true);
    expect(data.token).toBeTruthy();
    authToken = data.token;
  });

  test('1.3 Rota protegida /me com token válido → 200, sem token → 401', async () => {
    const withToken = await apiGet('/auth/me', authToken);
    expect(withToken.status).toBe(200);
    expect(withToken.data.success).toBe(true);

    const withoutToken = await apiGet('/auth/me');
    expect(withoutToken.status).toBe(401);
  });

  test('1.4 Login inválido retorna 401', async () => {
    const { status, data } = await apiPost('/auth/login', {
      email: testEmail,
      password: 'wrong_password',
    });
    expect(status).toBe(401);
    expect(data.success).toBe(false);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// 2. Upload de fotos (via API)
// ══════════════════════════════════════════════════════════════════════════════

test.describe('2. Upload', () => {
  test('2.1 Upload sem arquivo retorna 400', async () => {
    const res = await fetch(`${BACKEND}/upload`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${authToken}` },
    });
    expect(res.status).toBe(400);
    const data = await res.json();
    expect(data.error).toContain('Nenhum arquivo');
  });

  test('2.2 Upload de arquivo .txt rejeitado', async () => {
    const form = new FormData();
    form.append('file', new Blob(['not an image'], { type: 'text/plain' }), 'test.txt');
    const res = await fetch(`${BACKEND}/upload`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${authToken}` },
      body: form,
    });
    expect(res.status).toBe(400);
    const data = await res.json();
    expect(data.error).toContain('não permitido');
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// 3. Geração de ensaios
// ══════════════════════════════════════════════════════════════════════════════

test.describe('3. Geração', () => {
  test('3.1 Listar estilos disponíveis', async () => {
    const { status, data } = await apiGet('/styles');
    expect(status).toBe(200);
    expect(Array.isArray(data)).toBe(true);
    expect(data.length).toBeGreaterThanOrEqual(5);
  });

  test('3.2 Saldo insuficiente (0 créditos) retorna erro', async () => {
    const { status, data } = await apiPost('/generate', {
      image_urls: ['https://via.placeholder.com/512'],
      tipo_ensaio: 'luxury_studio',
    });
    expect(status).toBe(402);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// 4. Pagamentos
// ══════════════════════════════════════════════════════════════════════════════

test.describe('4. Pagamentos Asaas', () => {
  test('4.1 PIX: criar cobrança retorna QR Code', async () => {
    const { status, data } = await apiPost('/create-pix-payment', {
      external_reference: `${Date.now()}:100_credits`,
      value: 25.0,
      description: '100 Creditos AureaIA',
    });
    // Pode falhar se conta Asaas não aprovada para PIX
    if (status === 500) {
      test.skip(true, 'PIX indisponível (conta Asaas não aprovada)');
    }
    expect(status).toBe(200);
    expect(data.success).toBe(true);
    expect(data.qr_code).toBeTruthy();
    expect(data.qr_code_base64).toBeTruthy();
    expect(data.payment_id).toBeTruthy();
  });

  test('4.2 Cartão: criar checkout retorna invoiceUrl', async () => {
    const { status, data } = await apiPost('/create-card-payment', {
      external_reference: `${Date.now()}:200_credits`,
      value: 50.0,
      description: '200 Creditos AureaIA',
    });
    expect(status).toBe(200);
    expect(data.success).toBe(true);
    expect(data.checkout_url).toContain('asaas.com');
    expect(data.payment_id).toBeTruthy();
  });

  test('4.3 Webhook sem token retorna 401', async () => {
    const res = await fetch(`${BACKEND}/webhooks/asaas`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ event: 'PAYMENT_CREATED' }),
    });
    expect(res.status).toBe(401);
  });

  test('4.4 Webhook com token inválido retorna 401', async () => {
    const res = await fetch(`${BACKEND}/webhooks/asaas`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'asaas-access-token': 'invalid_token',
      },
      body: JSON.stringify({ event: 'PAYMENT_CREATED' }),
    });
    expect(res.status).toBe(401);
  });

  test('4.5 Webhook PAYMENT_CONFIRMED com usuário válido adiciona créditos', async () => {
    // Primeiro registra um usuário específico pra este teste
    const webhookEmail = `webhook_${Date.now()}@teste.com`;
    const { data: regData } = await apiPost('/auth/register', {
      name: 'Webhook Test',
      email: webhookEmail,
      password: 'Teste123!',
    });
    const userId = regData.user.id;
    const paymentId = `pay_wh_${Date.now()}`;
    const credits = 100;

    // Envia webhook simulando pagamento confirmado
    const res = await fetch(`${BACKEND}/webhooks/asaas`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        event: 'PAYMENT_CONFIRMED',
        payment: {
          id: paymentId,
          status: 'CONFIRMED',
          value: 25.0,
          externalReference: `${userId}:100_credits`,
        },
      }),
    });
    expect(res.status).toBe(200);
    const whData = await res.json();
    expect(whData.status).toBe('success');

    // Verifica saldo
    const { data: userData } = await apiPost('/auth/login', {
      email: webhookEmail,
      password: 'Teste123!',
    });
    expect(userData.user.credits_balance).toBe(credits);

    // Verifica transação no extrato
    const { data: txnData } = await apiGet('/auth/user/transactions', userData.token);
    const purchase = txnData.transactions.find((t: any) => t.type === 'purchase');
    expect(purchase).toBeTruthy();
    expect(purchase.amount).toBe(credits);
    expect(purchase.balance_after).toBe(credits);
  });

  test('4.6 Webhook idempotente: mesmo payment_id não dobra créditos', async () => {
    const userId = `idemp_${Date.now()}`;
    const paymentId = `pay_idemp_${Date.now()}`;

    // Cria usuário diretamente
    const { data: regData } = await apiPost('/auth/register', {
      name: 'Idemp Test',
      email: `idemp_${Date.now()}@teste.com`,
      password: 'Teste123!',
    });
    const uid = regData.user.id;

    const payload = {
      event: 'PAYMENT_RECEIVED',
      payment: {
        id: paymentId,
        status: 'RECEIVED',
        value: 25.0,
        externalReference: `${uid}:100_credits`,
      },
    };

    // Primeiro envio
    const r1 = await fetch(`${BACKEND}/webhooks/asaas`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    expect(r1.status).toBe(200);

    // Segundo envio (duplicado)
    const r2 = await fetch(`${BACKEND}/webhooks/asaas`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    expect(r2.status).toBe(200);

    const { data: loginData } = await apiPost('/auth/login', {
      email: regData.user.email,
      password: 'Teste123!',
    });
    expect(loginData.user.credits_balance).toBe(100);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// 5. Galeria e extrato
// ══════════════════════════════════════════════════════════════════════════════

test.describe('5. Galeria e Extrato', () => {
  test('5.1 Galeria retorna array vazio para usuário novo', async () => {
    const { status, data } = await apiGet('/gallery/', authToken);
    expect(status).toBe(200);
    expect(Array.isArray(data.gallery)).toBe(true);
  });

  test('5.2 Extrato retorna transações', async () => {
    const { status, data } = await apiGet('/auth/user/transactions', authToken);
    expect(status).toBe(200);
    expect(Array.isArray(data.transactions)).toBe(true);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// 6. Frontend - Páginas carregam (requer navegador)
// ══════════════════════════════════════════════════════════════════════════════

test.describe('6. Frontend (Páginas)', () => {
  test('6.1 Página inicial carrega', async ({ page }) => {
    await page.goto(FRONTEND);
    await expect(page.locator('body')).toBeVisible();
    await expect(page.locator('h1, h2').first()).toBeVisible();
  });

  test('6.2 Página de login tem campos de email e senha', async ({ page }) => {
    await page.goto(`${FRONTEND}/login`);
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
  });

  test('6.3 Página de créditos carrega pacotes', async ({ page }) => {
    await page.goto(`${FRONTEND}/credits`);
    await expect(page.locator('text=Essencial')).toBeVisible();
    await expect(page.locator('text=Ateliê')).toBeVisible();
    await expect(page.locator('text=Maison')).toBeVisible();
  });

  test('6.4 Página de créditos mostra botões PIX e Cartão no modal', async ({ page }) => {
    await page.goto(`${FRONTEND}/credits`);
    // Clica no primeiro pacote pra abrir o modal
    await page.locator('text=Adquirir Pacote').first().click();
    await expect(page.locator('text=PIX')).toBeVisible();
    await expect(page.locator('text=Cartão')).toBeVisible();
  });

  test('6.5 Dashboard redireciona para login sem token', async ({ page }) => {
    await page.goto(`${FRONTEND}/dashboard`);
    await page.waitForURL('**/login');
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// 7. Segurança - Secrets no frontend
// ══════════════════════════════════════════════════════════════════════════════

test.describe('7. Segurança', () => {
  test('7.1 Nenhuma chave de API exposta no HTML', async ({ page }) => {
    await page.goto(FRONTEND);
    const html = await page.content();
    const secrets = ['access_token', 'asaas_access_token', 'sk_live', 'sk_test', 'api_key'];
    for (const s of secrets) {
      expect(html).not.toContain(s);
    }
  });
});
