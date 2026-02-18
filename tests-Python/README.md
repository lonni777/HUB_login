# tests-Python (legacy)

Цей каталог містить **legacy-тести** на Python (pytest + Playwright).  
Нові тест-кейси пишуться в **tests-ts/** (TypeScript). Тут лишаються існуючі тести для зворотної сумісності та можливості їх запуску.

## Що всередині

- `tests/` — тести (login, xml_feed, excel_mapping)
- `pages/`, `locators/`, `config/`, `utils/` — Page Object, конфіг, хелпери
- `conftest.py` — фікстури pytest та Playwright
- `pytest.ini` — налаштування pytest
- `requirements.txt` — залежності Python

## Як запускати

1. **Перейти в каталог і встановити залежності:**

   ```bash
   cd tests-Python
   pip install -r requirements.txt
   playwright install
   ```

2. **Створити `.env`** на основі `.env.example` у цьому каталозі та заповнити обов'язкові змінні (логін, пароль, URL тощо).

3. **Запуск тестів** (з каталогу `tests-Python` або з кореня репозиторію):

   ```bash
   # З каталогу tests-Python
   pytest

   # Всі тести з відкритим браузером
   pytest --headed -v

   # Один файл
   pytest tests/test_login.py -v

   # Один тест
   pytest tests/test_xml_feed.py::TestXMLFeed::test_add_same_url_twice_no_duplicate --headed -v
   ```

4. **Звіти** зберігаються в корені репозиторію: `../reports/report_YYYYMMDD_HHMMSS.html`.

## Примітка

Цей набір тестів більше не розширюється новими кейсами. Усі нові тести пишуться в **tests-ts/** (TypeScript).
