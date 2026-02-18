# Документація проєкту (TypeScript — основний стек)

Усі документи тут описують **tests-ts** (TypeScript, Playwright). Python-тести — legacy, їхня документація в [tests-Python/docs/](../tests-Python/docs/).

---

## Зміст

| Документ | Опис |
|----------|------|
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Структура репо: tests-ts, tests-Python, репорти, де що лежить |
| [PAGE_OBJECT_MODEL.md](PAGE_OBJECT_MODEL.md) | Патерн POM у tests-ts: локатори, Page Objects, приклади на TypeScript |
| [PRE_RUN_CHECKLIST.md](PRE_RUN_CHECKLIST.md) | Чеклист перед запуском тестів (.env, залежності, команди) |
| [SECRETS_MANAGEMENT.md](SECRETS_MANAGEMENT.md) | Секрети: .env, fixtures/env.ts, CI/CD |
| [TEST_REPORTS.md](TEST_REPORTS.md) | Звіти: Allure (tests-ts), як генерувати й відкривати |
| [REPORTS_AND_ARTIFACTS.md](REPORTS_AND_ARTIFACTS.md) | Деталі Allure, історія прогонів (3 на сьют), артефакти при падінні |
| [TS_TESTS_RUN_STATUS.md](TS_TESTS_RUN_STATUS.md) | Статус проходження тестів (час, PASSED/FAILED по сьютах) |
| [XML_FEED_TESTS.md](XML_FEED_TESTS.md) | Тести XML-фідів: URL, TC-XML-007 (таймаут), змінні .env |

---

## Швидкий старт

1. **Конфіг:** `.env` у корені репо (скопіювати з `.env.example`).  
2. **Запуск:** `cd tests-ts && npm install && npx playwright install && npm run test`.  
3. **Звіт:** `npm run allure:generate && npm run allure:open` → http://localhost:9753/index.html.

Детально: [PRE_RUN_CHECKLIST.md](PRE_RUN_CHECKLIST.md), [tests-ts/README.md](../tests-ts/README.md).
