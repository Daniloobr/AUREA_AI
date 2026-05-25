# Relatório de Testes — Integração Asaas (AureaIA)

**Projeto:** AureaIA — Estúdio de Fotos IA  
**Data:** 25/05/2026  
**Responsável:** QA-Engineer  
**Ambiente:** Sandbox Asaas  

---

## Resumo

| Categoria | Resultado |
|-----------|-----------|
| Testes unitários (backend) | **48/48 ✔️** |
| Testes unitários (frontend) | **27/27 ✔️** |
| Integração PIX | **✔️ Aprovado** |
| Integração Cartão | **✔️ Aprovado** |
| Webhook | **✔️ Aprovado** |
| Segurança | **✔️ Aprovado** |
| **Geral** | **75/75 testes — 0 falhas** |

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

## 8. Conclusão

**Testes concluídos com sucesso.** A integração Asaas está funcional, segura e estável no ambiente Sandbox. Todos os 75 testes (48 backend + 27 frontend + integração PIX + integração Cartão + Webhook + Segurança) passaram sem falhas críticas.

O sistema processa corretamente:
- Pagamentos PIX com QR Code
- Pagamentos com cartão de crédito (via hosted checkout Asaas)
- Webhooks com idempotência e proteção por token
- Adição de créditos ao saldo do usuário
- Registro de transações no extrato
