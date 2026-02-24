# Приклад запуску крону через Postman

Покроковий приклад для **одного** ендпоінту: запуск задачі `feed/run-priority` (завантаження фідів з черги).

---

## Передумови

- Доступ до бранча Hub (наприклад `https://sm-1047.chub.kasta.ua` або `https://hubtest.kasta.ua`)
- Обліковий запис **superuser**
- Postman встановлений

---

## Крок 1: Отримати sessionid

1. Відкрити в браузері URL бранча (наприклад `https://sm-1047.chub.kasta.ua`).
2. Увійти як superuser.
3. Відкрити **DevTools** (F12) → вкладка **Application** → **Cookies** → вибрати домен.
4. Знайти cookie `sessionid` і скопіювати його **Value**.

---

## Крок 2: Створити запит у Postman

### Поля запиту

| Поле | Значення |
|------|----------|
| **Method** | `POST` |
| **URL** | `https://sm-1047.chub.kasta.ua/api/admin-cron/run` |

*(Замініть `sm-1047.chub.kasta.ua` на свій бранч, наприклад `hubtest.kasta.ua`.)*

### Headers

| Key | Value |
|-----|-------|
| `Content-Type` | `application/json` |
| `Cookie` | `sessionid=<ваш_sessionid>` |

*(Підставте замість `<ваш_sessionid>` значення з кроку 1.)*

### Body

- **Body type:** `raw`
- **Format:** `JSON`

```json
{
  "task": "feed/run-priority"
}
```

---

## Крок 3: Як це виглядає в Postman (візуально)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ POST  | https://sm-1047.chub.kasta.ua/api/admin-cron/run              [Send] │
├─────────────────────────────────────────────────────────────────────────────┤
│ Params  Authorization  Headers  Body  Pre-request  Tests  Settings           │
│                                                                              │
│ Headers (2)                                                                  │
│ ┌─────────────────┬──────────────────────────────────────────────────────┐  │
│ │ Content-Type    │ application/json                                     │  │
│ │ Cookie          │ sessionid=abc123xyz789...                            │  │
│ └─────────────────┴──────────────────────────────────────────────────────┘  │
│                                                                              │
│ Body  ○ none  ○ form-data  ○ x-www-form-urlencoded  ● raw  ○ binary        │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ {                                                                       │ │
│ │   "task": "feed/run-priority"                                            │ │
│ │ }                                                                       │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│ JSON                                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Крок 4: Натиснути Send

### Очікувана відповідь (200 OK)

```json
{
  "task-id": "admin-cron-abc123-xyz789",
  "task": "feed/run-priority",
  "status": "running"
}
```

### Можливі помилки

| Код | Причина |
|-----|---------|
| 401 | Немає cookie або sessionid прострочений — перелогінься в браузері і онови sessionid |
| 403 | Користувач не superuser або ендпоінт заблокований на production |
| 404 | Ендпоінт ще не реалізований (admin-cron API) |
| 422 | Невідома задача — перевір `task` у body |

---

## Інші feed-задачі для body

Замість `feed/run-priority` можна вказати:

```json
{"task": "feed/load-content"}
```

```json
{"task": "feed/refresh-global-manual-mappings"}
```

```json
{"task": "feed/pp-tree-sync-light"}
```

---

## Postman Collection (імпорт)

Можна зберегти як `.json` і імпортувати в Postman:

```json
{
  "info": { "name": "Hub Admin Cron", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json" },
  "item": [
    {
      "name": "Run feed/run-priority",
      "request": {
        "method": "POST",
        "header": [
          { "key": "Content-Type", "value": "application/json" },
          { "key": "Cookie", "value": "sessionid={{sessionid}}" }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"task\": \"feed/run-priority\"}"
        },
        "url": "{{baseUrl}}/api/admin-cron/run"
      }
    }
  ],
  "variable": [
    { "key": "baseUrl", "value": "https://sm-1047.chub.kasta.ua" },
    { "key": "sessionid", "value": "" }
  ]
}
```

Після імпорту встановити змінну `sessionid` у Collection Variables.

---

## Важливо

**admin-cron API** може ще не бути реалізований у kastaua-hub. Якщо отримаєте 404 — ендпоінт потрібно додати в бекенд. Цей документ описує очікуваний формат виклику.
