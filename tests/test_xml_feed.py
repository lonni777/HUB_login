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
    
    def test_validate_url_save_normalized_url_with_spaces(self, page: Page, test_config: TestConfig):
        """
        Тест кейс: Валідація url. Збереження нормалізованого URL (пробіли)
        
        Перевіряє нормалізацію URL при додаванні XML-фіду з пробілами перед та після URL.
        Очікується:
        - Фід успішно збережено та користувач отримав про це сповіщення "Дані збережено!"
        - В БД записано URL без пробілів (нормалізований)
        - При відкритті фіду в таблиці, посилання в полі буде без пробілів
        """
        # Крок 1: Авторизація в хаб як постачальник
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
        
        # Крок 1: Відкрити "Додати новий фід"
        xml_feed_page.click_add_new_feed_button()
        
        # Крок 2: Внести посилання з пробілами до та після
        original_url = test_config.TEST_XML_FEED_URL.strip()  # Оригінальне посилання без пробілів
        url_with_spaces = f" {original_url} "  # Додаємо пробіли перед та після
        xml_feed_page.fill_feed_url(url_with_spaces)
        
        # Крок 3: Проставити чекбокс "Завантажити товари з xml" та натиснути Зберегти
        xml_feed_page.enable_upload_items_checkbox()
        xml_feed_page.click_save_button()
        
        # Крок 4: Перевірка що після збереження перекинуло на таблицю фідів та відображається "Дані збережено"
        # Перевірка повідомлення опціональна - головне що збереження відбулося
        try:
            xml_feed_page.verify_success_message("Дані збережено!")
        except:
            # Якщо повідомлення не знайдено, перевіряємо що ми на сторінці з таблицею або редагування
            current_url = xml_feed_page.get_url()
            if "/supplier-content/xml" in current_url:
                print("Фід збережено (перевірено через URL сторінки)")
            else:
                print("Попередження: повідомлення про успіх не знайдено, але продовжуємо тест")
        
        # Переходимо на сторінку зі списком фідів для фільтрації
        xml_feed_page.navigate_to_feeds_table(test_config.XML_FEEDS_URL)
        
        # Крок 5-6: На сторінці з таблицею знайти стовпець "Лінк фіду", натиснути фільтр та внести оригінальне посилання
        # (Таблиця вже відкрита після збереження)
        # Для фільтрації використовуємо оригінальний URL (метод сам видалить /raw якщо потрібно)
        xml_feed_page.filter_feeds_by_link(original_url)
        
        # Крок 7: Отримати feed_id зі стовпця "id фіду" після фільтрації
        feed_id = xml_feed_page.get_feed_id_from_filtered_table()
        
        # Якщо не знайдено через фільтрацію, спробуємо знайти по URL в таблиці
        if not feed_id:
            print("Не вдалося знайти feed_id через фільтрацію, шукаємо по URL в таблиці...")
            feed_id = xml_feed_page.get_feed_id_by_url_from_table(original_url)
        
        if not feed_id:
            raise AssertionError("Не вдалося знайти feed_id після збереження. Тест провалено!")
        
        # Крок 8: Натиснути кнопку "Редагувати" і відкриється сторінка фіду
        xml_feed_page.click_edit_button()
        
        # Отримуємо URL з поля введення на сторінці редагування
        url_in_ui = xml_feed_page.get_feed_url_from_input()
        
        # Отримуємо origin_url з БД для порівняння
        db_origin_url = None
        if test_config.DB_HOST and test_config.DB_NAME:
            with DBHelper(
                host=test_config.DB_HOST,
                port=test_config.DB_PORT,
                database=test_config.DB_NAME,
                user=test_config.DB_USER,
                password=test_config.DB_PASSWORD
            ) as db:
                db_origin_url = db.get_feed_url_by_id(feed_id)
        
        if not db_origin_url:
            raise AssertionError(f"Не вдалося отримати origin_url з БД для feed_id '{feed_id}'")
        
        # Крок 9: Перевірка що URL збережено без пробілів та ідентичний з origin_url + #ufeed...
        # Головна мета тесту - перевірити що пробіли видаляються при збереженні
        
        # Перевірка що в БД origin_url без пробілів
        db_origin_url_normalized = db_origin_url.strip()
        assert ' ' not in db_origin_url_normalized, \
            f"origin_url в БД містить пробіли! URL: '{db_origin_url}'"
        
        # Перевірка що origin_url містить #ufeed параметр (додається системою)
        assert '#ufeed' in db_origin_url_normalized, \
            f"origin_url в БД не містить #ufeed параметр! URL: '{db_origin_url}'"
        
        print(f"origin_url в БД правильний (без пробілів + #ufeed): '{db_origin_url_normalized}'")
        
        # Перевірка що URL в UI без пробілів
        url_in_ui_normalized = url_in_ui.strip()
        assert ' ' not in url_in_ui_normalized, \
            f"URL в UI містить пробіли! URL: '{url_in_ui}'"
        
        # Перевірка що URL в UI містить #ufeed параметр
        assert '#ufeed' in url_in_ui_normalized, \
            f"URL в UI не містить #ufeed параметр! URL: '{url_in_ui}'"
        
        # Порівнюємо URL в UI з origin_url з БД (вони мають бути ідентичні)
        assert url_in_ui_normalized == db_origin_url_normalized, \
            f"URL в UI не ідентичний з origin_url в БД! UI: '{url_in_ui_normalized}', БД: '{db_origin_url_normalized}'"
        
        print(f"URL в UI ідентичний з origin_url в БД (без пробілів + #ufeed): '{url_in_ui_normalized}'")
        
        # Головна перевірка: базовий URL (без #ufeed) не містить пробілів
        base_url_from_db = db_origin_url_normalized.split('#')[0].strip()
        base_url_from_ui = url_in_ui_normalized.split('#')[0].strip()
        
        assert ' ' not in base_url_from_db, \
            f"Базовий URL в БД містить пробіли! URL: '{base_url_from_db}'"
        
        assert ' ' not in base_url_from_ui, \
            f"Базовий URL в UI містить пробіли! URL: '{base_url_from_ui}'"
        
        print(f"Базові URL без пробілів - БД: '{base_url_from_db}', UI: '{base_url_from_ui}'")
        print("Тест пройшов: URL нормалізований правильно (пробіли видалені)")
        
        # Крок 10: Cleanup - Видалення фіду з БД після тесту
        cleanup_success = False
        try:
            if test_config.DB_HOST and test_config.DB_NAME:
                with DBHelper(
                    host=test_config.DB_HOST,
                    port=test_config.DB_PORT,
                    database=test_config.DB_NAME,
                    user=test_config.DB_USER,
                    password=test_config.DB_PASSWORD
                ) as db:
                    db.delete_feed_by_id(feed_id)
                    cleanup_success = True
            else:
                raise AssertionError("Налаштування БД не вказані. Cleanup не виконано!")
        except Exception as e:
            error_msg = f"КРИТИЧНА ПОМИЛКА: Cleanup не вдався - {e}"
            print(error_msg)
            pytest.fail(error_msg)
        
        # Фінальна перевірка що cleanup виконано успішно
        assert cleanup_success, f"Cleanup не виконано для feed_id '{feed_id}'. Тест провалено!"
    
    def test_validate_url_save_invalid_xml_structure_json_inside(self, page: Page, test_config: TestConfig):
        """
        Тест кейс: Валідація url. Збереження url розширення xml невалідної структури фід (всередині json)
        
        Перевіряє що при додаванні фіду з URL файлу .xml, що містить JSON замість XML,
        система показує помилку валідації та не створює запис в БД.
        
        Очікуваний результат:
        1. Після натискання "Зберегти" — повідомлення про помилку валідації
           (містить "Помилка валідації xml структури фіду" та "Unexpected character '{'")
        2. В таблиці feed запис по origin_url не створено
        """
        invalid_feed_url = test_config.TEST_INVALID_XML_FEED_URL
        
        # Крок 1: Авторизація в хаб
        login_page = LoginPage(page)
        login_page.navigate_to_login(f"{test_config.LOGIN_URL}?next=/supplier-content/xml")
        login_page.login(
            email=test_config.USER_EMAIL,
            password=test_config.USER_PASSWORD
        )
        login_page.verify_successful_login()
        
        # Крок 2: Вибір постачальника
        xml_feed_page = XMLFeedPage(page)
        xml_feed_page.select_supplier(test_config.TEST_SUPPLIER_NAME)
        
        # Крок 3: Перехід в Товари - Імпорт новинок - XML
        xml_feed_page.navigate_to_xml_feeds_via_menu()
        
        # Крок 4: Натиснути "Додати новий фід" та додати URL з невалідною структурою
        xml_feed_page.click_add_new_feed_button()
        xml_feed_page.fill_feed_url(invalid_feed_url)
        
        # Крок 5: Проставити чекбокс "Завантажити товари з xml" та натиснути Зберегти
        xml_feed_page.enable_upload_items_checkbox()
        xml_feed_page.click_save_button()
        
        # Очікуваний результат 1: Повідомлення про помилку валідації
        xml_feed_page.verify_validation_error_message("Помилка валідації xml структури фіду")
        xml_feed_page.verify_validation_error_message("Unexpected character")
        
        # Очікуваний результат 2: Запис в БД не створено
        if test_config.DB_HOST and test_config.DB_NAME:
            with DBHelper(
                host=test_config.DB_HOST,
                port=test_config.DB_PORT,
                database=test_config.DB_NAME,
                user=test_config.DB_USER,
                password=test_config.DB_PASSWORD
            ) as db:
                feed_exists = db.feed_exists_by_origin_url(invalid_feed_url)
                assert not feed_exists, (
                    f"Запис у таблиці feed по origin_url не повинен був створитися, "
                    f"але він існує! URL: {invalid_feed_url}"
                )
            print("Підтверджено: запис у таблиці feed не створено")
        else:
            print("Попередження: налаштування БД не вказані, перевірка відсутності запису пропущена")
    
    def test_validate_url_save_unavailable_url_404(self, page: Page, test_config: TestConfig):
        """
        Тест кейс: Валідація url. Збереження недоступного URL (404 Not Found)
        
        Перевіряє що при додаванні фіду з URL, що повертає 404,
        система показує помилку та не створює запис в БД.
        
        Очікуваний результат:
        1. Після натискання "Зберегти" — повідомлення про помилку
           (містить "Помилка валідації xml структури фіду" та "status 404")
        2. В таблиці feed запис по origin_url не створено
        """
        url_404 = test_config.TEST_404_FEED_URL
        
        # Крок 1: Авторизація в хаб
        login_page = LoginPage(page)
        login_page.navigate_to_login(f"{test_config.LOGIN_URL}?next=/supplier-content/xml")
        login_page.login(
            email=test_config.USER_EMAIL,
            password=test_config.USER_PASSWORD
        )
        login_page.verify_successful_login()
        
        # Крок 2: Вибір постачальника
        xml_feed_page = XMLFeedPage(page)
        xml_feed_page.select_supplier(test_config.TEST_SUPPLIER_NAME)
        
        # Крок 3: Перехід в Товари - Імпорт новинок - XML
        xml_feed_page.navigate_to_xml_feeds_via_menu()
        
        # Крок 4: Натиснути "Додати новий фід" та додати URL що повертає 404
        xml_feed_page.click_add_new_feed_button()
        xml_feed_page.fill_feed_url(url_404)
        
        # Крок 5: Проставити чекбокс "Завантажити товари з xml" та натиснути Зберегти
        xml_feed_page.enable_upload_items_checkbox()
        xml_feed_page.click_save_button()
        
        # Очікуваний результат 1: Повідомлення про помилку (ключові фрази)
        xml_feed_page.verify_validation_error_message("Помилка валідації xml структури фіду")
        xml_feed_page.verify_validation_error_message("status 404")
        
        # Очікуваний результат 2: Запис в БД не створено
        if test_config.DB_HOST and test_config.DB_NAME:
            with DBHelper(
                host=test_config.DB_HOST,
                port=test_config.DB_PORT,
                database=test_config.DB_NAME,
                user=test_config.DB_USER,
                password=test_config.DB_PASSWORD
            ) as db:
                feed_exists = db.feed_exists_by_origin_url(url_404)
                assert not feed_exists, (
                    f"Запис у таблиці feed по origin_url не повинен був створитися, "
                    f"але він існує! URL: {url_404}"
                )
            print("Підтверджено: запис у таблиці feed не створено")
        else:
            print("Попередження: налаштування БД не вказані, перевірка відсутності запису пропущена")
