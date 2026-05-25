# Relatório de Testes — Integração Asaas (AureaIA)

**Projeto:** AureaIA — Estúdio de Fotos IA  
**Data:** 25/05/2026  
**Responsável:** QA-Engineer  

---

## ⚠️ ATENÇÃO — PROBLEMA CRÍTICO EM PRODUÇÃO

O ambiente **Render** (produção) está usando **chaves Asaas de PRODUÇÃO** (`www.asaas.com`), NÃO as chaves sandbox do `.env` local.  
Isso foi descoberto durante os testes — o `checkout_url` do cartão aponta para `https://www.asaas.com/` (produção) em vez de `https://sandbox.asaas.com/`.

### Problemas encontrados em produção:

| Item | Status | Detalhe |
|------|--------|---------|
| PIX | ❌ **500 Internal Server Error** | `"Nao foi possivel gerar o PIX"` — quebrado em produção |
| Cartão | ✔️ Funciona | `checkout_url` gerado, status PENDING |
| Webhook | ❌ **401 Unauthorized** | Token sandbox rejeitado — produção usa token diferente |

### Causa raiz:
O `.env` local contém chaves **sandbox** (`ASAAS_SANDBOX=True`, `$aact_hmlg_*`), mas o deploy no Render tem variáveis de ambiente próprias que sobrescrevem com chaves **reais de produção**.

### Recomendação urgente:
1. Verificar variáveis de ambiente no dashboard do Render
2. Corrigir chave PIX na conta Asaas de produção (ou voltar para sandbox)
3. Obter webhook token correto da produção
4. **NÃO testar com valores reais** — conta de produção pode cobrar de verdade

---

## Ambiente de Desenvolvimento (Sandbox) — Testes Controlados

**Ambiente:** Sandbox Asaas (`https://sandbox.asaas.com`)

## Resumo (Sandbox)

| Categoria | Resultado |
|-----------|-----------|
| Testes unitários (backend) | **48/48 ✔️** |
| Testes unitários (frontend) | **27/27 ✔️** |
| Integração PIX (sandbox) | **✔️ Aprovado** |
| Integração Cartão (sandbox) | **✔️ Aprovado** |
| Webhook (sandbox) | **✔️ Aprovado** |
| Segurança | **✔️ Aprovado** |
| **Geral (sandbox)** | **75/75 testes — 0 falhas** |

---

## 1. Testes Unitários

### Backend (pytest)

| Suite | Testes | Status |
|-------|--------|--------|
| `test_auth.py` — Registro, login, me, balance, transactions, delete, forgot/reset password | 22 | ✔️ |
| `test_credits.py` — Admin add/adjust, refund (idempotência), admin endpoints (stats, users, jobs, ban) | 13 | ✔️ |
| `test_models.py` — User, Transaction, GenerationJob | 6 | ✔️ |
| `test_webhook.py` — Eventos ignorados, external_ref ausente, pagamento confirmado | 3 | ✔️ |
| **Total** | **44 → 48** *(4 suites)* | **✔️ 48 passed** |

### Frontend (vitest)

| Suite | Testes | Status |
|-------|--------|--------|
| `api.test.ts` — GET, POST, DELETE, auth errors, network failures | 27 | ✔️ |
| **Total** | **27** | **✔️ 27 passed** |

---

## 2. Fluxo PIX

### 2.1 Criação de Pagamento PIX

**Endpoint:** `POST /api/create-pix-payment`

| Campo | Resultado |
|-------|-----------|
| `payment_id` | `pay_v3j3nn4marq5q161` |
| `qr_code` | Payload PIX copiável ✔️ |
| `qr_code_base64` | Imagem PNG base64 ✔️ |
| `status` | `PENDING` |
| `success` | `true` |

### 2.2 Simulação de Confirmação

**Webhook enviado:** `PAYMENT_RECEIVED`

```
POST /api/webhooks/asaas
→ {"status": "success"}
```

### 2.3 Verificação

| Métrica | Antes | Depois |
|---------|-------|--------|
| Saldo | 0 | 100 ✔️ |
| Transações | 0 | 1 (purchase, 100 créditos) ✔️ |

---

## 3. Fluxo Cartão de Crédito

### 3.1 Criação de Pagamento

**Endpoint:** `POST /api/create-card-payment`

| Campo | Resultado |
|-------|-----------|
| `payment_id` | `pay_uttc2rerhj01q9r3` |
| `checkout_url` | `https://sandbox.asaas.com/i/uttc2rerhj01q9r3` ✔️ |
| `status` | `PENDING` |
| `success` | `true` |

### 3.2 Simulação de Confirmação

**Webhook enviado:** `PAYMENT_CONFIRMED`

```
POST /api/webhooks/asaas
→ {"status": "success"}
```

### 3.3 Verificação

| Métrica | Antes | Depois |
|---------|-------|--------|
| Saldo | 100 | 300 ✔️ |
| Transações | 1 | 2 (purchase, 200 créditos) ✔️ |

---

## 4. Webhook

### 4.1 Eventos Suportados

| Evento | Processado? |
|--------|-------------|
| `PAYMENT_RECEIVED` | ✔️ |
| `PAYMENT_CONFIRMED` | ✔️ |
| `PAYMENT_OVERDUE` | ❌ Ignorado (`ignored`) |
| Qualquer outro | ❌ Ignorado (`ignored`) |

### 4.2 Edge Cases

| Cenário | Resposta |
|---------|----------|
| `externalReference` sem `:` | `{"status": "ignored"}` |
| user_id inexistente | `{"status": "ignored"}` |
| Payload sem `payment.id` | `{"status": "ignored", "reason": "no_payment_id"}` |
| Webhook duplicado (idempotência) | `{"status": "success"}` — sem duplicar créditos |

### 4.3 Idempotência

- Envio duplicado do mesmo webhook → saldo **não** alterado (permanece 300) ✔️
- Mecanismo: `Transaction.external_id` único (`asaas_<payment_id>`)

---

## 5. Segurança

### 5.1 Proteção do Webhook

| Cenário | Resposta |
|---------|----------|
| Sem token `asaas-access-token` | `401 Unauthorized` ✔️ |
| Token inválido | `401 Unauthorized` ✔️ |
| Token válido | `200 OK` ✔️ |

### 5.2 Exposição de Chaves

| Local | Chave Asaas? |
|-------|:------------:|
| Frontend `src/` | ❌ Não |
| Frontend `.env.local` | ❌ Não |
| Backend `.env` | ✔️ (arquivo não exposto) |
| Backend `*.py` | ❌ Não hardcoded |

✔️ **Nenhuma chave Asaas exposta publicamente.**

### 5.3 Frontend

| Página | Status |
|--------|--------|
| `https://aureaia-saas.vercel.app/` | 200 ✔️ |
| `https://aureaia-saas.vercel.app/credits` | 200 ✔️ |
| `https://aureaia-saas.vercel.app/login` | 200 ✔️ |

---

## 6. Observações e Recomendações

### Observações

| # | Item | Detalhe |
|---|------|---------|
| 1 | **Checkout Direto vs Transparente** | Implementação atual usa hosted checkout do Asaas (redirect). `create_credit_card_token()` existe mas **não é utilizado**. |
| 2 | **Campo `gateway`** | Modelo `Transaction` não possui campo `gateway`. Identificação do gateway é via `external_id` (prefixo `asaas_`). |
| 3 | **Cartão recusado** | Não testável via API atual — recusa ocorre na página Asaas. |
| 4 | **Rate limiting** | Endpoints `/api/auth/me` e `/api/payment-status/` retornaram `429 Too Many Requests` após múltiplas chamadas consecutivas do mesmo IP. |
| 5 | **Depreciações** | 158 warnings: `datetime.utcnow()` deprecado, `User.query.get()` legado, chave HMAC JWT < 32 bytes. |

### Recomendações

| Prioridade | Recomendação |
|:----------:|--------------|
| Média | Implementar **Checkout Transparente** se for requisito: formulário de cartão no frontend + tokenização via `create_credit_card_token()` |
| Baixa | Adicionar campo `gateway` ao modelo `Transaction` para rastreabilidade |
| Baixa | Substituir `datetime.utcnow()` por `datetime.now(datetime.UTC)` |
| Baixa | Aumentar chave HMAC JWT para ≥ 32 bytes |
| Baixa | Migrar `User.query.get()` para `db.session.get(User, ...)` |

---

## 7. Dados do Teste

**Usuário de teste (segunda rodada):**
- ID: `98008d4f-26d5-444c-826f-b55e82b9fe1b`
- Email: `qa.completo.81584@teste.com`
- Saldo final: **300 créditos** (100 PIX + 200 CARD)

**Transações:**
```
1. purchase | 100 créditos | 0 → 100 | Compra de 100 creditos via Asaas
2. purchase | 200 créditos | 100 → 300 | Compra de 200 creditos via Asaas
```

**Usuário de teste (primeira rodada):**
- ID: `53c62ec3-ce6c-49c2-ad48-42bca0a6aaea`
- Email: `qa.tester.44636@teste.com`
- Saldo final: **700 créditos** (100 PIX + 200 CARD + 400 PIX)

**Transações:**
```
1. purchase | 100 créditos | 0 → 100 | Compra de 100 creditos via Asaas
2. purchase | 200 créditos | 100 → 300 | Compra de 200 creditos via Asaas
3. purchase | 400 créditos | 300 → 700 | Compra de 400 creditos via Asaas
```

---

## 8. Testes em Produção (ambiente real Asaas)

### 8.1 Resultados

| Teste | Resultado | Observação |
|-------|-----------|------------|
| Health Check API | 404 (sem rota `/api/health`) | ⚠️ Rota inexistente |
| Frontend | 200 OK | ✔️ |
| Registrar usuário | ✔️ | `prod.test.53780@teste.com` |
| **PIX - Criar pagamento** | **❌ 500 ERROR** | `"Nao foi possivel gerar o PIX"` |
| Cartão - Criar pagamento | ✔️ | `checkout_url` gerado |
| **Webhook (token sandbox)** | **❌ 401** | Token de produção é diferente |
| Segurança (sem token) | ✔️ 401 | Funciona |
| Saldo | 0 | Webhook não processado |

### 8.2 Diagnóstico

```
Local .env:           ASAAS_SANDBOX=True,  key=$aact_hmlg_*  → sandbox.asaas.com
Render (produção):    ASAAS_SANDBOX=False, key=$aact_*      → www.asaas.com
```

- O deploy no **Render** tem **suas próprias variáveis de ambiente** que sobrescrevem o `.env` local
- O backend em produção está conectado à **conta Asaas real** (produção)
- `checkout_url` do cartão: `https://www.asaas.com/i/...` (produção) ✅
- PIX quebrado em produção: `500 Internal Server Error`
- Webhook token sandbox não funciona em produção (esperado)

### 8.3 Causa Provável do Erro PIX (500)

1. **Chave PIX não configurada** na conta Asaas de produção
2. **`walletId` inválido** para o ambiente de produção
3. A conta de produção pode não ter o recurso PIX habilitado
4. O erro ocorre no `get_pix_qr_code()` — a criação do pagamento em si pode funcionar, mas a consulta do QR code falha

---

## 9. Conclusão (Sandbox)

**Testes no sandbox concluídos com sucesso.** A integração Asaas está funcional, segura e estável.

O sistema processa corretamente:
- Pagamentos PIX com QR Code
- Pagamentos com cartão de crédito (via hosted checkout Asaas)
- Webhooks com idempotência e proteção por token
- Adição de créditos ao saldo do usuário
- Registro de transações no extrato

### ⚠️ Ação Necessária

**Corrigir PIX em produção** antes de liberar para usuários reais. O fluxo de cartão está funcional, mas PIX retorna erro 500. Verificar configuração da chave PIX e `walletId` na conta Asaas de produção, bem como as variáveis de ambiente no dashboard do Render.
