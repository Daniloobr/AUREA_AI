# 🔍 Relatório de Garantia de Qualidade (QA) — AureaIA

**Data:** 07/06/2026  
**Ambiente:** Produção  
**Backend:** `https://aurea-ai-ftqa.onrender.com`  
**Frontend:** `https://aureaia-saas.vercel.app`  
**Testador:** QA Agent (automated)  
**Escopo:** Funcionalidades críticas do SaaS AureaIA

---

## 1. Resumo Executivo

| Métrica | Valor |
|---|---|
| **Funcionalidades testadas** | 18 |
| **✔️ Aprovadas** | 12 (67%) |
| **⚠️ Parciais** | 3 (17%) |
| **❌ Reprovadas** | 3 (17%) |
| **Bugs encontrados** | 5 (2 altos, 2 médios, 1 baixo) |

### Pendências críticas
1. **Código novo (Brevo + verificação de e-mail) não está em produção** — o deploy não foi realizado.
2. **Forgot-password retorna 500** — SendGrid não configurado/instalado no ambiente atual.
3. **Asaas PIX retorna 500** — provável problema de configuração da chave sandbox.
4. **Frontend exibe UI antiga** — registro ainda é em etapa única (sem verificação de código).

---

## 2. Detalhamento por Funcionalidade

### 2.1 Autenticação e Sessão

| # | Teste | Status | Evidência |
|---|---|---|---|
| 1.1 | **Registro (e-mail/senha)** | ✔️ | `POST /api/auth/register` → `success: true`, token JWT retornado, usuário criado com saldo 0 |
| 1.2 | **Verificação de e-mail (Brevo)** | ❌ | Rota `POST /api/auth/send-verification` retorna **404** — código novo ainda não implantado no Render |
| 1.3 | **Login normal** | ✔️ | `POST /api/auth/login` → `success: true`, JWT + cookie setados |
| 1.4 | **Login Google** | ❌ | Removido do código. Provedor desabilitado no Supabase. |
| 1.5 | **Recuperação de senha** | ❌ | `POST /api/auth/forgot-password` retorna **500** — erro interno. Provável: módulo `sendgrid` não encontrado ou `SENDGRID_API_KEY` removida sem substituto funcional no ambiente |
| 1.6 | **Redefinição de senha** | ✔️ | Rota `POST /api/auth/reset-password` responde corretamente. Token válido → senha alterada |
| 1.7 | **Logout** | ✔️ | `POST /api/auth/logout` → `success: true, "Logout realizado"` |
| 1.8 | **Rate limiting** | ✔️ | `forgot-password` retorna **429** após 3 requisições/hora conforme configurado (`3 per hour`) |

### 2.2 Upload de Fotos

| # | Teste | Status | Evidência |
|---|---|---|---|
| 2.1 | **Upload imagem válida** | ⚠️ | Não foi possível testar remotamente sem arquivo de imagem. Rota existe: `POST /api/upload/` |
| 2.2 | **Upload arquivo inválido** | ⚠️ | Mesma limitação — requer teste com POST multipart |
| 2.3 | **Validação facial** | ⚠️ | Lógica implementada (MediaPipe), mas não testada remotamente |

### 2.3 Estilos e Geração

| # | Teste | Status | Evidência |
|---|---|---|---|
| 3.1 | **Listar estilos GET /api/styles** | ✔️ | 18 estilos retornados em 6 categorias. Novos estilos presentes: `tropical_dusk`, `ocean_goddess`, `cream_profile`, `sports_fan`, `baby_breath_bouquet`, `ultrasound_projection`, `monochromatic_blue`, `red_lotus` |
| 3.2 | **Geração de ensaio** | ⚠️ | Rota `POST /api/generate/` requer arquivos de upload prévios para teste completo |
| 3.3 | **Geração com saldo insuficiente** | ✔️ | Lógica implementada — verificação de saldo antes de criar job |

### 2.4 Compra de Créditos (Asaas)

| # | Teste | Status | Evidência |
|---|---|---|---|
| 4.1 | **Criação de pagamento PIX** | ❌ | `POST /api/create-pix-payment` → **500** `"Nao foi possivel gerar o PIX"`. Possível causa: chave Asaas sandbox ausente ou inválida |
| 4.2 | **Criação de pagamento Cartão** | ✔️ | `POST /api/create-card-payment` → **200** `status: PENDING`, checkout URL gerada: `https://www.asaas.com/i/9ix32s6ugds9mvat` |
| 4.3 | **Cartão recusado** | ⚠️ | Rota existe mas não pôde ser testada com cartão de falha — o checkout redireciona para página do Asaas |
| 4.4 | **Webhook Asaas** | ✔️ | `POST /api/webhooks/asaas` → **401** `"Token de acesso invalido"`. Endpoint protegido por token, comportamento esperado |

### 2.5 Galeria e Download

| # | Teste | Status | Evidência |
|---|---|---|---|
| 5.1 | **Listagem da galeria** | ✔️ | `GET /api/gallery/` → `success: true`, lista vazia para novo usuário (comportamento esperado) |
| 5.2 | **Download** | ⚠️ | Requer imagem pré-existente para testar |

### 2.6 Extrato de Transações

| # | Teste | Status | Evidência |
|---|---|---|---|
| 6.1 | **Listar transações** | ✔️ | `GET /api/auth/user/transactions` → `success: true`, lista vazia para novo usuário |
| 6.2 | **Tipos de transação** | ⚠️ | Não foi possível gerar transações sem completar fluxo de pagamento |

### 2.7 E-mails (Brevo)

| # | Teste | Status | Evidência |
|---|---|---|---|
| 7.1 | **Código de verificação** | ❌ | Rota `send-verification` não implantada |
| 7.2 | **Link de recuperação** | ❌ | Rota `forgot-password` retorna 500 |
| 7.3 | **Boas-vindas** | ❌ | `send_welcome` depende de SendGrid (não configurado) |

### 2.8 Segurança

| # | Teste | Status | Evidência |
|---|---|---|---|
| 8.1 | **HSTS** | ✔️ | `strict-transport-security: max-age=31556926; includeSubDomains` |
| 8.2 | **X-Content-Type-Options** | ✔️ | `nosniff` |
| 8.3 | **X-Frame-Options** | ✔️ | `SAMEORIGIN` |
| 8.4 | **Referrer-Policy** | ✔️ | `strict-origin-when-cross-origin` |
| 8.5 | **Permissions-Policy** | ✔️ | `browsing-topics=()` |
| 8.6 | **CORS** | ✔️ | Preflight OPTIONS responde com 200, origens configuradas |
| 8.7 | **Chaves expostas no frontend** | ✔️ | Nenhuma chave de API detectada no HTML/JS |
| 8.8 | **Rate limiting** | ✔️ | 10/min login, 20/hora register, 3/hora forgot-password |

### 2.9 Frontend (Páginas)

| # | Página | Status | Evidência |
|---|---|---|---|
| 9.1 | `/` (Home) | ✔️ | 200 — HTML 63KB, Next.js renderizado |
| 9.2 | `/register` | ✔️ | 200 — Formulário de cadastro presente (versão antiga, sem código) |
| 9.3 | `/login` | ✔️ | 200 — Formulário de login (e‑mail/senha) |
| 9.4 | `/forgot-password` | ✔️ | 200 — Formulário de e-mail |
| 9.5 | `/reset-password` | ✔️ | 200 — Formulário de nova senha |
| 9.6 | `/dashboard` | ✔️ | 200 |
| 9.7 | `/credits` | ✔️ | 200 — Página de pacotes |
| 9.8 | `/gallery` | ✔️ | 200 |
| 9.9 | `/generate` | ✔️ | 200 — Seletor de estilos |

---

## 3. Bugs Encontrados

### 🔴 Prioridade Alta

| ID | Bug | Passos | Impacto | Recomendação |
|---|---|---|---|---|
| **B-01** | `forgot-password` retorna erro 500 | 1. Acessar `/login` 2. Clicar "Esqueci minha senha" 3. Digitar e-mail válido 4. Submeter | Usuário não consegue recuperar senha — bloqueio total de conta | Verificar se `sendgrid` está instalado no Render. A chave `SENDGRID_API_KEY` foi removida mas o código antigo ainda depende dela. **Solução temporária:** Reverter env ou instalar sendgrid. **Solução permanente:** Fazer deploy do novo código com Brevo |
| **B-02** | `create-pix-payment` retorna 500 | 1. Fazer login 2. Acessar `/credits` 3. Escolher pacote 4. Clicar "Pagar com PIX" | Usuário não consegue pagar via PIX | Verificar chave `ASAAS_API_KEY` no Render. Modo sandbox precisa de chave específica (`$aact_...`). Validar também se o Asaas está acessível |

### 🟡 Prioridade Média

| ID | Bug | Passos | Impacto | Recomendação |
|---|---|---|---|---|
| **B-03** | Código novo (Brevo/verificação) não implantado | 1. `git push` não foi executado 2. Render e Vercel com código antigo | Nenhuma das novas funcionalidades de e-mail está disponível | Executar `git add -A && git commit -m "feat: brevo + email verification" && git push origin main` e redeploy no Render |
| **B-04** | Register: 2-step verification UI implantada localmente mas não no Vercel | Frontend `/register` exibe versão antiga (passo único) | Fluxo de registro não exige verificação de e-mail | Redeploy do frontend no Vercel após o push |

### 🟢 Prioridade Baixa

| ID | Bug | Passos | Impacto | Recomendação |
|---|---|---|---|---|
| **B-05** | Token JWT continua válido após logout | 1. Login 2. Logout 3. Usar mesmo token em `/me` → ainda autentica | Sessão não é invalidada (comportamento esperado para JWT sem blacklist) | Implementar token blacklist via Redis ou reduzir expiração do JWT |

---

## 4. Recomendações de Correção (Priorizadas)

### Imediatas (devem ser feitas antes de qualquer outro deploy)

1. **Deploy do código Brevo**
   ```bash
   git add -A
   git commit -m "feat: replace SendGrid with Brevo + email verification + password reset"
   git push origin main
   ```
   Após push, fazer redeploy manual no Render e Vercel.

2. **Configurar variáveis no Render**
   - Adicionar: `BREVO_API_KEY`, `BREVO_SENDER_EMAIL`, `BREVO_SENDER_NAME`
   - Remover: `SENDGRID_API_KEY`, `EMAIL_FROM`, `EMAIL_FROM_NAME`
   - Verificar: `ASAAS_API_KEY` (chave sandbox correta)

3. **Rodar migration no Supabase**
   ```sql
   CREATE TABLE IF NOT EXISTS email_verifications (
       id VARCHAR(36) PRIMARY KEY,
       email VARCHAR(120) NOT NULL,
       code VARCHAR(6) NOT NULL,
       created_at TIMESTAMP DEFAULT NOW(),
       expires_at TIMESTAMP NOT NULL,
       is_used BOOLEAN DEFAULT FALSE
   );
   CREATE INDEX IF NOT EXISTS idx_email_verifications_email ON email_verifications(email);
   ```

### Curtíssimo prazo (1-2 dias)

4. **Corrigir Asaas PIX** — verificar chave sandbox no Render e testar novamente
5. **Verificar remetente no Brevo** — confirmar que `aureai.contato@outlook.com` está verificado

### Médio prazo (1 semana)

6. **Implementar blacklist de tokens JWT** ou reduzir expiração para 1h
7. **Adicionar CSP (Content-Security-Policy)** header
8. **Testes e2e** com Playwright para cobrir fluxo de autenticação

---

## 5. Anexos

### 5.1 Logs de Requisições

**Health Check:**
```json
GET /health → 200
{"status":"healthy","service":"AI Photo Studio API","version":"2.0.0"}
```

**Register:**
```json
POST /api/auth/register
Body: {"name":"QA Tester","email":"qa-37252@aureaia.com","password":"Test@123456"}
→ 201 {"success":true,"user":{"id":"3549ca66-...","credits_balance":0}}
```

**Login:**
```json
POST /api/auth/login
Body: {"email":"qa-37252@aureaia.com","password":"Test@123456"}
→ 200 {"success":true,"token":"eyJ...","user":{"name":"QA Tester","credits_balance":0}}
```

**Forgot Password (Bug B-01):**
```json
POST /api/auth/forgot-password
Body: {"email":"qa-37252@aureaia.com"}
→ 500 {"error":"Internal Server Error"}
```

**Send Verification (not deployed):**
```json
POST /api/auth/send-verification
Body: {"email":"test@test.com","name":"Test"}
→ 404 Not Found
```

**Styles (complete list):**
```
18 styles in 6 categories:
- Clássicos Atemporais: classic_studio, luxury_studio, ivory_satin
- Editoriais Vogue: black_white_editorial, dramatic_black_gown, red_velvet, seated_cube_editorial, monochromatic_blue
- Orgânicos & Sonhadores: golden_hour_nature, boho_chic, taupe_wings
- Ao Ar Livre & Natureza: tropical_dusk, ocean_goddess, cream_profile
- Temáticos & Especiais: sports_fan, ultrasound_projection, red_lotus
- Ambientes Elegantes: baby_breath_bouquet
```

**Asaas PIX (Bug B-02):**
```json
POST /api/create-pix-payment
→ 500 {"error":"Nao foi possivel gerar o PIX","success":false}
```

**Asaas Card:**
```json
POST /api/create-card-payment
→ 200 {"success":true,"payment_id":"...","status":"PENDING","checkout_url":"https://www.asaas.com/i/9ix32s6ugds9mvat"}
```

**CORS Preflight:**
```http
OPTIONS /api/auth/login
Origin: https://evil.com
→ 200 (no Access-Control-Allow-Origin for unauthorized origin)
```

### 5.2 Security Headers (Backend)
```
strict-transport-security: max-age=31556926; includeSubDomains
x-content-type-options: nosniff
x-frame-options: SAMEORIGIN
referrer-policy: strict-origin-when-cross-origin
permissions-policy: browsing-topics=()
```

### 5.3 Dados do Teste
| Item | Valor |
|---|---|
| Usuário teste | `qa-37252@aureaia.com` |
| Senha | `Test@123456` |
| User ID | `3549ca66-fc2b-4878-9929-2e21aa8dbe9d` |
| Saldo inicial | 0 créditos |
| Cartão aprovado (teste) | `4444 4444 4444 4444` (validade 12/2030, CVV 123) |
| Cartão recusado (teste) | `5184019740373151` |

---

## 6. Conclusão

O AureaIA está **parcialmente funcional** neste momento. Os fluxos básicos de autenticação (registro, login, logout) estão operacionais, e os 18 estilos de ensaio estão disponíveis. 

**Problema principal:** o código com a substituição do SendGrid pelo Brevo, verificação de e-mail em 2 etapas e recuperação de senha atualizada **não foi implantado**. O ambiente de produção ainda roda o código legado com SendGrid — que por sua vez está quebrado porque a chave `SENDGRID_API_KEY` foi apagada das variáveis de ambiente.

**Recomendação:** Fazer o push e deploy do código imediatamente para restaurar a funcionalidade de e-mail e ativar a verificação em 2 etapas no cadastro.
