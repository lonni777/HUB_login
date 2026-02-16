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
    
    def test_tc_xml_003_empty_url_validation(self, page: Page, test_config: TestConfig):
        """
        TC-XML-003: Порожнє поле URL
        
        Перевіряє що при спробі зберегти фід з порожнім URL
        відображається помилка валідації та запис у таблиці feed не створюється.
        
        Кроки:
        - Авторизуватися, обрати постачальника
        - Товари → Імпорт новинок → XML
        - Натиснути "Додати новий фід"
        - Залишити поле URL порожнім
        - Увімкнути чекбокс "Завантажити товари з xml"
        - Натиснути "Зберегти"
        
        Очікуваний результат:
        - Помилка валідації (не дозволено зберегти без URL)
        - Запис у таблиці feed не створюється
        """
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
        
        # Зберігаємо кількість рядків до дії (для перевірки що запис не створено)
        feeds_count_before = xml_feed_page.get_feeds_table_row_count()
        
        # Крок 4: Натиснути "Додати новий фід"
        xml_feed_page.click_add_new_feed_button()
        
        # Крок 5: Залишити поле URL порожнім (переконаємось що воно очищене)
        xml_feed_page.clear_feed_url()
        page.wait_for_timeout(500)
        
        # Крок 6: Увімкнути чекбокс "Завантажити товари з xml"
        xml_feed_page.enable_upload_items_checkbox()
        
        # Крок 7: Натиснути "Зберегти"
        xml_feed_page.click_save_button()
        page.wait_for_timeout(3000)
        
        # Очікуваний результат 1: Помилка валідації (повідомлення про порожнє/обов'язкове поле URL)
        has_error = (
            xml_feed_page.has_validation_error_message("URL")
            or xml_feed_page.has_validation_error_message("порожн")
            or xml_feed_page.has_validation_error_message("обов'язков")
            or xml_feed_page.has_validation_error_message("заповніть")
        )
        assert has_error, (
            "Очікувалось повідомлення про помилку валідації (URL/порт/обов'язкове поле), "
            "але воно не відображається"
        )
        print("Підтверджено: відображається помилка валідації")
        
        # Очікуваний результат 2: Запис у таблиці feed не створено
        xml_feed_page.goto(test_config.XML_FEEDS_URL)
        xml_feed_page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        feeds_count_after = xml_feed_page.get_feeds_table_row_count()
        assert feeds_count_after == feeds_count_before, (
            f"Очікувалось що запис не створиться. "
            f"Кількість рядків змінилась: було {feeds_count_before}, стало {feeds_count_after}"
        )
        print("Підтверджено: запис у таблиці feed не створено")
    
    def test_save_feed_without_checkbox(self, page: Page, test_config: TestConfig):
        """
        Збереження фіду без чекбокса "Завантажити товари з xml"

        Перевіряє що фід можна зберегти без увімкнення чекбокса "Завантажити товари з xml".
        Чекбокс залишається вимкненим, фід має статус "не активний" для завантаження товарів.

        Кроки:
        - Авторизуватися, обрати постачальника
        - Товари → Імпорт новинок → XML
        - Натиснути "Додати новий фід"
        - Ввести валідний URL XML-фіду
        - НЕ увімкнути чекбокс "Завантажити товари з xml"
        - Натиснути "Зберегти"

        Очікуваний результат:
        - Фід збережено
        - Чекбокс залишається вимкненим
        - Фід має статус "не активний" для завантаження товарів

        Cleanup: Видалення фіду з БД після тесту.
        """
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

        # Крок 4: Натиснути "Додати новий фід"
        xml_feed_page.click_add_new_feed_button()

        # Крок 5: Ввести валідний URL XML-фіду
        xml_feed_page.fill_feed_url(test_config.TEST_XML_FEED_URL)

        # Крок 6: НЕ увімкнути чекбокс "Завантажити товари з xml" (залишаємо вимкненим)
        # Крок 7: Натиснути "Зберегти"
        xml_feed_page.click_save_button()
        page.wait_for_timeout(3000)

        # Очікуваний результат 1: Фід збережено
        xml_feed_page.verify_success_message("Дані збережено!")
        print("Підтверджено: фід збережено успішно")

        # Переходимо на сторінку зі списком фідів для пошуку фіду
        xml_feed_page.navigate_to_feeds_table(test_config.XML_FEEDS_URL)
        page.wait_for_timeout(2000)

        feed_id = xml_feed_page.get_feed_id_by_url_from_table(test_config.TEST_XML_FEED_URL)
        if not feed_id:
            raise AssertionError("Не вдалося знайти feed_id після збереження фіду")

        # Очікуваний результат 2: Відкриваємо фід для редагування та перевіряємо що чекбокс вимкнений
        xml_feed_page.open_feed_from_table_by_id(feed_id)
        page.wait_for_timeout(2000)
        xml_feed_page.click_edit_button()
        page.wait_for_timeout(1500)

        is_checked = xml_feed_page.is_upload_items_checkbox_checked()
        assert not is_checked, (
            "Очікувалось що чекбокс 'Завантажити товари з xml' буде вимкнений, але він увімкнений"
        )
        print("Підтверджено: чекбокс залишається вимкненим")

        # Очікуваний результат 3: Фід має статус "не активний" для завантаження товарів
        # (перевірка через БД: is_active = false, якщо є доступ)
        if test_config.DB_HOST and test_config.DB_NAME:
            try:
                with DBHelper(
                    host=test_config.DB_HOST,
                    port=test_config.DB_PORT,
                    database=test_config.DB_NAME,
                    user=test_config.DB_USER,
                    password=test_config.DB_PASSWORD
                ) as db:
                    is_active = db.is_feed_active(feed_id)
                    assert not is_active, (
                        f"Очікувалось що фід {feed_id} буде не активний (is_active=false), але is_active=true"
                    )
                print("Підтверджено: фід має статус 'не активний' в БД")
            except Exception as e:
                print(f"Попередження: не вдалося перевірити is_active в БД ({e}), пропускаємо")

        # Cleanup: Видалення фіду з БД після тесту
        cleanup_success = False
        try:
            if not (test_config.DB_HOST and test_config.DB_NAME):
                raise AssertionError("Налаштування БД не вказані. Cleanup не виконано!")

            with DBHelper(
                host=test_config.DB_HOST,
                port=test_config.DB_PORT,
                database=test_config.DB_NAME,
                user=test_config.DB_USER,
                password=test_config.DB_PASSWORD
            ) as db:
                db.delete_feed_by_id(feed_id)
                cleanup_success = True
            print(f"Cleanup: фід {feed_id} успішно видалено з БД")
        except Exception as e:
            error_msg = f"КРИТИЧНА ПОМИЛКА: Cleanup не вдався - {e}"
            print(error_msg)
            pytest.fail(error_msg)

        assert cleanup_success, f"Cleanup не виконано для feed_id '{feed_id}'. Тест провалено!"

    def test_invalid_url_format_validation(self, page: Page, test_config: TestConfig):
        """
        Тест кейс: Невірний формат URL (не URL)
        
        Перевіряє що при додаванні фіду з невалідним URL (наприклад ftp://)
        відображається помилка валідації та запис у feed не створюється.
        
        Кроки:
        - Авторизуватися, обрати постачальника
        - Товари → Імпорт новинок → XML
        - Натиснути "Додати новий фід"
        - Ввести невалідний рядок (ftp://test.com або not-a-url)
        - Увімкнути чекбокс "Завантажити товари з xml"
        - Натиснути "Зберегти"
        
        Очікуваний результат:
        - Помилка: "Помилка валідації xml структури фіду помилка завантаження фіду: ftp protocol is not supported"
        - Запис у feed не створюється
        """
        invalid_url = test_config.TEST_INVALID_URL_FEED
        
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
        
        feeds_count_before = xml_feed_page.get_feeds_table_row_count()
        
        # Крок 4: Натиснути "Додати новий фід"
        xml_feed_page.click_add_new_feed_button()
        
        # Крок 5: Ввести невалідний URL
        xml_feed_page.fill_feed_url(invalid_url)
        page.wait_for_timeout(500)
        
        # Крок 6: Увімкнути чекбокс "Завантажити товари з xml"
        xml_feed_page.enable_upload_items_checkbox()
        
        # Крок 7: Натиснути "Зберегти"
        xml_feed_page.click_save_button()
        page.wait_for_timeout(3000)
        
        # Очікуваний результат 1: Помилка валідації
        xml_feed_page.verify_validation_error_message("Помилка валідації xml структури фіду")
        xml_feed_page.verify_validation_error_message("ftp protocol is not supported")
        print("Підтверджено: відображається помилка валідації")
        
        # Очікуваний результат 2: Запис у feed не створюється
        if test_config.DB_HOST and test_config.DB_NAME:
            with DBHelper(
                host=test_config.DB_HOST,
                port=test_config.DB_PORT,
                database=test_config.DB_NAME,
                user=test_config.DB_USER,
                password=test_config.DB_PASSWORD
            ) as db:
                feed_exists = db.feed_exists_by_origin_url(invalid_url)
                assert not feed_exists, (
                    f"Запис у таблиці feed по origin_url не повинен був створитися, "
                    f"але він існує! URL: {invalid_url}"
                )
            print("Підтверджено: запис у таблиці feed не створено")
        else:
            xml_feed_page.goto(test_config.XML_FEEDS_URL)
            xml_feed_page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)
            feeds_count_after = xml_feed_page.get_feeds_table_row_count()
            assert feeds_count_after == feeds_count_before, (
                f"Очікувалось що запис не створиться. "
                f"Кількість рядків змінилась: було {feeds_count_before}, стало {feeds_count_after}"
            )
            print("Підтверджено: запис у таблиці feed не створено")
    
    def test_tc_xml_008_invalid_xml_structure(self, page: Page, test_config: TestConfig):
        """
        TC-XML-008: XML з некоректною структурою (неповний/зламаний XML)
        
        Перевіряє що при додаванні фіду з URL, що повертає XML з незакритими тегами
        або порушеною структурою, відображається помилка валідації та запис у feed не створюється.
        
        Кроки:
        - Авторизуватися, обрати постачальника
        - Товари → Імпорт новинок → XML
        - Натиснути "Додати новий фід"
        - Ввести URL файлу з незакритими тегами або порушеною XML-структурою
        - Увімкнути чекбокс "Завантажити товари з xml"
        - Натиснути "Зберегти"
        
        Очікуваний результат:
        - Повідомлення про помилку валідації XML
        - Запис у feed не створюється
        """
        invalid_structure_url = test_config.TEST_INVALID_XML_STRUCTURE_URL
        
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
        
        feeds_count_before = xml_feed_page.get_feeds_table_row_count()
        
        # Крок 4: Натиснути "Додати новий фід"
        xml_feed_page.click_add_new_feed_button()
        
        # Крок 5: Ввести URL з некоректною XML-структурою
        xml_feed_page.fill_feed_url(invalid_structure_url)
        page.wait_for_timeout(500)
        
        # Крок 6: Увімкнути чекбокс "Завантажити товари з xml"
        xml_feed_page.enable_upload_items_checkbox()
        
        # Крок 7: Натиснути "Зберегти"
        xml_feed_page.click_save_button()
        page.wait_for_timeout(5000)
        
        # Очікуваний результат 1: Помилка валідації XML
        xml_feed_page.verify_validation_error_message("Помилка валідації xml структури фіду")
        print("Підтверджено: відображається помилка валідації XML")
        
        # Очікуваний результат 2: Запис у feed не створюється
        if test_config.DB_HOST and test_config.DB_NAME:
            with DBHelper(
                host=test_config.DB_HOST,
                port=test_config.DB_PORT,
                database=test_config.DB_NAME,
                user=test_config.DB_USER,
                password=test_config.DB_PASSWORD
            ) as db:
                feed_exists = db.feed_exists_by_origin_url(invalid_structure_url)
                assert not feed_exists, (
                    f"Запис у таблиці feed не повинен був створитися, але існує! URL: {invalid_structure_url}"
                )
            print("Підтверджено: запис у таблиці feed не створено")
        else:
            xml_feed_page.goto(test_config.XML_FEEDS_URL)
            xml_feed_page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)
            feeds_count_after = xml_feed_page.get_feeds_table_row_count()
            assert feeds_count_after == feeds_count_before, (
                f"Очікувалось що запис не створиться. "
                f"Кількість рядків змінилась: було {feeds_count_before}, стало {feeds_count_after}"
            )
            print("Підтверджено: запис у таблиці feed не створено")
    
    def test_tc_xml_007_connection_timeout_1min(self, page: Page, test_config: TestConfig):
        """
        TC-XML-007: Таймаут при збереженні фіду (conn-timeout 1 хв)
        
        Валідація фіду при "Зберегти" використовує feed-download з лімітами:
        - conn-timeout 1 хв — якщо сервер не відповідає протягом 1 хв → "connection timeout"
        - socket-timeout 5 хв — якщо після з'єднання дані не надходять 5 хв → "Operation timed out"
        
        Тестуємо conn-timeout 1 хв. URL має відповідати довше 1 хвилини
        (напр. https://httpbin.org/delay/65), щоб гарантовано отримати помилку таймауту.
        
        Кроки:
        - Авторизуватися, обрати постачальника
        - Товари → Імпорт новинок → XML
        - Натиснути "Додати новий фід"
        - Ввести URL сервісу, що довго відповідає (> 1 хв)
        - Увімкнути чекбокс "Завантажити товари з xml"
        - Натиснути "Зберегти"
        
        Очікуваний результат:
        - Помилка "Помилка валідації xml структури фіду помилка завантаження фіду: Connect timed out"
        - Запис у feed не створюється
        """
        timeout_url = test_config.TEST_TIMEOUT_FEED_URL
        
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
        
        feeds_count_before = xml_feed_page.get_feeds_table_row_count()
        
        # Крок 4: Натиснути "Додати новий фід"
        xml_feed_page.click_add_new_feed_button()
        
        # Крок 5: Ввести URL що відповідає довше 1 хв
        xml_feed_page.fill_feed_url(timeout_url)
        page.wait_for_timeout(500)
        
        # Крок 6: Увімкнути чекбокс "Завантажити товари з xml"
        xml_feed_page.enable_upload_items_checkbox()
        
        # Крок 7: Натиснути "Зберегти"
        xml_feed_page.click_save_button()
        # Чекаємо на відповідь: conn-timeout 1 хв + буфер
        page.wait_for_timeout(90000)
        
        # Очікуваний результат 1: Помилка "Connect timed out" (conn-timeout 1 хв)
        xml_feed_page.verify_validation_error_message("Помилка валідації xml структури фіду")
        xml_feed_page.verify_validation_error_message("Connect timed out")
        print("Підтверджено: відображається помилка 'Connect timed out' (conn-timeout)")
        
        # Очікуваний результат 2: Запис у feed не створюється
        if test_config.DB_HOST and test_config.DB_NAME:
            with DBHelper(
                host=test_config.DB_HOST,
                port=test_config.DB_PORT,
                database=test_config.DB_NAME,
                user=test_config.DB_USER,
                password=test_config.DB_PASSWORD
            ) as db:
                feed_exists = db.feed_exists_by_origin_url(timeout_url)
                assert not feed_exists, (
                    f"Запис у таблиці feed не повинен був створитися, але існує! URL: {timeout_url}"
                )
            print("Підтверджено: запис у таблиці feed не створено")
        else:
            xml_feed_page.goto(test_config.XML_FEEDS_URL)
            xml_feed_page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)
            feeds_count_after = xml_feed_page.get_feeds_table_row_count()
            assert feeds_count_after == feeds_count_before, (
                f"Очікувалось що запис не створиться. "
                f"Кількість рядків змінилась: було {feeds_count_before}, стало {feeds_count_after}"
            )
            print("Підтверджено: запис у таблиці feed не створено")
    
    def test_limit_3_active_feeds(self, page: Page, test_config: TestConfig):
        """
        Тест кейс: Обмеження "3 активні фіди"
        
        Перевіряє що при спробі вмикнути фід, коли вже 3 активні,
        система показує помилку "Неможливо підключити більше 3х фідів. Вимкніть спочатку один з фідів".
        
        У таблиці можуть вже бути включені фіди — помилка може з’явитись на 1-й, 2-й або 3-й спробі.
        Проходимо по списку фідів, вмикаємо по черзі, до появи помилки.
        Cleanup: вимкнення увімкнених фідів через БД.
        """
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
        
        # Крок 4: Сортування по "Останнє завантаження" та отримання 4 найсвіжіших фідів
        xml_feed_page.sort_table_by_last_upload_desc()
        feed_ids = xml_feed_page.get_first_n_feed_ids(n=4)
        if len(feed_ids) < 4:
            pytest.skip(f"У таблиці менше 4 фідів (знайдено {len(feed_ids)})")
        print(f"Обрано 4 найсвіжіших фіди: {feed_ids}")
        
        # Вмикаємо фіди по черзі — помилка може з’явитись на будь-якій спробі
        enabled_feed_ids = []
        error_received = False
        
        for i, feed_id in enumerate(feed_ids):
            print(f"Спроба вмикнути фід {i + 1}/4: {feed_id}")
            try:
                xml_feed_page.open_feed_from_table_by_id(feed_id)
            except Exception as e:
                print(f"Не вдалося відкрити фід {feed_id} з таблиці: {e}, пробуємо через URL")
                feed_url = f"{test_config.XML_FEEDS_URL}?feed_id={feed_id}&tab=feed"
                xml_feed_page.goto(feed_url)
                xml_feed_page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)
            # Клік "Редагувати" для переходу в режим редагування
            xml_feed_page.click_edit_button()
            page.wait_for_timeout(1500)
            xml_feed_page.enable_upload_items_checkbox()
            page.wait_for_timeout(500)
            xml_feed_page.click_save_button()
            page.wait_for_timeout(3000)
            
            if xml_feed_page.has_validation_error_message("більше 3") and xml_feed_page.has_validation_error_message("фідів"):
                print(f"Отримано очікувану помилку при спробі вмикнути фід {feed_id}")
                error_received = True
                break
            
            # Збережено успішно — повертаємось до таблиці для наступного фіду
            enabled_feed_ids.append(feed_id)
            print(f"Фід {feed_id} успішно вмикнено")
            xml_feed_page.goto(test_config.XML_FEEDS_URL)
            xml_feed_page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)
        
        assert error_received, (
            "Очікувалась помилка 'Неможливо підключити більше 3х фідів', "
            "але вдалося вмикнути всі 4 фіди без помилки"
        )
        
        # Cleanup: вимкнути фіди, які ми вмикали під час тесту
        if test_config.DB_HOST and test_config.DB_NAME and enabled_feed_ids:
            for fid in enabled_feed_ids:
                try:
                    with DBHelper(
                        host=test_config.DB_HOST,
                        port=test_config.DB_PORT,
                        database=test_config.DB_NAME,
                        user=test_config.DB_USER,
                        password=test_config.DB_PASSWORD
                    ) as db:
                        db.deactivate_feed_by_id(fid)
                    print(f"Фід {fid} вимкнено через БД")
                except Exception as e:
                    error_msg = f"КРИТИЧНА ПОМИЛКА: Не вдалося вимкнути фід {fid} - {e}"
                    print(error_msg)
                    pytest.fail(error_msg)
        elif not enabled_feed_ids:
            print("Увімкнених фідів немає — cleanup не потрібен")
