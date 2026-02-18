# Тести XML-фідів (tests-ts)

Сьют: **`tests-ts/e2e/xml-feed.spec.ts`**. Використовуються Page Object `XmlFeedPage` та локатори `xml-feed.locators.ts`.

---

## Валідний фід (додавання, нормалізація, Excel-мапінг)

**URL (за замовчуванням):**  
https://gist.github.com/lonni777/dc7d69b7226ce29d807d762bbb054598

Змінна в `.env`: **`TEST_XML_FEED_URL`**.

Використовується в тестах:

- Збереження валідного URL без пробілів
- Збереження нормалізованого URL (пробіли до/після)
- Excel-мапінг (скачування/завантаження) — у `excel-mapping.spec.ts`

---

## TC-XML-007: Таймаут при збереженні фіду

### Ліміти feed-download (валідація при «Зберегти»)

При натисканні «Зберегти» валідація фіду використовує feed-download з такими таймаутами:

| Параметр | Значення | Опис |
|----------|----------|------|
| **conn-timeout** | 1 хв | Якщо сервер не відповідає протягом 1 хв → "Connect timed out" |
| **socket-timeout** | 5 хв | Якщо після з'єднання дані не надходять 5 хв → "Operation timed out" / "Таймаут завантаження фіду" |

### Що тестуємо

Тест перевіряє **conn-timeout 1 хв** (не socket-timeout 5 хв).

**Очікувана помилка:**  
`Помилка валідації xml структури фіду помилка завантаження фіду: Connect timed out`

### URL для тесту

Потрібен URL, який **не відповідає** протягом 1 хв (з'єднання не встановлюється):

- `http://192.0.2.1/xml` — non-routable IP (TEST-NET), гарантовано connection timeout.

**Не використовувати** httpbin.org/delay — повертає JSON за ~10 с → помилка валідації XML, а не таймаут.

Змінна в `.env`: **`TEST_TIMEOUT_FEED_URL`** (за замовчуванням вже `http://192.0.2.1/xml`). Конфіг і чеклист: [PRE_RUN_CHECKLIST.md](PRE_RUN_CHECKLIST.md), [fixtures/env.ts](../tests-ts/fixtures/env.ts).
