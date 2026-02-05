"""
Тести для функціоналу XML-фідів.
Містить тест-кейси для додавання та валідації XML-фідів.
"""
import pytest
from playwright.sync_api import Page
from config.settings import TestConfig
from pages.xml_feed_page import XMLFeedPage
from pages.login_page import LoginPage
from utils.db_helper import DBHelper


class TestXMLFeed:
    """Тест сьют: XML-фіди - Додавання та валідація"""
    
    def test_validate_url_save_valid_url_without_spaces(self, page: Page, test_config: TestConfig):
        """
        Тест кейс: Валідація url. Збереження валідного URL (без пробілів)
        
        Перевіряє успішне додавання XML-фіду з валідним URL без пробілів.
        Очікується:
        - Фід успішно збережено та користувач отримав про це сповіщення "Дані збережено!"
        """
        # Крок 1: Авторизація в хаб
        login_page = LoginPage(page)
        login_page.navigate_to_login(f"{test_config.LOGIN_URL}?next=/supplier-content/xml")
        login_page.login(
            email=test_config.USER_EMAIL,
            password=test_config.USER_PASSWORD
        )
        login_page.verify_successful_login()
        
        # Крок 2: Вибір постачальника "Braggart"
        xml_feed_page = XMLFeedPage(page)
        xml_feed_page.select_supplier(test_config.TEST_SUPPLIER_NAME)
        
        # Крок 3: Перехід в Товари - Імпорт новинок - XML
        xml_feed_page.navigate_to_xml_feeds_via_menu()
        
        # Крок 4: Натиснути "Додати новий фід" та додати валідний URL
        xml_feed_page.click_add_new_feed_button()
        xml_feed_page.fill_feed_url(test_config.TEST_XML_FEED_URL)
        
        # Крок 5: В налаштуваннях включити чекбокс "Завантажити товари з xml" та натиснути Зберегти
        xml_feed_page.enable_upload_items_checkbox()
        xml_feed_page.click_save_button()
        
        # Очікуваний результат: Фід успішно збережено та користувач отримав про це сповіщення
        xml_feed_page.verify_success_message("Дані збережено!")
        
        # Cleanup: Видалення фіду з БД після тесту для можливості повторного запуску
        # ВАЖЛИВО: Cleanup є критичним - без видалення фіду тест не можна буде запустити повторно
        feed_id = None
        cleanup_success = False
        
        try:
            # Переходимо на сторінку зі списком фідів
            xml_feed_page.navigate_to_feeds_table(test_config.XML_FEEDS_URL)
            
            # Знаходимо feed_id по URL фіду
            feed_id = xml_feed_page.get_feed_id_by_url_from_table(test_config.TEST_XML_FEED_URL)
            
            if not feed_id:
                raise AssertionError("Не вдалося знайти feed_id для видалення. Cleanup не виконано!")
            
            if not (test_config.DB_HOST and test_config.DB_NAME):
                raise AssertionError("Налаштування БД не вказані. Cleanup не виконано!")
            
            # Видаляємо фід з БД (спочатку фото, потім сам фід)
            with DBHelper(
                host=test_config.DB_HOST,
                port=test_config.DB_PORT,
                database=test_config.DB_NAME,
                user=test_config.DB_USER,
                password=test_config.DB_PASSWORD
            ) as db:
                db.delete_feed_by_id(feed_id)
                cleanup_success = True
                
        except Exception as e:
            error_msg = f"КРИТИЧНА ПОМИЛКА: Cleanup не вдався - {e}"
            print(error_msg)
            # Cleanup є критичним - провалюємо тест якщо не вдався
            pytest.fail(error_msg)
        
        # Фінальна перевірка що cleanup виконано успішно
        assert cleanup_success, f"Cleanup не виконано для feed_id '{feed_id}'. Тест провалено!"
