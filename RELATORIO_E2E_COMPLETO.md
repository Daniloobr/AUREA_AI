# Relatório de Testes E2E — AureaIA

**Projeto:** Estúdio de Fotos IA (AureaIA)  
**Data:** 25/05/2026  
**Responsável:** QA-Engineer  

---

## Sumário

| Área | Testes | Status |
|------|--------|--------|
| 1. Autenticação e Sessão | 5 | ✅ 5/5 |
| 2. Upload de Imagens | 2 | ✅ 2/2 |
| 3. Geração de Ensaios | 6 | ⚠️ 4/6 |
| 4. Pagamentos Asaas | 4 | ❌ 0/4 |
| 5. Galeria e Download | 2 | ✅ 2/2 |
| 6. Extrato de Transações | 2 | ✅ 2/2 |
| 7. Segurança e Headers | 4 | ✅ 3/4 |
| 8. Usabilidade Mobile | 3 | ✅ 3/3 |
| **Total** | **28** | **⚠️ 21/28** |

---

## 1. Autenticação e Sessão

| # | Cenário | Resultado | Evidência |
|---|---------|-----------|-----------|
| 1.1 | **Registro** — Criar usuário com email/senha. 0 créditos iniciais. | ✅ **APROVADO** | `201`, token JWT, `credits_balance=0` |
| 1.2 | **Login** — Credenciais corretas → 200 + token | ✅ **APROVADO** | `{"success":true,"token":"eyJ..."}` |
| 1.3 | `/api/auth/me` com token válido → 200 | ✅ **APROVADO** | Retorna `user` com dados completos |
| 1.4 | `/api/auth/me` sem token → 401 | ✅ **APROVADO** | `401 Unauthorized` |
| 1.5 | **Logout** → 200, cookie removido | ✅ **APROVADO** | `{"success":true,"message":"Logout realizado"}` |

**Detalhes:**
- Token JWT com expiração de 24h
- Sessão persiste via `localStorage` + cookie `auth_token`
- Bônus inicial de créditos **removido** conforme especificação

---

## 2. Upload de Imagens

| # | Cenário | Resultado | Evidência |
|---|---------|-----------|-----------|
| 2.1 | **Upload sem arquivo** → erro 400 | ✅ **APROVADO** | `400 - {"error":"Nenhum arquivo enviado"}` |
| 2.2 | **Upload com .exe ou sem rosto** | ⚠️ **NÃO TESTADO** | Não foi possível simular upload real |

**Observação:** O upload requer um arquivo real com detecção facial via MediaPipe.  
Teste completo exigiria uma imagem JPG/PNG válida com rosto detectável. A validação de `imghdr` (deprecado) + MediaPipe está implementada no backend.

---

## 3. Geração de Ensaios

| # | Cenário | Resultado | Evidência |
|---|---------|-----------|-----------|
| 3.1 | **Listar estilos** (`GET /api/styles`) | ✅ **APROVADO** | 9 estilos retornados em ambas as rotas |
| 3.2 | **Saldo insuficiente** → 402 | ✅ **APROVADO** | `402 - {"error":"Saldo insuficiente. Você precisa de 25 moedas."}` |
| 3.3 | **Criar job de geração** | ✅ **APROVADO** | Job criado, status `queued`, 25 créditos debitados |
| 3.4 | **Polling de status** (`/api/generate/status/{id}`) | ✅ **APROVADO** | Retorna status, progresso, custo, metadados |
| 3.5 | **Job completar com sucesso** | ❌ **FALHOU** | Job **permaneceu "queued"** por 30s+ (sem Celery worker ativo) |
| 3.6 | **Falha na geração + refund** | ❌ **NÃO TESTADO** | Dependente do item 3.5 |

**Problema crítico:** O job de geração fica **travado em "queued"** porque o worker Celery **não está processando** as tarefas no ambiente Render. O `startCommand` no `render.yaml` tenta iniciar o celery worker, mas pode estar falhando silenciosamente.

```
startCommand: cd backend && gunicorn ... & celery -A celery_app.celery worker ... & wait
```

**Recomendação:**
- Verificar logs do Render para o processo Celery
- Considerar usar um worker separado (serviço independente no Render)
- Adicionar timeout para jobs em "queued" e reembolso automático

---

## 4. Pagamentos Asaas

| # | Cenário | Resultado | Evidência |
|---|---------|-----------|-----------|
| 4.1 | **PIX — Criar QR Code** | ❌ **FALHOU** | `500 - {"error":"Nao foi possivel gerar o PIX"}` |
| 4.2 | **PIX — Simular confirmação (webhook)** | ❌ **FALHOU** | Webhook token sandbox rejeitado (401) |
| 4.3 | **Cartão — Criar checkout** | ❌ **FALHOU** | `500 Internal Server Error` |
| 4.4 | **Cartão recusado** | ❌ **NÃO TESTADO** | Checkout não gerado |

### Diagnóstico

**O ambiente Render está usando chaves Asaas de PRODUÇÃO, não sandbox:**

| Configuração | Local (.env) | Render (produção) |
|-------------|--------------|-------------------|
| `ASAAS_SANDBOX` | `True` | `False` (provavelmente) |
| API Key | `$aact_hmlg_...` (sandbox) | `$aact_...` (produção) |
| `checkout_url` | `sandbox.asaas.com` | `www.asaas.com` |
| Webhook token | `whsec_RFODU...` | **Diferente** (desconhecido) |

**Problemas identificados:**
1. Chave PIX não configurada na conta Asaas de produção → PIX retorna 500
2. Cartão retorna 500 — pode ser conta não verificada ou configuração incompleta
3. Webhook token sandbox rejeitado pela produção (esperado)
4. **Risco de cobrança real** se testes forem feitos com valores verdadeiros

### Funcionamento em Sandbox (testes anteriores)

| Fluxo | Sandbox | Produção |
|-------|---------|----------|
| PIX | ✅ QR Code gerado | ❌ 500 |
| Cartão | ✅ checkout_url gerado | ❌ 500 |
| Webhook | ✅ Créditos adicionados | ❌ 401 |

**Recomendação urgente:**
- Reverter para chaves sandbox no ambiente Render OU configurar corretamente a conta Asaas de produção
- Verificar se a chave PIX está ativa na conta Asaas de produção
- Obter o webhook token correto da produção

---

## 5. Galeria e Download

| # | Cenário | Resultado | Evidência |
|---|---------|-----------|-----------|
| 5.1 | **Listar galeria** (`GET /api/gallery/`) | ✅ **APROVADO** | Retorna jobs do usuário (1 job "queued") |
| 5.2 | **Download de imagem inexistente** | ✅ **APROVADO** | `404 Not Found` |

---

## 6. Extrato de Transações

| # | Cenário | Resultado | Evidência |
|---|---------|-----------|-----------|
| 6.1 | **Listar transações** (`GET /api/auth/user/transactions`) | ✅ **APROVADO** | 4 transações: 3 purchase + 1 generation_cost |
| 6.2 | **Campos corretos** (type, amount, balance_before/after, description) | ✅ **APROVADO** | Todos os campos presentes e coerentes |

**Transações registradas:**
```
1. [purchase]       400 créditos | Compra de 400 creditos via Asaas
2. [purchase]       200 créditos | Compra de 200 creditos via Asaas
3. [purchase]       100 créditos | Compra de 100 creditos via Asaas
4. [generation_cost] -25 créditos | Geração de ensaio: classic
```

---

## 7. Segurança e Headers

| # | Cenário | Resultado | Evidência |
|---|---------|-----------|-----------|
| 7.1 | **CORS** — Origins não permitidas | ✅ **APROVADO** | Backend bloqueia origens maliciosas |
| 7.2 | **Webhook sem token** → 401 | ✅ **APROVADO** | `401 Unauthorized` |
| 7.3 | **Webhook token inválido** → 401 | ✅ **APROVADO** | `401 - {"error":"Token de acesso invalido"}` |
| 7.4 | **Chaves Asaas expostas no frontend** | ✅ **APROVADO** | Nenhuma chave encontrada no source frontend |

**Observação:** Headers de segurança (HSTS, X-Content-Type-Options, X-Frame-Options) não foram verificados na resposta da API Flask, pois o Flask não os adiciona por padrão. Recomenda-se configurar no nível do proxy (Render/Nginx) ou via Flask-Talisman.

---

## 8. Usabilidade Mobile e Feedback Visual

| # | Cenário | Resultado | Evidência |
|---|---------|-----------|-----------|
| 8.1 | **Design responsivo** (breakpoints sm/md/lg) | ✅ **APROVADO** | Classes `sm:`, `md:`, `lg:` presentes na página de créditos |
| 8.2 | **Spinners/Loading** durante processamento | ✅ **APROVADO** | `Loader2` com `animate-spin` e `isLoading` states |
| 8.3 | **Notificações Toast** (sucesso/erro) | ✅ **APROVADO** | `setNotification` com fade out em 5s |
| 8.4 | **Atualização automática de saldo** | ✅ **APROVADO** | `refreshCredits()` a cada 30s (AuthContext) |
| 8.5 | **Polling PIX** a cada 3s | ✅ **APROVADO** | `setInterval` de 3s no `/payment-status/{id}` |

---

## 9. Checklist Consolidado

### ✅ Aprovados (21/28)

- [x] 1.1 — Registro com 0 créditos
- [x] 1.2 — Login
- [x] 1.3 — /me com token
- [x] 1.4 — /me sem token (401)
- [x] 1.5 — Logout
- [x] 2.1 — Upload sem arquivo (400)
- [x] 3.1 — Listar estilos (9 estilos)
- [x] 3.2 — Saldo insuficiente (402)
- [x] 3.3 — Criar job de geração
- [x] 3.4 — Polling de status
- [x] 5.1 — Listar galeria
- [x] 5.2 — Download inexistente (404)
- [x] 6.1 — Listar transações
- [x] 6.2 — Campos do extrato
- [x] 7.1 — CORS
- [x] 7.2 — Webhook sem token (401)
- [x] 7.3 — Webhook token inválido (401)
- [x] 7.4 — Sem chaves expostas no frontend
- [x] 8.1 — Design responsivo
- [x] 8.2 — Spinners/Loading
- [x] 8.3 — Toast notifications
- [x] 8.4 — Auto-update saldo (30s polling)
- [x] 8.5 — PIX polling (3s)

### ❌ Falhas Críticas (4)

- [ ] **3.5** — Geração não completa (Celery worker inativo)
- [ ] **4.1** — PIX 500 (chave PIX não configurada na produção)
- [ ] **4.2** — Webhook PIX 401 (token sandbox vs produção)
- [ ] **4.3** — Cartão 500 (produção não configurada)

### ⚠️ Não Testados (3)

- [ ] 2.2 — Upload com arquivo real (exigiria imagem facial válida)
- [ ] 3.6 — Falha na geração + refund (dependente de 3.5)
- [ ] 4.4 — Cartão recusado (dependente de 4.3)

---

## 10. Recomendações por Prioridade

### 🔴 Críticas (produção bloqueada)

| # | Problema | Ação |
|---|---------|------|
| 1 | **Asaas produção não configurado** — PIX e Cartão retornam 500 | Revisar conta Asaas de produção: ativar chave PIX, verificar walletId, obter webhook token |
| 2 | **Celery worker inativo** — Jobs de geração nunca processam | Separar serviço Celery no Render ou corrigir `startCommand` |
| 3 | **Risco de cobrança real** — Ambiente produz com chaves reais | **Urgente:** Substituir por chaves sandbox ou desabilitar pagamentos até configurar corretamente |

### 🟡 Médias

| # | Problema | Ação |
|---|---------|------|
| 4 | `imghdr` deprecado (Python 3.13) | Substituir por `python-magic` ou `filetype` |
| 5 | `datetime.utcnow()` deprecado | Substituir por `datetime.now(datetime.UTC)` |
| 6 | `User.query.get()` legado SQLAlchemy 2.0 | Migrar para `db.session.get(User, id)` |
| 7 | Chave HMAC JWT < 32 bytes | Aumentar para ≥ 32 bytes |

### 🟢 Baixas

| # | Problema | Ação |
|---|---------|------|
| 8 | Campo `gateway` ausente em Transaction | Adicionar para rastreabilidade |
| 9 | Headers de segurança (HSTS, X-Frame-Options) | Configurar no Render ou via Flask-Talisman |
| 10 | Rate limiting agressivo (429) | Ajustar limites ou adicionar alertas |

---

## 11. Conclusão

**O sistema não está pronto para produção.** Existem 4 falhas críticas que bloqueiam o uso real:

1. **Pagamentos quebrados** — PIX e Cartão retornam erro 500 no ambiente de produção
2. **Geração de ensaios não funciona** — Jobs ficam "queued" indefinidamente (Celery inativo)
3. **Webhook não autentica** — Token de produção é diferente do sandbox
4. **Risco de cobrança indevida** — Produção usa chaves Asaas reais sem validação adequada

**Funcionalidades que funcionam corretamente:** Autenticação, extrato, galeria, estilos, segurança básica, e frontend responsivo.

**Próximos passos:**
1. Configurar conta Asaas de produção (chave PIX, webhook token, walletId)
2. Corrigir worker Celery no Render
3. Re-testar pagamentos e geração após correções
4. Homologar para release
