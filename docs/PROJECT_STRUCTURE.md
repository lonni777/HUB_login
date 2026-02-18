# Структура проєкту (TypeScript — основний стек)

Проєкт автотестів HUB: логін, XML-фіди, Excel-мапінг. **Основний набір тестів** — **tests-ts** (TypeScript, Playwright). tests-Python — legacy, нові кейси не додаються.

---

## Кореневі папки та спільне

| Що | Де | Примітка |
|----|-----|----------|
| Секрети/конфіг | `.env`, `.env.example` у **корені** | Обидва підпроєкти читають з кореня |
| Документація | `docs/` | Орієнтована на TypeScript; Python — legacy |
| Репорти | `reports/` | Allure (tests-ts): `allure-results/`, `allure-report/`, `history/<suite>/` |
| Артефакти прогону | `test-results/` | Скріншоти, trace, відео (при падінні/retry) |

---

## tests-ts (TypeScript) — основний набір

### Структура

| Призначення | Шлях |
|-------------|------|
| Тести | `e2e/login.spec.ts`, `e2e/xml-feed.spec.ts`, `e2e/excel-mapping.spec.ts` |
| Page Objects | `pages/BasePage.ts`, `pages/LoginPage.ts`, `pages/XmlFeedPage.ts` |
| Локатори | `locators/login.locators.ts`, `locators/xml-feed.locators.ts` |
| Конфіг | `fixtures/env.ts` (testConfig з .env) |
| Фікстури | `fixtures/feed-cleanup.ts` (cleanup для xml-feed) |
| Утиліти | `utils/db-helper.ts` (cleanup по БД) |
| Конфіг запуску | `playwright.config.ts` |

### Репорти (tests-ts)

| Що | Де |
|----|-----|
| Allure (сирі дані) | `reports/allure-results/` |
| Allure (HTML-звіт) | `reports/allure-report/` (після `npm run allure:generate`) |
| Історія по сьютах (останні 3) | `reports/history/<suite>/run_<timestamp>/` після `allure:rotate -- <suite>` |
| Скріншоти, trace, відео | `test-results/` |

### Запуск

```bash
cd tests-ts
npm install
npx playwright install
npm run test
npm run allure:generate
npm run allure:open
```

Детально: [tests-ts/README.md](../tests-ts/README.md), [REPORTS_AND_ARTIFACTS.md](REPORTS_AND_ARTIFACTS.md).

---

## Зіставлення тестів і сторінок

| Модуль | Спеки | Page Object | Локатори |
|--------|-------|-------------|----------|
| Логін | `e2e/login.spec.ts` | `LoginPage` | `login.locators.ts` |
| XML-фіди | `e2e/xml-feed.spec.ts` | `XmlFeedPage` | `xml-feed.locators.ts` |
| Excel мапінг | `e2e/excel-mapping.spec.ts` | `XmlFeedPage` (ті самі екрани) | `xml-feed.locators.ts` |

Усього 24 тести в tests-ts (11 login + 11 xml-feed + 2 excel-mapping).

---

## tests-Python (legacy)

Існуючі тести на pytest + Playwright. Нові кейси пишуться лише в tests-ts.

| Що | Де |
|----|-----|
| Тести | `tests-Python/tests/` |
| Pages, locators, config, utils | `tests-Python/pages/`, `locators/`, `config/`, `utils/` |
| Фікстури, репорти | `tests-Python/conftest.py`, `pytest.ini` |
| Документація Python | `tests-Python/docs/` (чеклист, план міграції, продуктивність тощо) |

Запуск: `cd tests-Python && pytest`. Детально: [tests-Python/README.md](../tests-Python/README.md).
