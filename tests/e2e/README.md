# QA E2E Tests — AureaIA

## Setup

```bash
cd tests/e2e
npm init -y
npm install -D @playwright/test
npx playwright install chromium
```

## Run

```bash
# All tests (API + frontend)
npx playwright test

# Only API tests (automated, no browser needed beyond login page)
npx playwright test --grep "^(?![6.])"

# Only frontend page tests
npx playwright test --grep "^6\\."

# Run a single test file
npx playwright test aureaia-qa.spec.ts --grep "4.2"

# UI mode (interactive)
npx playwright test --ui
```

## What it tests

| Section | Coverage | Automated? |
|---|---|---|
| 1. Autenticação | register, login, /me, invalid login | ✅ API |
| 2. Upload | file validation, extension rejection | ✅ API |
| 3. Geração | styles list, insufficient balance | ✅ API |
| 4. Pagamentos | PIX create, card create, webhook, idempotency | ✅ API (partial) |
| 5. Galeria/Extrato | empty gallery, transactions list | ✅ API |
| 6. Frontend | page loads, button visibility, redirects | ✅ Browser |
| 7. Segurança | secret exposure in HTML | ✅ Browser |

## Manual steps needed

- **PIX simulation**: after `4.1` passes, log into Asaas Sandbox and confirm payment
- **Card payment**: after `4.2` passes, follow the `checkout_url` in a browser and complete the card form
- **Mobile/responsive**: open DevTools and test at 375px width
