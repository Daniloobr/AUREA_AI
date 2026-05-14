# 💎 AureaIA: Product Requirements Document (PRD) Definitivo

| Metadado | Valor |
| :--- | :--- |
| **Projeto** | AureaIA |
| **Versão** | 1.0.0 |
| **Status** | **CONGELADO** |
| **Data de Aprovação** | 14 de Maio de 2026 |
| **Responsável** | Product Manager (Antigravity AI) |

## 1. Changelog
| Versão | Data | Autor | Descrição das Alterações |
| :--- | :--- | :--- | :--- |
| 1.0.0 | 14/05/2026 | PM Agent | Emissão inicial do PDR blindado (Base MVP). |

---

## 2. Resumo Executivo e Proposta de Valor
O **AureaIA** é uma plataforma SaaS de fotografia generativa focada no nicho de gestantes e casais. Utiliza inteligência artificial de ponta para transformar fotos caseiras em ensaios fotográficos de luxo.

*   **Missão:** Eliminar as barreiras físicas, financeiras e logísticas de um ensaio fotográfico de gestante tradicional.
*   **Público-Alvo:** Gestantes (primário) e casais (secundário).
*   **Diferencial Competitivo:**
    *   **Velocidade:** Resultados em segundos, não semanas.
    *   **Custo:** ~95% mais barato que um ensaio físico.
    *   **Praticidade:** Processo 100% mobile via upload de fotos.
    *   **Tecnologia:** Uso de InstantID para garantir que a IA mantenha a identidade real da gestante.

---

## 3. Escopo Funcional (Versão 1.0.0)

### 3.1 Autenticação e Gestão de Acesso
*   **Descrição:** Sistema de login baseado em JWT.
*   **Comportamento:**
    *   Expiração do token: 24 horas fixas.
    *   Armazenamento: Cookies `Secure` e `HttpOnly`.
*   **Critério de Aceitação:** O usuário não deve conseguir acessar rotas de `/generate` sem um token válido no cookie.

### 3.2 Sistema de Créditos (Economia Interna)
*   **Bônus Inicial:** Exatamente **25 moedas** creditadas no registro bem-sucedido.
*   **Custo por Geração:** **25 moedas** por cada foto gerada.
*   **Débito Atômico:** O débito deve ocorrer *antes* da chamada à API de IA em uma transação SQL. Se a chamada falhar, o sistema deve registrar o erro, mas o débito é a garantia de reserva de recurso.

### 3.3 Geração de Imagens (AI Engine)
*   **Engine:** Replicate API.
*   **Modelos:** FLUX.1 (base) + InstantID (preservação facial).
*   **Estilos Disponíveis (v1.0.0):**
    1.  `luxury_studio`: Fundo neutro, iluminação de estúdio profissional.
    2.  `golden_hour_nature`: Campo aberto com luz solar de fim de tarde.
    3.  `boho_chic`: Decoração rústica, flores secas, tons pastéis.
    4.  `black_white_editorial`: Alto contraste, estilo revista de moda.
*   **Fluxo:**
    1.  Usuário faz upload de 1 foto de referência facial clara.
    2.  Usuário seleciona 1 estilo.
    3.  Sistema valida saldo (Saldo >= 25).
    4.  Sistema debita 25 moedas.
    5.  Chamada assíncrona ao Replicate.
    6.  Polling ou Webhook para atualizar status.
*   **Critério de Aceitação:** A imagem deve ser entregue e exibida no dashboard em até 45 segundos sob condições normais de API.

### 3.4 Segurança e LGPD
*   **Exclusão de Conta:** Anonimização lógica. O campo `email` no banco deve ser substituído por `deleted_user_{uuid}@aureaia.com` e o `password_hash` limpo.
*   **Rate Limiting:** Máximo de 5 tentativas de login por minuto por IP; 2 solicitações de geração por minuto por usuário.
*   **Security Headers:** Uso obrigatório de `Flask-Talisman` para forçar HTTPS e prevenir XSS/Clickjacking.

---

## 4. Escopo Não Funcional

*   **Stack Técnica:**
    *   Backend: Flask (Python 3.10+).
    *   Frontend: Next.js (React 18+).
    *   Banco de Dados: Supabase (PostgreSQL).
    *   Infraestrutura: Render (App) + Supabase (DB).
*   **Performance:** Endpoints de API (exceto geração) devem responder em < 500ms.
*   **Disponibilidade:** 99.0% de uptime mensal.
*   **Armazenamento:** Local (temporário) evoluindo para Cloudflare R2 (preparado).

---

## 5. Roadmap Congelado

| Versão | Feature | Prazo Estimado | Justificativa de Negócio |
| :--- | :--- | :--- | :--- |
| **1.1.0** | Integração Stripe/Asaas | 30 dias | Início da monetização e pacotes de créditos. |
| **1.2.0** | Otimização de Prompts | 60 dias | Melhoria da qualidade visual baseada no feedback de "artificialidade". |
| **1.3.0** | Download Pro Hub | 90 dias | Permitir download em 4K, PNG e compartilhamento social. |
| **2.0.0** | App Nativo (iOS/Android) | Q4 | Aumentar retenção e facilitar upload de fotos. |

---

## 6. Processo Formal de Mudança (FCR)

Qualquer alteração neste documento deve seguir o fluxo:
1.  **Abertura do FCR:** Documentar o pedido com:
    *   ID da Mudança: `FCR-YYYYMMDD-XX`
    *   Impacto: (Backend/Frontend/DB/Preço)
    *   Esforço: (Horas estimadas)
2.  **Análise de Impacto:** O PM valida se a mudança quebra a "Promessa de Luxo" ou a segurança.
3.  **Aprovação:** Somente após aprovação, a versão do PDR é incrementada (ex: 1.0.0 -> 1.1.0).
4.  **Implementação:** Nenhuma linha de código deve ser escrita para a nova feature antes do PDR atualizado ser commitado.

---

## 7. Dicionário de Dados (Modelos SQL)

```sql
-- Tabela de Usuários
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    balance INTEGER DEFAULT 25, -- Bônus inicial fixo
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de Transações (Livro Razão)
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    type VARCHAR(50) NOT NULL, -- 'bonus', 'generation', 'purchase', 'admin_adjustment'
    amount INTEGER NOT NULL, -- Negativo para débito, Positivo para crédito
    balance_before INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de Gerações
CREATE TABLE generation_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    style_id VARCHAR(50) NOT NULL,
    prompt_used TEXT,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    replicate_id TEXT,
    result_url TEXT, -- URL final da imagem
    error_log TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 8. Especificações de API

### 8.1 Autenticação
*   `POST /api/auth/login`
    *   **Payload:** `{ "email": "...", "password": "..." }`
    *   **Resposta (200):** Cookie Set com JWT.
    *   **Resposta (401):** `{ "error": "Credenciais inválidas" }`

### 8.2 Geração
*   `POST /api/generate` (Auth Obrigatória)
    *   **Payload:** `{ "style": "luxury_studio", "image_base64": "..." }`
    *   **Fluxo de Erro (402):** Se `user.balance < 25`, retornar `{ "error": "Saldo insuficiente" }`.
    *   **Resposta (202):** `{ "job_id": "...", "message": "Geração iniciada" }`

### 8.3 Administração
*   `POST /api/admin/credits`
    *   **Header:** `X-Admin-Key: [CHAVE_ENV]`
    *   **Payload:** `{ "user_id": "...", "amount": 100 }`
    *   **Ação:** Incrementa o saldo e registra transação do tipo `admin_adjustment`.

---

## 9. Matriz de Responsabilidades

| Papel | Responsabilidade | Permissão PDR |
| :--- | :--- | :--- |
| **Backend Architect** | Garantir atomicidade e segurança de dados. | Leitura/Sugestão de FCR. |
| **Frontend Dev** | Implementar UI premium e estados de loading. | Leitura/Sugestão de FCR. |
| **Reality Checker** | Validar se a entrega condiz com o PDR. | **Veto de Deploy.** |
| **Stakeholder (Humano)** | Definir estratégia e preços. | Aprovação de FCR. |

---

## 10. Apêndice: Fluxos Críticos

### 10.1 Fluxo de Saldo Insuficiente
1. Usuário clica em "Gerar".
2. Frontend verifica `user.balance` via API ou estado global.
3. Se < 25, o botão "Gerar" é desabilitado e um banner de "Comprar Créditos" é exibido.
4. Caso o usuário tente burlar via API, o backend retorna `HTTP 402 Payment Required`.

### 10.2 Fluxo de Exclusão (LGPD)
1. Usuário solicita exclusão em `/settings`.
2. Sistema confirma password.
3. SQL: `UPDATE users SET email = 'deleted_' || id, password_hash = '********', is_active = false WHERE id = ...`
4. Logout imediato e limpeza de cookies.

---

**FIM DO DOCUMENTO**
