# Звіти про виконання тестів (tests-ts, TypeScript)

Основний набір тестів — **tests-ts** (TypeScript, Playwright). Звіти формуються через **Allure Report**.

---

## tests-ts: Allure Report

### Після прогону

1. **Запустити тести** (з каталогу tests-ts):
   ```bash
   cd tests-ts
   npm run test
   ```
   Результати пишуться в **`reports/allure-results/`** (сирі дані).

2. **Згенерувати HTML-звіт:**
   ```bash
   npm run allure:generate
   ```
   Звіт створюється в **`reports/allure-report/`**.

3. **Відкрити звіт:**
   ```bash
   npm run allure:open
   ```
   У браузері відкриється **http://localhost:9753/index.html** (перегляд тільки через сервер, не file://).

### Історія (останні 3 прогони на сьют)

Після прогону конкретного сьюту можна зберегти звіт у історію:

```bash
cd tests-ts
npm run test -- e2e/login.spec.ts
npm run allure:generate
npm run allure:rotate -- login
```

Параметр: `login`, `xml-feed` або `excel-mapping`. Скрипт зберігає поточний звіт у `reports/history/<suite>/run_<timestamp>/` і залишає лише останні 3 прогони для цього сьюту.

Детально: [REPORTS_AND_ARTIFACTS.md](REPORTS_AND_ARTIFACTS.md).

---

## Артефакти при падінні

- **Скріншоти** — зберігаються лише при падінні тесту (`test-results/`).
- **Trace і відео** — при першому retry (налаштування в `playwright.config.ts`).

Папка `test-results/` в `.gitignore`, у репо не комітиться.

---

## Структура та запуск

Де що лежить і як запускати: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md). Індекс усієї документації: [README.md](README.md).

---

## tests-Python (legacy)

Python-тести в **tests-Python** при запуску генерують власні звіти (pytest-html, bug report). Деталі: [tests-Python/README.md](../tests-Python/README.md), [tests-Python/docs/](../tests-Python/docs/). Основний робочий набір і звіти — **tests-ts** (Allure).
