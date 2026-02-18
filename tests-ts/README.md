# tests-ts (основні тести)

E2E-тести на **TypeScript** (Playwright). Тут пишуться та запускаються всі нові тест-кейси.

## Встановлення

```bash
cd tests-ts
npm install
npx playwright install
```

У **корені** репозиторію має бути файл **`.env`** (скопіюйте з `.env.example`): `TEST_USER_EMAIL`, `TEST_USER_PASSWORD`, `TEST_BASE_URL` / `TEST_LOGIN_URL` тощо. Playwright підвантажує `.env` з кореня.

## Запуск

```bash
npm run test
npm run test:headed
npm run test:ui
npx playwright test e2e/login.spec.ts
npx playwright test e2e/login.spec.ts -g "успішний логін"
```

## Звіти (Allure)

- Результати пишуться в **`../reports/allure-results/`**.
- Згенерувати HTML-звіт: **`npm run allure:generate`** → `../reports/allure-report/`.
- Відкрити: **`npm run allure:open`** → http://localhost:9753/index.html (перегляд тільки через сервер).
- Історія (останні 3 прогони на сьют): **`npm run allure:rotate -- login`** (або `xml-feed`, `excel-mapping`).

Детально: [../docs/REPORTS_AND_ARTIFACTS.md](../docs/REPORTS_AND_ARTIFACTS.md), [../docs/TEST_REPORTS.md](../docs/TEST_REPORTS.md).

## Документація

Повний перелік документів (POM, чеклист, секрети, структура проєкту): [../docs/README.md](../docs/README.md).
