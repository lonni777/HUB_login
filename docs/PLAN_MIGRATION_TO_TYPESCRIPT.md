# План міграції тестів на TypeScript (варіант C)

## Мета
- **Основний стек:** тести пишемо і запускаємо на TypeScript (Playwright + TypeScript).
- **Python-тести:** виносимо в окремий підпроєкт як legacy, без подальшої розробки нових кейсів там.

---

## Таблиця: що зробили / що залишилось

| Що | Статус | Деталі |
|----|--------|--------|
| **Login (login.spec.ts)** | ✅ Зроблено | 11 тестів, усі PASSED. LoginPage, locators, fixtures. |
| **XML-фіди (xml-feed.spec.ts)** | ✅ Зроблено | 11 тестів, усі PASSED. XmlFeedPage, locators, cleanup по БД (delete/deactivate). Тест 11 — обмеження 3 фіди (20.1 с). |
| **Excel мапінг (excel-mapping.spec.ts)** | ⏳ Код є, прогон не фіксували | 2 тести переписані; у статусі — ⏳ не запускався. Потрібні TEST_EXISTING_FEED_ID, перевірка стабільності. |
| **Інфраструктура** | ✅ Зроблено | fixtures/env.ts, utils/db-helper.ts (pg, SSL), playwright.config, .env.example (TEST_DB_SSL). |
| **Документація** | ✅ Частково | README (tests-ts / tests-Python), docs/TS_TESTS_RUN_STATUS.md з часом і статусом по тестах. |
| **Етап 4. Фіксація** | ⏳ Залишилось | Прогнати excel-mapping, пройтися по всіх TS-тестах на стабільність, зафіксувати в docs, що основний набір — tests-ts. |
| **Етап 5. Тільки TS** | ⏳ Залишилось | Усі нові кейси тільки в tests-ts; tests-Python — legacy, без нових кейсів. |

---

## Статус: що вже зроблено (етали плану)

| Етап | Статус | Що зроблено |
|------|--------|--------------|
| **1. Підготовка** | ✅ Виконано | Створено `tests-Python/`, перенесено всі Python-тести, pages, config, utils, conftest, pytest.ini, requirements. Додано README для legacy. |
| **2. Ініціалізація tests-ts** | ✅ Виконано | Створено `tests-ts/` з Playwright + TypeScript, package.json, playwright.config.ts, tsconfig.json, e2e/login.spec.ts. Встановлено залежності та браузери. |
| **3. Переписування тестів** | ✅ Виконано | Login, xml_feed, excel_mapping переписані на TypeScript у tests-ts/. Login і xml-feed прогнані, усі тести проходять. |
| **4. README** | ✅ Виконано | Кореневий README оновлено: два підпроєкти (tests-ts / tests-Python), як запускати. |
| **4. Фіксація** | ⏳ Залишилось | Прогнати excel-mapping; перевірка стабільності всіх TS-тестів; зафіксувати в docs, що основний набір — tests-ts. |
| **5. Тільки TypeScript** | ⏳ Після міграції | Усі нові кейси тільки в tests-ts. |

## Цільова структура проєкту

```
HUB_login/
├── tests-ts/                    # Основні тести (TypeScript, Playwright)
│   ├── e2e/
│   │   ├── login.spec.ts
│   │   ├── xml-feed.spec.ts
│   │   └── ...
│   ├── pages/
│   ├── fixtures/
│   ├── playwright.config.ts
│   ├── package.json
│   └── tsconfig.json
│
├── tests-Python/                # Legacy: існуючі тести на Python
│   ├── tests/
│   │   ├── test_login.py
│   │   ├── test_xml_feed.py
│   │   └── ...
│   ├── pages/
│   ├── config/
│   ├── utils/
│   ├── conftest.py
│   ├── pytest.ini
│   ├── requirements.txt
│   └── README.md                 # Як запускати legacy-тести
│
├── reports/                     # Спільна папка звітів (опційно: окремо для ts/python)
├── docs/
└── README.md                    # Оновлений: опис двох підпроєктів та як їх запускати
```

## Етапи плану

### Етап 1. Підготовка ✅
- [x] Створити папку `tests-Python/` в корені репозиторію.
- [x] Перенести в `tests-Python/` усі Python-артефакти:
  - `tests/` (test_login.py, test_xml_feed.py, test_excel_mapping.py тощо),
  - `pages/`, `locators/`, `config/`, `utils/`, `conftest.py`, `pytest.ini`, `requirements.txt`, копія `.env.example`.
- [x] У корені залишити `tests-ts/`, `tests-Python/`, `docs/`, `reports/`, README, `.env.example`.
- [x] Додати в `tests-Python/README.md` коротку інструкцію: як встановити залежності, як запускати pytest, що це legacy-код.

### Етап 2. Ініціалізація TypeScript-тестів ✅
- [x] Створити `tests-ts/` з повноцінним Playwright + TypeScript проєктом:
  - `package.json` (playwright, typescript, dotenv),
  - `playwright.config.ts`, `tsconfig.json`,
  - базова структура: `e2e/`, `e2e/login.spec.ts`.
- [x] Додати мінімальний e2e-тест логіну; конфіг підвантажує `.env` з кореня репозиторію.

### Етап 3. Переписування тестів з Python на TypeScript ✅
- [x] Скласти список усіх тест-кейсів з `tests-Python/` (login, xml_feed, excel_mapping).
- [x] Переписати на TypeScript у `tests-ts/`:
  - **login:** `e2e/login.spec.ts`, `pages/LoginPage.ts`, `locators/login.locators.ts`
  - **xml_feed:** `e2e/xml-feed.spec.ts`, `pages/XmlFeedPage.ts`, `locators/xml-feed.locators.ts`
  - **excel_mapping:** `e2e/excel-mapping.spec.ts` (використовує XmlFeedPage + xlsx для валідації аркушів).
- [x] Login та xml-feed прогнані, усі тести PASSED; excel-mapping — код є, прогон очікується.

### Етап 4. Фіксація та перевірка
- [ ] Пройтися по усіх переписаних тестах у TypeScript, переконатися, що вони стабільні й збігаються з очікуваною поведінкою.
- [x] Оновити кореневий `README.md`: описати дві частини — `tests-ts` (основні тести) та `tests-Python` (legacy), як їх запускати окремо.
- [ ] У документації (наприклад, у `docs/`) зафіксувати: основні тести тепер у `tests-ts/`, нові кейси пишемо тільки в TypeScript.

### Етап 5. Далі тільки TypeScript
- [ ] Усі нові тест-кейси писати лише в `tests-ts/`.
- [ ] `tests-Python/` не змінювати для нової функціональності; при потребі лише виправляти поломки, якщо хтось тимчасово запускає legacy-набір.

---

## Що робимо далі (наступні кроки)

1. **Excel мапінг — прогон і фіксація**
   - Задати в `.env` `TEST_EXISTING_FEED_ID` (існуючий feed_id з XML-фідів постачальника).
   - Прогнати обидва тести: `npx playwright test e2e/excel-mapping.spec.ts` (з папки `tests-ts/`).
   - Оновити `docs/TS_TESTS_RUN_STATUS.md`: час і статус для тестів Excel мапінгу.

2. **Етап 4 — фіксація**
   - Пройтися по усіх переписаних тестах у TS, переконатися, що вони стабільні.
   - У документації зафіксувати: основний набір тестів — `tests-ts/`, нові кейси пишемо тільки в TypeScript.

3. **Етап 5 — далі тільки TypeScript**
   - Усі нові тест-кейси писати лише в `tests-ts/`.
   - `tests-Python/` не змінювати для нової функціональності; при потребі лише виправляти поломки.

---

## Коротко

| Що | Де |
|----|-----|
| Новий код тестів, запуск локально | **tests-ts/** (TypeScript) |
| Існуючі тести, без нових кейсів | **tests-Python/** (legacy) |
| Після переписування та перевірки | Розробка лише в TypeScript |
