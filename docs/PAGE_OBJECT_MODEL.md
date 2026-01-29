# Page Object Model (POM) - Документація

## Що таке Page Object Model?

Page Object Model (POM) - це патерн проектування для автоматизації тестування, який інкапсулює веб-елементи та методи роботи з ними в окремі класи (Page Objects).

## Структура проекту

### 1. Локатори (`locators/`)

Локатори зберігаються окремо для легкого оновлення:

```python
# locators/login_locators.py
class LoginLocators:
    EMAIL_INPUT = "#email"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#root-content > div:nth-child(2) > form > button"
```

**Переваги:**
- Всі локатори в одному місці
- Легко знайти та оновити
- Зміна локатора оновлює всі тести одразу

### 2. Page Objects (`pages/`)

Page Objects інкапсулюють логіку роботи зі сторінками:

```python
# pages/login_page.py
class LoginPage(BasePage):
    def login(self, email: str, password: str):
        self.fill_email(email)
        self.fill_password(password)
        self.click_login_button()
```

**Переваги:**
- Повторне використання коду
- Чисті та читабельні тести
- Легка підтримка

### 3. Тести (`tests/`)

Тести використовують Page Objects:

```python
# tests/test_login.py
def test_positive_login(self, page: Page, test_config: TestConfig):
    login_page = LoginPage(page)
    login_page.navigate_to_login(test_config.LOGIN_URL)
    login_page.login(email=test_config.USER_EMAIL, password=test_config.USER_PASSWORD)
    login_page.verify_successful_login(expected_url=test_config.DASHBOARD_URL)
```

## Як додати нову сторінку

### Крок 1: Створити локатори

Створіть файл `locators/your_page_locators.py`:

```python
class YourPageLocators:
    ELEMENT_1 = "#selector1"
    ELEMENT_2 = ".class-name"
    BUTTON = "button[type='submit']"
```

### Крок 2: Створити Page Object

Створіть файл `pages/your_page.py`:

```python
from pages.base_page import BasePage
from locators.your_page_locators import YourPageLocators

class YourPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.locators = YourPageLocators()
    
    def do_something(self):
        element = self.page.locator(self.locators.ELEMENT_1)
        element.click()
```

### Крок 3: Використати в тестах

```python
def test_something(self, page: Page):
    your_page = YourPage(page)
    your_page.do_something()
```

## Оновлення локаторів

Якщо змінився селектор на сторінці:

1. Відкрийте відповідний файл локаторів
2. Оновіть потрібний локатор
3. Всі тести автоматично використають новий локатор

**Приклад:**
```python
# Було:
EMAIL_INPUT = "#email"

# Стало:
EMAIL_INPUT = "#user-email"
```

## Кросс-браузерне тестування

Проект підтримує тестування на різних браузерах без змін в коді:

### Підтримувані браузери:
- ✅ **Chromium** (за замовчуванням)
- ✅ **Safari (WebKit)**
- ✅ **Firefox**

### Як це працює:

1. **pytest-playwright автоматично параметризує тести** по браузерам через фікстуру `page: Page`
2. **Page Objects працюють однаково** на всіх браузерах - вони використовують стандартні Playwright API
3. **Локатори не залежать від браузера** - CSS селектори працюють однаково

### Запуск на різних браузерах:

```bash
# Chromium (за замовчуванням)
pytest tests/test_login.py

# Safari (WebKit)
pytest tests/test_login.py --browser webkit

# Firefox
pytest tests/test_login.py --browser firefox

# З відкритим браузером
pytest tests/test_login.py --headed --browser webkit
```

### Переваги POM для кросс-браузерного тестування:

- ✅ **Один код для всіх браузерів** - Page Objects не потребують змін
- ✅ **Легке додавання нових браузерів** - просто встановити та запустити з `--browser`
- ✅ **Консистентність** - локатори та методи працюють однаково на всіх браузерах

## Best Practices

1. ✅ **Один Page Object = одна сторінка**
2. ✅ **Локатори в окремих класах**
3. ✅ **Методи Page Objects повертають об'єкти сторінок для ланцюжкових викликів**
4. ✅ **Базовий клас для загальних методів**
5. ✅ **Описові назви методів**
6. ✅ **Кросс-браузерна сумісність** - використовувати стандартні Playwright API

## Приклади

### Додавання методу в Page Object

```python
class LoginPage(BasePage):
    def fill_email(self, email: str):
        email_input = self.page.locator(self.locators.EMAIL_INPUT)
        email_input.fill(email)
        return self  # Для ланцюжкових викликів
```

### Використання в тесті

```python
login_page = LoginPage(page)
login_page.fill_email("test@example.com").fill_password("password").click_login_button()
```
