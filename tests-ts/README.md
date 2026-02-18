# tests-ts (основні тести)

E2E-тести на **TypeScript** (Playwright). Тут пишуться та запускаються всі нові тест-кейси.

## Встановлення

З каталогу репозиторію:

```bash
cd tests-ts
npm install
npx playwright install
```

У корені репозиторію має бути файл **`.env`** (або скопіюйте з `.env.example`) з змінними для тестів: `TEST_USER_EMAIL`, `TEST_USER_PASSWORD`, `TEST_BASE_URL` / `TEST_LOGIN_URL` тощо. Конфіг Playwright підвантажує `.env` з кореня (`HUB_login/.env`).

## Запуск

```bash
# З каталогу tests-ts
npm run test

# З відкритим браузером
npm run test:headed

# UI mode
npm run test:ui

# Один файл
npx playwright test e2e/login.spec.ts

# Один тест
npx playwright test e2e/login.spec.ts -g "успішний логін"
```

## Звіти

- **Playwright HTML:** папки `../reports/report_YYYYMMDD_HHMMSS/` (з timestamp). Відкрити: `npm run report` або вручну `index.html` з останньої папки.
- **Allure:** після прогону результати в `../reports/allure-results/`. Щоб згенерувати HTML-звіт, потрібен [Allure CLI](https://allurereport.org/docs/v2/install-for-nodejs/) (Java 8+), далі з папки `tests-ts`:
  ```bash
  npm run allure:generate   # → ../reports/allure-report/
  npm run allure:serve      # згенерувати і відкрити в браузері
  ```
- **Bug report при падінні:** `../reports/last_failure_bug_report.txt` (формат для Jira).
