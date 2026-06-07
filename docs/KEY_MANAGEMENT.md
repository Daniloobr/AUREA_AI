# Gerenciamento de Chaves — AureaIA

## Chaves em Uso

| Serviço         | Variável de Ambiente         | Onde é Usada                          | Como Gerar                                                     |
|-----------------|-----------------------------|---------------------------------------|----------------------------------------------------------------|
| Replicate       | `REPLICATE_API_TOKEN`       | `services/ai_generator.py`            | https://replicate.com/account/api-tokens                       |
| Replicate       | `AI_PROVIDER_API_TOKEN`     | `services/ai_generator.py`            | Mesmo token do Replicate                                        |
| Supabase        | `SUPABASE_URL`              | `services/supabase_service.py`        | Dashboard do Supabase → Settings → API                         |
| Supabase        | `SUPABASE_KEY` (anon)       | `services/supabase_service.py`        | Dashboard do Supabase → Settings → API → anon public           |
| Supabase        | `SUPABASE_SERVICE_ROLE_KEY` | `services/supabase_service.py`        | Dashboard do Supabase → Settings → API → service_role          |
| Flask           | `SECRET_KEY`                | `app.py`, `utils/auth_utils.py`       | `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| Flask Admin     | `ADMIN_SECRET_KEY`          | `routes/auth.py` (rota /admin/credits)| Gere string aleatória forte                                     |
| Brevo           | `BREVO_API_KEY`             | `services/email_service.py`           | https://app.brevo.com/settings/api                             |
| Asaas           | `ASAAS_API_KEY`             | `services/asaas_service.py`           | Dashboard Asaas → Integrações                                   |
| Asaas Webhook   | `ASAAS_WEBHOOK_TOKEN`       | `routes/webhooks.py`                  | Gere token aleatório                                            |
| PostgreSQL      | `DATABASE_URL`              | `config.py`, SQLAlchemy               | Supabase → Settings → Database → Connection String             |

## Instruções para Rotação

1. **Replicate**: Acesse https://replicate.com/account/api-tokens → gere novo token → atualize no Render → revogue o antigo.
2. **Supabase**: Acesse Dashboard → Settings → API → clique "Reset anon key" e "Reset service_role key".
3. **SECRET_KEY**: Execute `python -c "import secrets; print(secrets.token_urlsafe(32))"` e atualize no Render.
4. **Brevo**: Acesse https://app.brevo.com/settings/api → create a new API key → atualize no Render.
5. **Asaas**: Acesse Integrações → gere nova chave → atualize no Render.

## Ambiente

- **Backend (Render)**: Variáveis em Dashboard → Environment Variables
- **Frontend (Vercel)**: Variáveis em Project Settings → Environment Variables
- **Local**: Arquivo `backend/.env` (NUNCA commitar)

**⚠️ Atenção**: Após rotacionar qualquer chave, teste imediatamente o fluxo completo.
