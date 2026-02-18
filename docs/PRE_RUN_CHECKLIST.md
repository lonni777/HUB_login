# Чеклист перед запуском тестів (tests-ts, TypeScript)

## Перевірка перед запуском

### 1. Конфігурація (.env)

Файл **`.env`** має бути в **корені** репозиторію (не в tests-ts). Скопіюйте `.env.example` у `.env` і заповніть:

| Змінна | Призначення |
|--------|-------------|
| `TEST_USER_EMAIL` | Email для логіну |
| `TEST_USER_PASSWORD` | Пароль |
| `TEST_LOGIN_URL` або `TEST_BASE_URL` | URL сторінки логіну (наприклад `https://hubtest.kasta.ua/user/login`) |
| `TEST_DASHBOARD_URL` | (Опціонально) URL після успішного логіну |
| `TEST_SUPPLIER_NAME` / `TEST_SUPPLIER` | Постачальник для тестів XML-фідів |
| `TEST_XML_FEED_URL` | Валідний URL XML-фіду для тестів |
| `TEST_EXISTING_FEED_ID` | Існуючий feed_id для тестів Excel-мапінгу (наприклад R3DV) |
| `TEST_XML_FEEDS_URL` | Базовий URL сторінки XML-фідів |

Якщо не задані обов’язкові змінні, тести можуть пропускатися (skip) з повідомленням у логах.

### 2. Залежності та браузери

З каталогу **tests-ts**:

```bash
cd tests-ts
npm install
npx playwright install
```

При потребі встановити лише Chromium:

```bash
npx playwright install chromium
```

### 3. Структура проєкту

Переконайтеся, що є:

- Файл `.env` у корені репо (або змінні середовища задані інакше).
- У tests-ts: `playwright.config.ts`, `fixtures/env.ts`, `e2e/*.spec.ts`, `pages/`, `locators/`.

---

## Що буде при запуску

### Успішний прогон (приклад)

```
Running 24 tests using 1 worker
  24 passed (3m)
```

### Типові помилки

**Відсутні секрети:**

Тест виконає `test.skip(true, 'TEST_USER_EMAIL та TEST_USER_PASSWORD мають бути задані в .env')` — перевірте `.env`.

**Таймаут навігації:**

```
page.goto: Timeout 30000ms exceeded
```

Перевірте `TEST_LOGIN_URL` / мережу / доступність стенду.

**Таймаут локатора:**

```
locator.fill: Timeout 30000ms exceeded
```

Можлива зміна верстки — перевірте локатори в `locators/` та оновіть за потреби.

---

## Команди запуску

Усі команди виконуються з каталогу **tests-ts**.

| Дія | Команда |
|-----|--------|
| Усі тести | `npm run test` |
| З відкритим браузером | `npm run test:headed` |
| UI mode | `npm run test:ui` |
| Один файл | `npx playwright test e2e/login.spec.ts` |
| Один тест за назвою | `npx playwright test e2e/login.spec.ts -g "успішний логін"` |
| Конкретний сьют | `npm run test:login` / `test:xml-feed` / `test:excel-mapping` (якщо є в package.json) |

---

## Що робить тест (логін)

1. Завантажує конфіг з `.env` через `fixtures/env.ts`.
2. Відкриває браузер (Playwright).
3. Переходить на сторінку логіну (`LoginPage.navigateToLogin(loginUrl)`).
4. Заповнює email і пароль, натискає «Увійти» (`LoginPage.login()`).
5. Перевіряє успішний вхід (URL або відсутність `/user/login`) (`LoginPage.verifySuccessfulLogin()`).

Інші сьюти (xml-feed, excel-mapping) використовують логін у `beforeEach` і далі працюють через `XmlFeedPage`.

---

## Звіти

- **Allure:** після прогону згенерувати звіт: `npm run allure:generate`, відкрити: `npm run allure:open` → http://localhost:9753/index.html.
- Детально: [REPORTS_AND_ARTIFACTS.md](REPORTS_AND_ARTIFACTS.md) та [TEST_REPORTS.md](TEST_REPORTS.md).

---

## Важливі зауваження

1. **Секрети не комітяться** — `.env` у `.gitignore`.
2. **Браузер** — за замовчуванням headless; для відлагодження використовуйте `npm run test:headed` або UI mode.
3. **Дані** — тести використовують реальні облікові записи та стенд; переконайтеся, що обліковий запис активний і URL правильний.
4. **Legacy Python-тести** — окремо в tests-Python; чеклист для них: [tests-Python/docs/PRE_RUN_CHECKLIST_PYTHON.md](../tests-Python/docs/PRE_RUN_CHECKLIST_PYTHON.md).
