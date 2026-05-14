# 🚀 Guia de Configuração de Produção - AureaIA

Este guia detalha as etapas necessárias para configurar e validar as variáveis de ambiente e a infraestrutura de armazenamento no Render e Supabase.

## 1. Variáveis de Ambiente (Secrets)

As seguintes chaves **devem** ser configuradas no painel do **Render** (Environment > Environment Variables):

| Variável | Descrição | Onde Obter |
| :--- | :--- | :--- |
| `SENDGRID_API_KEY` | Envio de e-mails de boas-vindas e recuperação. | Painel SendGrid (API Keys) |
| `REPLICATE_API_TOKEN` | Geração de imagens via IA. | [replicate.com/account](https://replicate.com/account) |
| `SUPABASE_URL` | URL do projeto Supabase. | Project Settings > API |
| `SUPABASE_SERVICE_ROLE_KEY` | Chave secreta para bypass de RLS (Backend). | Project Settings > API > service_role |
| `DATABASE_URL` | URL de conexão PostgreSQL. | Project Settings > Database > Connection String |
| `SECRET_KEY` | Chave para assinatura de tokens JWT. | Gere um UUID ou string aleatória longa. |

> [!IMPORTANT]
> **Nunca** exponha o `SUPABASE_SERVICE_ROLE_KEY` ou o `REPLICATE_API_TOKEN` no frontend ou em repositórios públicos.

## 2. Configuração do Supabase Storage

O backend agora está configurado para usar o Supabase Storage. Certifique-se de que os seguintes buckets existam:

1.  **`inputs`**: Para fotos de referência e crops faciais.
2.  **`outputs`**: Para as imagens geradas pela IA.

### Permissões (RLS)
Para que as imagens sejam visíveis no frontend, os buckets devem ser marcados como **Public** no Supabase Storage.

*   **Bucket `inputs`**: Público (para que o Replicate possa acessar a URL).
*   **Bucket `outputs`**: Público (para visualização na galeria).

## 3. Migração de Dados Locais

Se você possui imagens salvas localmente no servidor Render (que são perdidas a cada deploy), execute o script de migração:

```bash
cd backend
python migrate_to_supabase.py
```

## 4. Validação de Saúde (Health Check)

Após configurar as variáveis, você pode verificar se o serviço de e-mail e Supabase estão inicializados corretamente verificando os logs do Render:
- `Supabase Client initialized successfully.`
- `SendGrid Service Initialized.` (Caso a chave esteja presente)

---
*Documento gerado automaticamente pela Antigravity AI.*
