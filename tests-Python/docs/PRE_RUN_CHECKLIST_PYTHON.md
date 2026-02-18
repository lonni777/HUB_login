# Чеклист перед запуском тестів (tests-Python, pytest) — legacy

Для основних тестів (TypeScript) див. [../../docs/PRE_RUN_CHECKLIST.md](../../docs/PRE_RUN_CHECKLIST.md).

---

## Перевірка перед запуском (pytest)

### 1. Конфігурація (.env)
Файл `.env` у **корені** репозиторію (спільний з tests-ts). Потрібні:
- `TEST_USER_EMAIL`, `TEST_USER_PASSWORD`
- `TEST_LOGIN_URL` (або `TEST_BASE_URL`)
- за потреби: `TEST_DASHBOARD_URL`, `TEST_NON_EXISTENT_USER_EMAIL`

### 2. Залежності
```bash
cd tests-Python
pip install -r requirements.txt
playwright install
```

### 3. Структура
- `tests-Python/tests/`, `conftest.py`, `pytest.ini`, `config/settings.py` мають існувати.

---

## Запуск

```bash
cd tests-Python
pytest
pytest -v
pytest tests/test_login.py -v
pytest --headed --browser webkit
```

---

## Звіти (pytest)

- HTML-звіт: `reports/report_YYYYMMDD_HHMMSS.html` (генерується з timestamp).
- Bug report при падінні: `reports/last_failure_bug_report.txt`.
- Скріншоти при помилках: `test-results/screenshots/`.

Деталі налаштувань — у `conftest.py` та `pytest.ini`.
