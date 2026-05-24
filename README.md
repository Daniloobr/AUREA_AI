<div align="center">
  <h1>AureaIA</h1>
  <p><strong>Inteligência artificial para ensaios fotográficos de gestantes – transforme momentos em arte.</strong></p>
</div>

---

## Sobre

AureaIA é uma plataforma SaaS que usa inteligência artificial para transformar fotos de gestantes em ensaios premium. O usuário faz upload de 3 fotos de referência, escolhe um estilo e recebe imagens geradas por IA com alta qualidade e identidade preservada.

**Para quem é:** Estúdios fotográficos, fotógrafos autônomos e gestantes que desejam ensaios criativos sem depender de sessões presenciais.

**Benefícios:**
- Geração em 4 estilos premium (Estúdio Luxo, Pôr do Sol, Preto & Branco, Boho Chic)
- Preservação de identidade facial
- Créditos flexíveis (pagamento por uso via Stripe)
- Pronto em segundos, não em dias

---

## Stack Tecnológica

| Componente     | Tecnologia                              |
|----------------|----------------------------------------|
| Frontend       | Next.js 16 + React 19 + Tailwind CSS 4 |
| Backend        | Flask 3.0 (Python 3.12)               |
| Banco de Dados | PostgreSQL (Supabase)                  |
| ORM            | SQLAlchemy 2.0                         |
| Pagamentos     | Stripe                                 |
| Fila           | Celery + Redis                         |
| IA             | API de IA proprietária                |
| Auth           | JWT (backend) / Clerk (frontend)       |
| Deploy         | Render (backend) + Vercel (frontend)   |

---

## Variáveis de Ambiente

Crie um arquivo `.env` na raiz do diretório `backend/` com as seguintes variáveis:

```env
# Flask
FLASK_ENV=development
SECRET_KEY=sua_chave_secreta_aqui
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:4000

# Banco de Dados (Supabase PostgreSQL)
DATABASE_URL=postgresql://usuario:senha@host:porta/postgres
DIRECT_URL=postgresql://usuario:senha@host:porta/postgres

# Supabase (Storage + Auth)
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_anon_key
SUPABASE_SERVICE_ROLE_KEY=sua_service_role_key

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_ALLOWED_PRICES=price_id1,price_id2,price_id3
STRIPE_SUCCESS_URL=https://seu-site.com/credits?success=true
STRIPE_CANCEL_URL=https://seu-site.com/credits?canceled=true

# IA
AI_PROVIDER_API_TOKEN=seu_token_aqui
AI_MODEL_ID=openai/gpt-image-2

# Email (SendGrid)
SENDGRID_API_KEY=
EMAIL_FROM=contato@seudominio.com
```

---

## Setup Local

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
cp .env.example .env      # Configurar variáveis
python app.py
```

### Worker (Fila)

```bash
cd backend
celery -A celery_app.celery worker --loglevel=info --pool=solo
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Produção

- **Site:** [aureaia.com](https://aureaia-saas.vercel.app)
- **Backend:** Render (Gunicorn + Celery)
- **Frontend:** Vercel

---

## Licença

Proprietária. Todos os direitos reservados.
