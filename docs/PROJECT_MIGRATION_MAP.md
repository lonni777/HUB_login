# Зіставлення проєкту: Python → TypeScript

Повна таблиця папок і файлів: що переписано, що поєднано, де що лежить. Щоб нічого не пропустити.

---

## 1. Де записуються репорти

Формат репортів **tests-ts** зроблено таким же, як у Python: timestamp-звіт + bug report при падінні.

| Джерело | Що | Де записується |
|--------|-----|-----------------|
| **tests-ts** (Playwright) | HTML-звіт (з timestamp) | `reports/report_YYYYMMDD_HHMMSS/index.html` — кожен прогон у своїй папці |
| **tests-ts** | Bug report при падінні тесту | `reports/last_failure_bug_report.txt` (той самий формат, що й у Python — для Jira) |
| **tests-ts** | Скріншоти при падінні, trace, video (при retry) | `test-results/` (підпапки по тестах) |
| **tests-ts** | Excel-файли з тестів мапінгу | `test-results/excel_mappings/` (при запуску з tests-ts) |
| **tests-ts** | Allure (сирі результати) | `reports/allure-results/` — після прогону; далі `npm run allure:generate` → `reports/allure-report/` |
| **tests-Python** (pytest) | HTML-звіт з timestamp | `reports/report_YYYYMMDD_HHMMSS.html` |
| **tests-Python** | Bug report при падінні | `reports/last_failure_bug_report.txt` |
| **tests-Python** | Скріншоти при падінні | `test-results/screenshots/` |

**Як відкрити HTML-звіт Playwright (TS):**
```bash
cd tests-ts
npx playwright test
# Останній звіт: reports/report_YYYYMMDD_HHMMSS/index.html (відкрити в браузері)
npx playwright show-report ../reports/report_YYYYMMDD_HHMMSS
```
При падінні тесту: відкрити `reports/last_failure_bug_report.txt` — можна копіювати в Jira.

---

## 2. Кореневі папки та файли (HUB_login)

| Що | Python (tests-Python) | TypeScript (tests-ts) | Примітка |
|----|------------------------|------------------------|----------|
| Конфіг/секрети | — | — | **Спільний** `.env` і `.env.example` у корені; обидва підпроєкти читають з кореня |
| Документація | — | — | **Спільна** папка `docs/` |
| Репорти | пише в `reports/` | пише в `reports/playwright/` | **Спільна** папка `reports/` у корені |
| Артефакти прогону | `test-results/screenshots/` | `test-results/` (підпапки) | **Спільна** папка `test-results/` у корені (playwright.config виносить outputDir у корінь) |
| README | — | — | **Кореневий** `README.md` оновлено: два підпроєкти, як запускати |

---

## 3. Тести (кейси)

| Модуль Python | Файл Python | Файл TypeScript | Статус |
|---------------|-------------|-----------------|--------|
| Логін | `tests-Python/tests/test_login.py` | `tests-ts/e2e/login.spec.ts` | ✅ Переписано (11 тестів) |
| XML-фіди | `tests-Python/tests/test_xml_feed.py` | `tests-ts/e2e/xml-feed.spec.ts` | ✅ Переписано (11 тестів) |
| Excel мапінг | `tests-Python/tests/test_excel_mapping.py` | `tests-ts/e2e/excel-mapping.spec.ts` | ✅ Переписано (2 тести) |

**Разом:** 24 тести в Python → 24 тести в TS (1:1).

---

## 4. Сторінки (Page Object)

| Призначення | Python | TypeScript | Статус |
|-------------|--------|------------|--------|
| Базова сторінка | `tests-Python/pages/base_page.py` | `tests-ts/pages/BasePage.ts` | ✅ Переписано |
| Логін | `tests-Python/pages/login_page.py` | `tests-ts/pages/LoginPage.ts` | ✅ Переписано |
| XML-фіди (+ Excel мапінг у TS) | `tests-Python/pages/xml_feed_page.py` | `tests-ts/pages/XmlFeedPage.ts` | ✅ Переписано, Excel-методи в тому ж класі |

---

## 5. Локатори

| Призначення | Python | TypeScript | Статус |
|-------------|--------|------------|--------|
| Логін | `tests-Python/locators/login_locators.py` | `tests-ts/locators/login.locators.ts` | ✅ Переписано |
| XML-фіди | `tests-Python/locators/xml_feed_locators.py` | `tests-ts/locators/xml-feed.locators.ts` | ✅ Переписано |

---

## 6. Конфіг та фікстури

| Призначення | Python | TypeScript | Статус |
|-------------|--------|------------|--------|
| Конфіг (URL, логин, XML, БД, .env) | `tests-Python/config/settings.py` (клас TestConfig) | `tests-ts/fixtures/env.ts` (testConfig) | ✅ Поєднано: один об’єкт конфігу з .env |
| Фікстури / перед-після тестів | `tests-Python/conftest.py` (pytest fixtures, hooks, репорти) | У кожному `*.spec.ts`: `beforeEach` (логін), без окремого conftest | ✅ Логіка перенесена в spec-файли та playwright.config |

---

## 7. Утиліти

| Призначення | Python | TypeScript | Статус |
|-------------|--------|------------|--------|
| БД (cleanup: delete/deactivate фід) | `tests-Python/utils/db_helper.py` | `tests-ts/utils/db-helper.ts` | ✅ Переписано (pg, SSL) |
| Валідація Excel (аркуші, структура) | `tests-Python/utils/excel_validator.py` | У `excel-mapping.spec.ts` використовується бібліотека `xlsx` напряму | ✅ Поєднано: логіка в spec, без окремого utils-файлу |

---

## 8. Запуск та конфіг проєкту

| Призначення | Python | TypeScript | Статус |
|-------------|--------|------------|--------|
| Конфіг запуску тестів | `tests-Python/pytest.ini` | `tests-ts/playwright.config.ts` | ✅ Різні інструменти; обидва читають .env з кореня |
| Залежності | `tests-Python/requirements.txt` | `tests-ts/package.json` | ✅ Окремо |
| Приклад env | У корені `.env.example` (спільний) | той самий | — |
| README підпроєкту | `tests-Python/README.md` | `tests-ts/README.md` | ✅ Окремо для кожного |

---

## 9. Що лишилось тільки в Python (legacy)

| Файл/папка | Призначення |
|------------|-------------|
| `tests-Python/conftest.py` | Хуки pytest, генерація report_*.html, last_failure_bug_report.txt, скріншоти при падінні |
| `tests-Python/pytest.ini` | addopts, html-звіти |
| `tests-Python/.pytest_cache/` | Кеш pytest |
| Всі файли в `tests-Python/` | Legacy: нові кейси не додаються, при потребі тільки виправлення поломок |

---

## 10. Що є тільки в TypeScript

| Файл/папка | Призначення |
|------------|-------------|
| `tests-ts/fixtures/env.ts` | Єдиний модуль конфігу (немає окремої папки config/) |
| `tests-ts/tsconfig.json` | Збірка TypeScript |
| `tests-ts/e2e/*.spec.ts` | Усі тест-кейси; логін у beforeEach |
| Репорти Playwright | `reports/playwright/` (HTML), `test-results/` (скріншоти, trace, video) |

---

## Підсумок

- **Переписано:** усі тести (3 модулі), усі pages, усі locators, db-helper, конфіг (як fixtures/env).
- **Поєднано:** конфіг у один `env.ts`; Excel-валідація без окремого utils у TS; репорти обидвох у спільній папці `reports/` (різні підпапки/файли).
- **Спільне:** кореневий `.env` / `.env.example`, `docs/`, `reports/`, `test-results/`, кореневий `README.md`.
- **Тільки Python:** conftest (hooks, репорти pytest), pytest.ini, .pytest_cache.
- **Тільки TS:** fixtures/env.ts, tsconfig, playwright.config, репорти в `reports/playwright/`.

Репорти **TypeScript** пишуться в **`reports/playwright/`** (HTML) та **`test-results/`** (артефакти). Перегляд: `npx playwright show-report` з папки `tests-ts` або відкрити `reports/playwright/index.html`.
