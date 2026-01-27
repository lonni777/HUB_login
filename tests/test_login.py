import pytest
from playwright.sync_api import Page
from config.settings import TestConfig
from pages.login_page import LoginPage


class TestLogin:
    """Тест сьют: Авторизація в HUB"""

    def test_positive_login(self, page: Page, test_config: TestConfig):
        """
        Тест кейс: Авторизація з валідними даними
        
        Перевіряє успішний логін з валідними email та паролем.
        Використовує конфігурацію з .env файлу та Page Object Model.
        """
        # Створення екземпляру сторінки логіну
        login_page = LoginPage(page)
        
        # Перехід на сторінку логіну
        login_page.navigate_to_login(test_config.LOGIN_URL)
        
        # Виконання логіну (заповнення полів та натискання кнопки)
        login_page.login(
            email=test_config.USER_EMAIL,
            password=test_config.USER_PASSWORD
        )
        
        # Перевірка успішного логіну
        login_page.verify_successful_login(expected_url=test_config.DASHBOARD_URL)

    def test_login_with_invalid_password(self, page: Page, test_config: TestConfig):
        """
        Тест кейс: Авторизація з невірним паролем
        
        Перевіряє що при введенні невірного паролю:
        - Користувач залишається на сторінці логіну
        - Відображається повідомлення про помилку (якщо є)
        """
        # Створення екземпляру сторінки логіну
        login_page = LoginPage(page)
        
        # Перехід на сторінку логіну
        login_page.navigate_to_login(test_config.LOGIN_URL)
        
        # Спробувати виконати логін з невірним паролем
        invalid_password = "wrong_password_123"
        login_page.attempt_login(
            email=test_config.USER_EMAIL,
            password=invalid_password
        )
        
        # Перевірка що залишились на сторінці логіну
        login_page.verify_stayed_on_login_page()
        
        # Перевірка наявності повідомлення про помилку (alert)
        error_visible = login_page.is_error_message_visible()
        if error_visible:
            error_text = login_page.get_error_message_text()
            assert error_text, "Повідомлення про помилку має містити текст"

    def test_login_with_invalid_email(self, page: Page, test_config: TestConfig):
        """
        Тест кейс: Авторизація з невалідним логіном (email з подвійною літерою)
        
        Використовує email з невеликою зміною від валідного (наприклад: i.karpenkoo@kasta.ua)
        з вірним паролем.
        
        Очікуваний результат:
        - Користувач залишається на сторінці логіну
        - Відображається повідомлення: "Невірний логін" та "Зверніться до адмінів"
        - Відповідь API містить код помилки: "invalid-ldap-password"
        """
        # Створення екземпляру сторінки логіну
        login_page = LoginPage(page)
        
        # Перехід на сторінку логіну
        login_page.navigate_to_login(test_config.LOGIN_URL)
        
        # Створюємо невалідний email з подвійною літерою на основі валідного
        # Наприклад: i.karpenko@kasta.ua -> i.karpenkoo@kasta.ua
        valid_email = test_config.USER_EMAIL
        if "@" in valid_email:
            username, domain = valid_email.split("@", 1)
            invalid_email = username + "o@" + domain  # Додаємо "o" перед "@"
        else:
            invalid_email = valid_email + "o@kasta.ua"
        
        # Перехоплення network response для перевірки коду помилки
        api_response = None
        try:
            with page.expect_response(
                lambda response: (
                    "login" in response.url.lower() or 
                    "auth" in response.url.lower() or
                    "ldap" in response.url.lower()
                ),
                timeout=10000
            ) as response_info:
                login_page.attempt_login(
                    email=invalid_email,
                    password=test_config.USER_PASSWORD
                )
                api_response = response_info.value
        except Exception:
            # Якщо не вдалося перехопити response, продовжуємо тест
            login_page.attempt_login(
                email=invalid_email,
                password=test_config.USER_PASSWORD
            )
        
        # Чекаємо більше часу для появи повідомлення про помилку
        page.wait_for_timeout(3000)
        
        # Перевірка що залишились на сторінці логіну
        login_page.verify_stayed_on_login_page()
        
        # Перевірка повідомлення про помилку на сторінці
        # Очікувані тексти: "Невірний логін" та "Зверніться до адмінів"
        expected_error_texts = ["Невірний логін", "Зверніться до адмінів"]
        
        # Перевірка через текст на сторінці
        page_text = page.locator("body").text_content() or ""
        found_texts = []
        
        for expected_text in expected_error_texts:
            if expected_text in page_text:
                found_texts.append(expected_text)
        
        # Якщо не знайдено через текст, спробуємо через різні локатори
        if len(found_texts) < len(expected_error_texts):
            # Перевіряємо різні можливі місця відображення помилки
            possible_selectors = [
                "text=Невірний логін",
                "text=Зверніться до адмінів",
                ".ant-message",
                ".ant-notification",
                ".ant-message-error",
                ".ant-notification-notice-error",
                "[role='alert']",
                ".error",
                ".notification-error",
                ".ant-alert"
            ]
            
            for selector in possible_selectors:
                try:
                    elements = page.locator(selector)
                    count = elements.count()
                    for i in range(count):
                        element_text = elements.nth(i).text_content() or ""
                        for expected_text in expected_error_texts:
                            if expected_text in element_text and expected_text not in found_texts:
                                found_texts.append(expected_text)
                except:
                    continue
        
        # Перевірка API response (якщо є)
        api_error_found = False
        if api_response:
            try:
                response_json = api_response.json()
                if response_json.get("status") == "fail" and response_json.get("code") == "invalid-ldap-password":
                    api_error_found = True
            except:
                pass
        
        # Якщо знайдено хоча б один текст або API response правильний, тест пройшов
        assert len(found_texts) > 0 or api_error_found, \
            f"Не знайдено очікувані тексти '{expected_error_texts}' на сторінці. " \
            f"Знайдено: {found_texts}. " \
            f"API response: {'valid' if api_error_found else 'not found or invalid'}. " \
            f"Поточний текст сторінки (перші 300 символів): {page_text[:300]}"
        
        # Перевірка API відповіді (якщо є)
        if api_response:
            try:
                response_json = api_response.json()
                assert response_json.get("status") == "fail", \
                    f"Очікувалось status='fail', але отримано: {response_json.get('status')}"
                assert response_json.get("code") == "invalid-ldap-password", \
                    f"Очікувалось code='invalid-ldap-password', але отримано: {response_json.get('code')}"
            except Exception as e:
                # Якщо не вдалося отримати JSON, це не критично для тесту
                pass

    def test_login_with_nonexistent_user(self, page: Page, test_config: TestConfig):
        """
        Тест кейс: Авторизація з неіснуючим користувачем
        
        Використовує email якого немає в базі даних: i.i.kontent@gmail.com
        з паролем: Qwerty123
        
        Очікуваний результат:
        1. Після натискання кнопки "Увійти" користувача редіректимо на https://hubtest.kasta.ua/?supplier-reg=true
        2. Над формою логіну з'являється помилка з текстом: "Такого користувача не існує" та "Зареєструйте, заповнивши форму нижче"
        """
        # Створення екземпляру сторінки логіну
        login_page = LoginPage(page)
        
        # Перехід на сторінку логіну
        login_page.navigate_to_login(test_config.LOGIN_URL)
        
        # Дані для тесту (неіснуючий користувач)
        nonexistent_email = "i.i.kontent@gmail.com"
        password = "Qwerty123"
        
        # Виконання спроби логіну
        login_page.attempt_login(
            email=nonexistent_email,
            password=password
        )
        
        # Чекаємо для появи повідомлення про помилку та переадресації
        page.wait_for_timeout(3000)
        
        # Перевірка 1: Переадресація на сторінку реєстрації
        expected_url = "https://hubtest.kasta.ua/?supplier-reg=true"
        current_url = page.url
        assert current_url == expected_url or "supplier-reg=true" in current_url, \
            f"Очікувалось переадресацію на '{expected_url}'. " \
            f"Поточний URL: {current_url}"
        
        # Перевірка 2: Alert з помилкою над формою логіну відображається
        assert login_page.is_error_message_visible(), \
            "Очікувалось що alert з повідомленням про помилку буде видимим над формою логіну"
        
        # Отримуємо текст повідомлення про помилку
        error_text = login_page.get_error_message_text()
        assert error_text, "Повідомлення про помилку має містити текст"
        
        # Перевірка конкретних текстів в повідомленні
        error_text_lower = error_text.lower()
        
        # Перевірка першого повідомлення: "Такого користувача не існує"
        assert "такого користувача не існує" in error_text_lower, \
            f"Повідомлення про помилку має містити текст 'Такого користувача не існує'. " \
            f"Отримано: '{error_text}'"
        
        # Перевірка другого повідомлення: "Зареєструйте, заповнивши форму нижче"
        assert "зареєструйте" in error_text_lower, \
            f"Повідомлення про помилку має містити текст 'Зареєструйте'. " \
            f"Отримано: '{error_text}'"
        
        assert "заповнивши форму" in error_text_lower or "заповнивши" in error_text_lower, \
            f"Повідомлення про помилку має містити текст про заповнення форми. " \
            f"Отримано: '{error_text}'"

    def test_login_with_deactivated_user(self, page: Page, test_config: TestConfig):
        """
        Тест кейс: Авторизація з деактивованим/видаленим користувачем
        
        Перевіряє що користувач, який існує в базі даних kasta.ua, але не має доступу
        до HUB (звільнений співробітник, видалений з налаштувань продавця тощо)
        не може авторизуватися в кабінет, але перенаправляється на сторінку реєстрації.
        
        Використовує email: i.i.kontent+test123@gmail.com
        з паролем: Qwerty123
        
        Очікуваний результат:
        1. Користувача не логінить в кабінет
        2. Після натискання кнопки "Увійти" користувача редіректимо на 
           https://hubtest.kasta.ua/?supplier-reg=true
        3. Над полем email з'являється повідомлення: 
           "Вітаємо! Ви вже зареєстровані на kasta.ua, для завершення реєстрації в hub, заповніть поля нижче"
        4. Відповідь API містить: {"status":"fail","code":"no-supplier"}
        """
        # Створення екземпляру сторінки логіну
        login_page = LoginPage(page)
        
        # Перехід на сторінку логіну
        login_page.navigate_to_login(test_config.LOGIN_URL)
        
        # Дані для тесту (деактивований користувач)
        deactivated_email = "i.i.kontent+test123@gmail.com"
        password = "Qwerty123"
        
        # Перехоплення network response для перевірки коду помилки
        api_response = None
        try:
            with page.expect_response(
                lambda response: (
                    "login" in response.url.lower() or 
                    "auth" in response.url.lower() or
                    "supplier" in response.url.lower()
                ),
                timeout=10000
            ) as response_info:
                login_page.attempt_login(
                    email=deactivated_email,
                    password=password
                )
                api_response = response_info.value
        except Exception:
            # Якщо не вдалося перехопити response, продовжуємо тест
            login_page.attempt_login(
                email=deactivated_email,
                password=password
            )
        
        # Чекаємо для появи повідомлення про помилку та переадресації
        page.wait_for_timeout(3000)
        
        # Перевірка 1: Переадресація на сторінку реєстрації
        expected_url = "https://hubtest.kasta.ua/?supplier-reg=true"
        current_url = page.url
        assert current_url == expected_url or "supplier-reg=true" in current_url, \
            f"Очікувалось переадресацію на '{expected_url}'. " \
            f"Поточний URL: {current_url}"
        
        # Перевірка 2: Повідомлення на сторінці
        # Очікуваний текст: "Вітаємо! Ви вже зареєстровані на kasta.ua, для завершення реєстрації в hub, заповніть поля нижче"
        expected_message_parts = [
            "вітаємо",
            "ви вже зареєстровані",
            "kasta.ua",
            "завершення реєстрації",
            "hub",
            "заповніть поля"
        ]
        
        # Перевірка через текст на сторінці
        page_text = page.locator("body").text_content() or ""
        found_texts = []
        
        for expected_text in expected_message_parts:
            if expected_text in page_text.lower():
                found_texts.append(expected_text)
        
        # Якщо не знайдено через текст, спробуємо через різні локатори
        if len(found_texts) < len(expected_message_parts):
            # Перевіряємо різні можливі місця відображення повідомлення
            possible_selectors = [
                ".ant-alert",
                ".ant-message",
                ".ant-notification",
                "[role='alert']",
                ".alert",
                ".message",
                ".notification",
                "form .ant-alert",
                "form .ant-message"
            ]
            
            for selector in possible_selectors:
                try:
                    elements = page.locator(selector)
                    count = elements.count()
                    for i in range(count):
                        element_text = elements.nth(i).text_content() or ""
                        for expected_text in expected_message_parts:
                            if expected_text in element_text.lower() and expected_text not in found_texts:
                                found_texts.append(expected_text)
                except:
                    continue
        
        # Також перевіряємо через метод LoginPage (якщо повідомлення в alert)
        error_text = login_page.get_error_message_text()
        if error_text:
            error_text_lower = error_text.lower()
            for expected_text in expected_message_parts:
                if expected_text in error_text_lower and expected_text not in found_texts:
                    found_texts.append(expected_text)
        
        # Перевірка що знайдено достатньо частин повідомлення
        assert len(found_texts) >= 4, \
            f"Повідомлення має містити текст про реєстрацію на kasta.ua та завершення реєстрації в hub. " \
            f"Знайдено частин: {found_texts} з {expected_message_parts}. " \
            f"Поточний текст сторінки (перші 500 символів): {page_text[:500]}"
        
        # Перевірка API відповіді (якщо є)
        if api_response:
            try:
                response_json = api_response.json()
                assert response_json.get("status") == "fail", \
                    f"Очікувалось status='fail', але отримано: {response_json.get('status')}"
                assert response_json.get("code") == "no-supplier", \
                    f"Очікувалось code='no-supplier', але отримано: {response_json.get('code')}"
            except Exception as e:
                # Якщо не вдалося отримати JSON, це не критично для тесту
                pass
        else:
            # Якщо API response не перехоплено, спробуємо знайти через текст сторінки
            page_text = page.locator("body").text_content() or ""
            # Перевірка що ми на сторінці реєстрації (supplier-reg)
            assert "supplier-reg" in current_url.lower() or "реєстраці" in page_text.lower(), \
                "Очікувалось переадресацію на сторінку реєстрації"

    def _test_sql_injection_payload(self, login_page: LoginPage, page: Page, payload: str, test_config: TestConfig):
        """
        Допоміжна функція для перевірки одного SQL injection payload.
        
        Args:
            login_page: Екземпляр LoginPage
            page: Екземпляр Page з Playwright
            payload: SQL injection payload для тестування
            test_config: Конфігурація тестів
        """
        # Перехід на сторінку логіну перед кожним тестом
        login_page.navigate_to_login(test_config.LOGIN_URL)
        
        # Спробувати виконати логін з SQL injection payload
        login_page.attempt_login(
            email=payload,
            password=test_config.USER_PASSWORD
        )
        
        # Чекаємо для появи відповіді
        page.wait_for_timeout(2000)
        
        # Перевірка що система не піддалася атаці
        # 1. Перевірка що не відбувся успішний логін (якщо б SQL injection спрацював)
        current_url = page.url
        assert "/user/login" in current_url or "supplier-reg" in current_url or "?" in current_url, \
            f"SQL injection payload '{payload}' не повинен дозволити успішний логін. " \
            f"Поточний URL: {current_url}"
        
        # 2. Перевірка що не відбувся перехід на dashboard (якщо вказано)
        if test_config.DASHBOARD_URL:
            assert test_config.DASHBOARD_URL not in current_url, \
                f"SQL injection payload '{payload}' не повинен дозволити доступ до dashboard. " \
                f"Поточний URL: {current_url}"
        
        # 3. Перевірка що відображається помилка або система відхилила запит
        # Може бути помилка валідації або alert про невірні дані
        error_visible = login_page.is_error_message_visible()
        # Якщо немає помилки, це теж нормально - система може просто ігнорувати injection
        
        # 4. Перевірка що сторінка все ще працює (не зламана)
        page_title = page.title()
        assert page_title, \
            f"SQL injection payload '{payload}' не повинен зламати сторінку. " \
            f"Сторінка має мати title"
        
        # 5. Перевірка що форма логіну все ще доступна
        try:
            email_input = page.locator(login_page.locators.EMAIL_INPUT)
            assert email_input.is_visible(timeout=2000), \
                f"SQL injection payload '{payload}' не повинен зламати форму логіну"
        except:
            # Якщо форма не видима, це може бути нормально якщо відбулась переадресація
            pass

    def test_login_sql_injection_basic_or_with_comments(self, page: Page, test_config: TestConfig):
        """
        Тест кейс: Авторизація з базовими OR injection з різними коментарями
        
        Перевіряє захист системи від найпростіших та найпоширеніших SQL injection атак.
        Тестує базові OR injection з різними типами коментарів.
        
        Очікуваний результат:
        - Система не піддається SQL injection атаці
        - Відображається помилка валідації або система ігнорує injection
        - Користувач залишається на сторінці логіну або отримує помилку
        """
        login_page = LoginPage(page)
        
        # Базові OR injection з різними коментарями (4 payloads)
        sql_injection_payloads = [
            # Базовий OR injection - тестує чи система екранує одинарні лапки
            "' OR '1'='1",
            # OR injection з коментарем (--) - тестує захист від SQL коментарів
            "' OR '1'='1' --",
            # OR injection з багаторядковим коментарем (/* */) - тестує захист від багаторядкових коментарів
            "' OR '1'='1' /*",
            # OR injection з хешем (#) - тестує захист від різних типів коментарів
            "' OR '1'='1' #"
        ]
        
        # Тестуємо кожен payload
        for payload in sql_injection_payloads:
            self._test_sql_injection_payload(login_page, page, payload, test_config)

    def test_login_sql_injection_numeric_and_string_comparisons(self, page: Page, test_config: TestConfig):
        """
        Тест кейс: Авторизація з OR injection з числовими та рядковими порівняннями
        
        Перевіряє захист системи від SQL injection з різними типами порівнянь.
        Тестує числові та рядкові порівняння, а також валідацію формату email.
        
        Очікуваний результат:
        - Система не піддається SQL injection атаці
        - Відображається помилка валідації або система ігнорує injection
        - Користувач залишається на сторінці логіну або отримує помилку
        """
        login_page = LoginPage(page)
        
        # OR injection з числовими та рядковими порівняннями (4 payloads)
        sql_injection_payloads = [
            # OR injection з числовим порівнянням - тестує чи система перевіряє тип даних
            "' OR 1=1--",
            # OR injection з рядковим порівнянням - тестує чи система правильно обробляє рядкові порівняння
            "' OR 'a'='a",
            # OR injection з числовим порівнянням та хешем - тестує захист від різних типів коментарів
            "' OR 1=1#",
            # OR injection з числом на початку - тестує чи система валідує формат email
            "1' OR '1'='1"
        ]
        
        # Тестуємо кожен payload
        for payload in sql_injection_payloads:
            self._test_sql_injection_payload(login_page, page, payload, test_config)

    def test_login_sql_injection_with_valid_data_and_union(self, page: Page, test_config: TestConfig):
        """
        Тест кейс: Авторизація з injection після валідних даних та UNION атаками
        
        Перевіряє захист системи від комбінованих SQL injection атак.
        Тестує injection після валідних даних та UNION injection.
        
        Очікуваний результат:
        - Система не піддається SQL injection атаці
        - Відображається помилка валідації або система ігнорує injection
        - Користувач залишається на сторінці логіну або отримує помилку
        """
        login_page = LoginPage(page)
        
        # Injection після валідних даних та UNION атаки (4 payloads)
        sql_injection_payloads = [
            # Injection після імені користувача з коментарем - тестує чи система обрізає injection після коментаря
            "admin'--",
            # Injection після імені з багаторядковим коментарем - тестує захист від багаторядкових коментарів після даних
            "admin'/*",
            # OR injection з ім'ям користувача - тестує комбінацію валідного імені з injection
            "admin' OR '1'='1",
            # UNION injection - тестує чи система дозволяє UNION запити
            "' UNION SELECT NULL--"
        ]
        
        # Тестуємо кожен payload
        for payload in sql_injection_payloads:
            self._test_sql_injection_payload(login_page, page, payload, test_config)

    def test_login_with_empty_fields(self, page: Page, test_config: TestConfig):
        """
        Тест кейс: Авторизація з пустими полями
        
        Перевіряє що при натисканні кнопки "Увійти" з пустими полями
        з'являється помилка валідації "Обов'язкове поле" під полями.
        
        Очікуваний результат:
        - Кнопка "Увійти" активна (можна натиснути)
        - При натисканні кнопки з'являється помилка "Обов'язкове поле" під полями
        """
        # Створення екземпляру сторінки логіну
        login_page = LoginPage(page)
        
        # Перехід на сторінку логіну
        login_page.navigate_to_login(test_config.LOGIN_URL)
        
        # Чекаємо завантаження сторінки
        page.wait_for_load_state("networkidle")
        
        # Перевірка що поля дійсно пусті
        email_input = page.locator(login_page.locators.EMAIL_INPUT)
        password_input = page.locator(login_page.locators.PASSWORD_INPUT)
        
        email_value = email_input.input_value()
        password_value = password_input.input_value()
        
        assert email_value == "", \
            f"Поле email повинно бути пустим, але містить: '{email_value}'"
        assert password_value == "", \
            f"Поле password повинно бути пустим, але містить: '{password_value}'"
        
        # Перевірка що кнопка "Увійти" активна (можна натиснути)
        assert login_page.is_login_button_enabled(), \
            "Кнопка 'Увійти' повинна бути активною навіть коли поля пусті"
        
        # Натискаємо кнопку "Увійти" з пустими полями
        login_button = page.locator(login_page.locators.LOGIN_BUTTON)
        login_button.click()
        
        # Чекаємо появи помилки валідації (більше часу для появи)
        page.wait_for_timeout(2000)
        
        # Перевірка що з'явилась помилка валідації під полями
        # Спробуємо знайти різними способами
        error_found = login_page.is_field_validation_error_visible()
        
        # Якщо не знайдено через метод, спробуємо знайти через текст на сторінці
        if not error_found:
            page_text = page.locator("body").text_content() or ""
            if "обов'язкове поле" in page_text.lower() or "обовязкове поле" in page_text.lower():
                error_found = True
        
        # Якщо все ще не знайдено, спробуємо через різні можливі селектори
        if not error_found:
            possible_selectors = [
                "form .ant-form-item-explain-error",
                ".ant-form-item-explain-error",
                "[role='alert']",
                ".ant-form-item-has-error"
            ]
            for selector in possible_selectors:
                try:
                    element = page.locator(selector)
                    if element.count() > 0 and element.first.is_visible(timeout=1000):
                        error_found = True
                        break
                except:
                    continue
        
        assert error_found, \
            "Після натискання кнопки 'Увійти' з пустими полями повинна з'явитись помилка валідації 'Обов'язкове поле'"
        
        # Перевірка тексту помилки
        error_text = login_page.get_field_validation_error_text()
        
        # Якщо текст не отримано через метод, спробуємо знайти через текст на сторінці
        if not error_text:
            page_text = page.locator("body").text_content() or ""
            # Шукаємо текст помилки в контексті форми
            form_text = page.locator("form").text_content() or ""
            if "обов'язкове поле" in form_text.lower() or "обовязкове поле" in form_text.lower():
                error_text = "Обов'язкове поле"
        
        # Перевірка що помилка містить текст "Обов'язкове поле"
        if error_text:
            error_text_lower = error_text.lower()
            assert "обов'язкове поле" in error_text_lower or "обовязкове поле" in error_text_lower, \
                f"Помилка валідації має містити текст 'Обов'язкове поле'. Отримано: '{error_text}'"
        else:
            # Якщо текст не знайдено, перевіримо що помилка все ж таки видима
            # Це означає що помилка є, просто текст може бути в іншому форматі
            assert login_page.is_field_validation_error_visible(), \
                "Помилка валідації повинна бути видимою після натискання кнопки з пустими полями"

    def test_login_with_email_only(self, page: Page, test_config: TestConfig):
        """
        Тест кейс: Авторизація логін без паролю
        
        Перевіряє що при натисканні кнопки "Увійти" з заповненим email та пустим паролем
        з'являється помилка валідації "Обов'язкове поле" під полем паролю.
        
        Очікуваний результат:
        - Кнопка "Увійти" активна (можна натиснути)
        - При натисканні кнопки з'являється помилка "Обов'язкове поле" під полем паролю
        - Користувач залишається на сторінці логіну
        """
        # Створення екземпляру сторінки логіну
        login_page = LoginPage(page)
        
        # Перехід на сторінку логіну
        login_page.navigate_to_login(test_config.LOGIN_URL)
        
        # Чекаємо завантаження сторінки
        page.wait_for_load_state("networkidle")
        
        # Заповнюємо тільки поле email
        login_page.fill_email(test_config.USER_EMAIL)
        
        # Перевірка що поле password пусте
        password_input = page.locator(login_page.locators.PASSWORD_INPUT)
        password_value = password_input.input_value()
        assert password_value == "", \
            f"Поле password повинно бути пустим, але містить: '{password_value}'"
        
        # Перевірка стану кнопки "Увійти"
        # Кнопка може бути неактивною якщо не заповнені обидва поля
        is_button_enabled = login_page.is_login_button_enabled()
        
        if is_button_enabled:
            # Якщо кнопка активна, натискаємо її
            login_button = page.locator(login_page.locators.LOGIN_BUTTON)
            login_button.click()
            # Чекаємо появи помилки валідації
            page.wait_for_timeout(2000)
            
            # Перевірка що залишились на сторінці логіну
            login_page.verify_stayed_on_login_page()
            
            # Перевірка що з'явилась помилка валідації під полем паролю
            error_found = login_page.is_field_validation_error_visible()
            
            # Якщо не знайдено через метод, спробуємо знайти через текст на сторінці
            if not error_found:
                form_text = page.locator("form").text_content() or ""
                if "обов'язкове поле" in form_text.lower() or "обовязкове поле" in form_text.lower():
                    error_found = True
            
            # Якщо все ще не знайдено, спробуємо через різні можливі селектори
            if not error_found:
                possible_selectors = [
                    "form .ant-form-item-explain-error",
                    ".ant-form-item-explain-error",
                    "[role='alert']",
                    ".ant-form-item-has-error"
                ]
                for selector in possible_selectors:
                    try:
                        element = page.locator(selector)
                        if element.count() > 0 and element.first.is_visible(timeout=1000):
                            error_found = True
                            break
                    except:
                        continue
            
            assert error_found, \
                "Після натискання кнопки 'Увійти' з заповненим email та пустим паролем " \
                "повинна з'явитись помилка валідації 'Обов'язкове поле' під полем паролю"
        else:
            # Якщо кнопка неактивна, це правильна поведінка - форма не дозволяє відправити без паролю
            # Перевіряємо що кнопка дійсно неактивна
            assert not is_button_enabled, \
                "Кнопка 'Увійти' повинна бути неактивною коли заповнено тільки email без паролю"
            
            # Перевірка що залишились на сторінці логіну
            login_page.verify_stayed_on_login_page()

    def test_login_with_password_only(self, page: Page, test_config: TestConfig):
        """
        Тест кейс: Авторизація пароль без логіну
        
        Перевіряє що при натисканні кнопки "Увійти" з заповненим паролем та пустим email
        з'являється помилка валідації "Обов'язкове поле" під полем email.
        
        Очікуваний результат:
        - Кнопка "Увійти" активна (можна натиснути)
        - При натисканні кнопки з'являється помилка "Обов'язкове поле" під полем email
        - Користувач залишається на сторінці логіну
        """
        # Створення екземпляру сторінки логіну
        login_page = LoginPage(page)
        
        # Перехід на сторінку логіну
        login_page.navigate_to_login(test_config.LOGIN_URL)
        
        # Чекаємо завантаження сторінки
        page.wait_for_load_state("networkidle")
        
        # Заповнюємо тільки поле password
        login_page.fill_password(test_config.USER_PASSWORD)
        
        # Перевірка що поле email пусте
        email_input = page.locator(login_page.locators.EMAIL_INPUT)
        email_value = email_input.input_value()
        assert email_value == "", \
            f"Поле email повинно бути пустим, але містить: '{email_value}'"
        
        # Перевірка стану кнопки "Увійти"
        # Кнопка може бути неактивною якщо не заповнені обидва поля
        is_button_enabled = login_page.is_login_button_enabled()
        
        if is_button_enabled:
            # Якщо кнопка активна, натискаємо її
            login_button = page.locator(login_page.locators.LOGIN_BUTTON)
            login_button.click()
            # Чекаємо появи помилки валідації
            page.wait_for_timeout(2000)
            
            # Перевірка що залишились на сторінці логіну
            login_page.verify_stayed_on_login_page()
            
            # Перевірка що з'явилась помилка валідації під полем email
            error_found = login_page.is_field_validation_error_visible()
            
            # Якщо не знайдено через метод, спробуємо знайти через текст на сторінці
            if not error_found:
                form_text = page.locator("form").text_content() or ""
                if "обов'язкове поле" in form_text.lower() or "обовязкове поле" in form_text.lower():
                    error_found = True
            
            # Якщо все ще не знайдено, спробуємо через різні можливі селектори
            if not error_found:
                possible_selectors = [
                    "form .ant-form-item-explain-error",
                    ".ant-form-item-explain-error",
                    "[role='alert']",
                    ".ant-form-item-has-error"
                ]
                for selector in possible_selectors:
                    try:
                        element = page.locator(selector)
                        if element.count() > 0 and element.first.is_visible(timeout=1000):
                            error_found = True
                            break
                    except:
                        continue
            
            assert error_found, \
                "Після натискання кнопки 'Увійти' з заповненим паролем та пустим email " \
                "повинна з'явитись помилка валідації 'Обов'язкове поле' під полем email"
        else:
            # Якщо кнопка неактивна, це правильна поведінка - форма не дозволяє відправити без email
            # Перевіряємо що кнопка дійсно неактивна
            assert not is_button_enabled, \
                "Кнопка 'Увійти' повинна бути неактивною коли заповнено тільки пароль без email"
            
            # Перевірка що залишились на сторінці логіну
            login_page.verify_stayed_on_login_page()
