"""
Page Object для сторінки логіну.
Містить методи для роботи зі сторінкою логіну.
"""
from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from locators.login_locators import LoginLocators


class LoginPage(BasePage):
    """Page Object для сторінки логіну"""
    
    def __init__(self, page: Page):
        """
        Ініціалізація сторінки логіну
        
        Args:
            page: Екземпляр Playwright Page
        """
        super().__init__(page)
        self.locators = LoginLocators()
    
    def navigate_to_login(self, login_url: str):
        """
        Перехід на сторінку логіну
        
        Args:
            login_url: URL сторінки логіну
        """
        self.goto(login_url)
    
    def fill_email(self, email: str):
        """
        Заповнити поле email
        
        Args:
            email: Email для логіну
        """
        email_input = self.page.locator(self.locators.EMAIL_INPUT)
        email_input.fill(email)
    
    def fill_password(self, password: str):
        """
        Заповнити поле паролю
        
        Args:
            password: Пароль для логіну
        """
        password_input = self.page.locator(self.locators.PASSWORD_INPUT)
        password_input.fill(password)
    
    def click_login_button(self):
        """Натиснути кнопку входу та очікувати навігацію"""
        login_button = self.page.locator(self.locators.LOGIN_BUTTON)
        with self.page.expect_navigation(timeout=15000):
            login_button.click()
    
    def click_login_button_without_navigation(self):
        """Натиснути кнопку входу без очікування навігації (для негативних тестів)"""
        login_button = self.page.locator(self.locators.LOGIN_BUTTON)
        login_button.click()
        # Чекаємо трохи для появи повідомлення про помилку
        self.page.wait_for_timeout(1000)
    
    def login(self, email: str, password: str):
        """
        Виконати повний процес логіну
        
        Args:
            email: Email для логіну
            password: Пароль для логіну
        """
        self.fill_email(email)
        self.fill_password(password)
        self.click_login_button()
        self.wait_for_load_state("networkidle")
    
    def attempt_login(self, email: str, password: str):
        """
        Спробувати виконати логін без очікування навігації (для негативних тестів)
        
        Args:
            email: Email для логіну
            password: Пароль для логіну
        """
        self.fill_email(email)
        self.fill_password(password)
        self.click_login_button_without_navigation()
    
    def verify_successful_login(self, expected_url: str = None):
        """
        Перевірити успішний логін
        
        Args:
            expected_url: Очікуваний URL після логіну (опціонально)
        """
        if expected_url:
            expect(self.page).to_have_url(expected_url, timeout=5000)
        else:
            # Перевірка що ми не залишились на сторінці логіну
            current_url = self.get_url()
            assert "/user/login" not in current_url, \
                f"Логін не відбувся, залишились на сторінці: {current_url}"
    
    def verify_stayed_on_login_page(self):
        """
        Перевірити що залишились на сторінці логіну (для негативних тестів)
        """
        current_url = self.get_url()
        assert "/user/login" in current_url, \
            f"Очікувалось залишитись на сторінці логіну, але перейшли на: {current_url}"
    
    def is_error_message_visible(self) -> bool:
        """
        Перевірити чи видиме повідомлення про помилку (alert)
        
        Returns:
            True якщо повідомлення про помилку видиме
        """
        try:
            error_alert = self.page.locator(self.locators.ERROR_ALERT)
            return error_alert.is_visible(timeout=3000)
        except:
            return False
    
    def get_error_message_text(self) -> str:
        """
        Отримати текст повідомлення про помилку з alert
        
        Returns:
            Текст повідомлення про помилку
        """
        try:
            error_alert = self.page.locator(self.locators.ERROR_ALERT)
            if error_alert.is_visible(timeout=2000):
                return error_alert.text_content() or ""
        except:
            pass
        return ""
    
    def verify_error_message_contains(self, expected_text: str):
        """
        Перевірити що повідомлення про помилку містить очікуваний текст
        
        Args:
            expected_text: Очікуваний текст в повідомленні про помилку
        """
        assert self.is_error_message_visible(), \
            "Повідомлення про помилку має бути видиме"
        
        error_text = self.get_error_message_text()
        assert expected_text.lower() in error_text.lower(), \
            f"Повідомлення про помилку має містити '{expected_text}', але отримано: '{error_text}'"
    
    def is_login_button_enabled(self) -> bool:
        """
        Перевірити чи кнопка входу активна (enabled)
        
        Returns:
            True якщо кнопка активна, False якщо неактивна (disabled)
        """
        try:
            login_button = self.page.locator(self.locators.LOGIN_BUTTON)
            return login_button.is_enabled()
        except:
            return False
    
    def is_field_validation_error_visible(self) -> bool:
        """
        Перевірити чи видима помилка валідації під полями (Обов'язкове поле)
        
        Returns:
            True якщо помилка валідації видима
        """
        try:
            # Спробуємо знайти через клас Ant Design
            validation_error = self.page.locator(self.locators.FIELD_VALIDATION_ERROR)
            if validation_error.is_visible(timeout=2000):
                return True
        except:
            pass
        
        # Якщо не знайдено через клас, спробуємо через текст
        try:
            text_locator = self.page.locator("text=Обов'язкове поле")
            if text_locator.is_visible(timeout=2000):
                return True
        except:
            pass
        
        # Також спробуємо альтернативний варіант тексту
        try:
            text_locator = self.page.locator("text=Обовязкове поле")
            if text_locator.is_visible(timeout=2000):
                return True
        except:
            pass
        
        return False
    
    def get_field_validation_error_text(self) -> str:
        """
        Отримати текст помилки валідації під полями
        
        Returns:
            Текст помилки валідації
        """
        # Спочатку спробуємо через клас
        try:
            validation_error = self.page.locator(self.locators.FIELD_VALIDATION_ERROR)
            if validation_error.is_visible(timeout=2000):
                return validation_error.text_content() or ""
        except:
            pass
        
        # Якщо не знайдено, спробуємо через текстовий локатор
        try:
            text_locator = self.page.locator("text=Обов'язкове поле")
            if text_locator.is_visible(timeout=2000):
                return text_locator.text_content() or ""
        except:
            pass
        
        # Альтернативний варіант
        try:
            text_locator = self.page.locator("text=Обовязкове поле")
            if text_locator.is_visible(timeout=2000):
                return text_locator.text_content() or ""
        except:
            pass
        
        return ""
    
    def verify_error_messages(self, expected_texts: list):
        """
        Перевірити що повідомлення про помилку містить всі очікувані тексти
        
        Args:
            expected_texts: Список очікуваних текстів в повідомленні про помилку
        """
        # Чекаємо трохи більше для появи повідомлення
        self.page.wait_for_timeout(2000)
        
        # Спробуємо знайти через різні локатори (notification, alert, error message)
        found_texts = []
        page_text = self.page.locator("body").text_content().lower()
        
        # Також перевіряємо через різні можливі селектори
        possible_selectors = [
            ".ant-message",
            ".ant-notification",
            ".error-message",
            ".alert",
            "[role='alert']",
            ".notification",
            ".toast"
        ]
        
        for selector in possible_selectors:
            try:
                element = self.page.locator(selector)
                if element.count() > 0:
                    element_text = element.text_content().lower()
                    page_text += " " + element_text
            except:
                pass
        
        # Перевіряємо наявність очікуваних текстів
        for expected_text in expected_texts:
            if expected_text.lower() in page_text:
                found_texts.append(expected_text)
            else:
                # Спробуємо знайти через текстовий локатор
                try:
                    text_locator = self.page.locator(f"text={expected_text}")
                    if text_locator.count() > 0:
                        found_texts.append(expected_text)
                except:
                    pass
        
        # Перевірка що всі тексти знайдені
        missing_texts = [text for text in expected_texts if text not in found_texts]
        if missing_texts:
            # Виводимо більше інформації для дебагу
            visible_text = self.page.locator("body").text_content()[:500]
            assert False, \
                f"Не знайдено очікувані тексти: {missing_texts}. " \
                f"Знайдено: {found_texts}. " \
                f"Видимий текст на сторінці: {visible_text}"
