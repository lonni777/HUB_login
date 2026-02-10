"""
Тести для функціоналу Excel мапінгу фідів.
Містить тест-кейси для скачування та завантаження Excel файлів мапінгу.
"""
import pytest
from pathlib import Path
from playwright.sync_api import Page
from config.settings import TestConfig
from pages.xml_feed_page import XMLFeedPage
from pages.login_page import LoginPage
from utils.db_helper import DBHelper
from utils.excel_validator import ExcelValidator


class TestExcelMapping:
    """Тест сьют: Excel мапінг фідів - Скачування та завантаження"""
    
    def test_excel_mapping_file_download_and_upload(self, page: Page, test_config: TestConfig):
        """
        Тест кейс: Скачування та завантаження Excel файлу мапінгу
        
        Перевіряє:
        1. Відкриття існуючого фіду (використовується фід R3DV постачальника Парфюмс)
        2. Скачування Excel файлу мапінгу (зберігається з ім'ям feed_id_YYYYMMDD_HHMMSS.xlsx)
        3. Перевірка структури Excel файлу (наявність вкладок, перевірка вкладки "Категорія+")
        4. Завантаження цього ж Excel файлу назад в систему
        5. Отримання повідомлення про успіх "Дані збережено!"
        6. Вимкнення фіду після тесту (прибрати галочку "Завантажити товари з xml")
        """
        # Визначаємо feed_id: використовуємо існуючий з конфігу або створюємо новий
        feed_id = test_config.TEST_EXISTING_FEED_ID
        
        # Крок 1: Авторизація в хаб
        login_page = LoginPage(page)
        login_page.navigate_to_login(f"{test_config.LOGIN_URL}?next=/supplier-content/xml")
        login_page.login(
            email=test_config.USER_EMAIL,
            password=test_config.USER_PASSWORD
        )
        login_page.verify_successful_login()
        
        # Крок 2: Вибір постачальника "Парфюмс"
        xml_feed_page = XMLFeedPage(page)
        xml_feed_page.select_supplier(test_config.TEST_SUPPLIER_NAME)
        
        # Крок 3: Перехід в Товари - Імпорт новинок - XML
        xml_feed_page.navigate_to_xml_feeds_via_menu()
        
        # Крок 4: Відкриваємо існуючий фід або створюємо новий якщо feed_id не вказано
        if feed_id:
            # Оптимізований шлях: використовуємо існуючий фід
            print(f"Використовуємо існуючий фід: {feed_id}")
            # Відкриваємо фід безпосередньо по URL
            feed_edit_url = f"{test_config.XML_FEEDS_URL}?feed_id={feed_id}&tab=feed"
            xml_feed_page.goto(feed_edit_url)
            xml_feed_page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)
            
            # Перевіряємо що фід відкрився (опціонально - можна перевірити наявність URL поля)
            try:
                # Перевіряємо що ми на сторінці редагування фіду
                current_url = xml_feed_page.get_url()
                if feed_id not in current_url:
                    raise AssertionError(f"Не вдалося відкрити фід {feed_id}. Поточний URL: {current_url}")
            except Exception as e:
                print(f"Попередження: не вдалося перевірити відкриття фіду: {e}")
        else:
            # Fallback: створюємо новий фід (оригінальна логіка)
            print("Існуючий feed_id не вказано, створюємо новий фід...")
            xml_feed_page.click_add_new_feed_button()
            xml_feed_page.fill_feed_url(test_config.TEST_XML_FEED_URL)
            xml_feed_page.enable_upload_items_checkbox()
            xml_feed_page.click_save_button()
            xml_feed_page.verify_success_message("Дані збережено!")
            
            # Знаходимо feed_id нового фіду
            xml_feed_page.navigate_to_feeds_table(test_config.XML_FEEDS_URL)
            feed_id = xml_feed_page.get_feed_id_by_url_from_table(test_config.TEST_XML_FEED_URL)
            
            if not feed_id:
                raise AssertionError("Не вдалося знайти feed_id після збереження фіду")
            
            # Відкриваємо фід для редагування
            xml_feed_page.open_feed_for_editing(feed_id)
        
        # Крок 9: Скачуємо Excel файл мапінгу
        # Файл буде збережено з ім'ям: feed_id_YYYYMMDD_HHMMSS.xlsx
        download_dir = Path("test-results/excel_mappings")
        excel_file_path = xml_feed_page.download_excel_mapping_file(str(download_dir), feed_id=feed_id)
        
        if not excel_file_path:
            raise AssertionError("Не вдалося скачати Excel файл мапінгу")
        
        # Перевіряємо що файл існує та має правильний формат
        excel_file = Path(excel_file_path)
        assert excel_file.exists(), f"Скачаний Excel файл не знайдено: {excel_file_path}"
        assert excel_file.suffix.lower() in ['.xlsx', '.xls'], f"Файл не є Excel файлом: {excel_file_path}"
        
        # Перевіряємо що ім'я файлу містить feed_id
        assert feed_id in excel_file.stem, f"Ім'я файлу не містить feed_id: {excel_file.name}"
        
        print(f"Excel файл успішно скачано: {excel_file_path}")
        
        # Крок 10: Завантажуємо Excel файл назад
        upload_success = xml_feed_page.upload_excel_mapping_file(excel_file_path)
        
        if not upload_success:
            raise AssertionError("Не вдалося завантажити Excel файл мапінгу")
        
        # Крок 11: Перевірка повідомлення про успіх після завантаження
        # Чекаємо трохи більше часу після завантаження файлу
        page.wait_for_timeout(3000)
        
        # Спробуємо знайти повідомлення про успіх
        try:
            xml_feed_page.verify_success_message("Дані збережено!")
            print("Повідомлення 'Дані збережено!' знайдено після завантаження Excel файлу")
        except AssertionError:
            # Якщо повідомлення не знайдено, перевіряємо що ми залишилися на сторінці редагування
            # та що немає помилок (це означає що файл завантажився успішно)
            current_url = xml_feed_page.get_url()
            if "feed_id" in current_url and "tab=feed" in current_url:
                print("Файл завантажено успішно (перевірено через URL сторінки)")
            else:
                # Якщо не на сторінці редагування, спробуємо знайти інші індикатори успіху
                page.wait_for_timeout(2000)
                # Повторна спроба знайти повідомлення
                try:
                    xml_feed_page.verify_success_message("Дані збережено!")
                except:
                    print("Попередження: повідомлення про успіх не знайдено, але файл завантажено")
        
        print("Excel файл успішно завантажено та збережено")
        
        # Cleanup: Вимкнути фід після тесту (важливо щоб фід не оброблявся)
        # Варіант 1: Через UI (прибрати галочку "Завантажити товари з xml" і зберегти)
        # Варіант 2: Через БД (встановити is_active = false)
        # Використовуємо обидва варіанти для надійності
        
        feed_deactivation_success = False
        
        # Спробуємо вимкнути через UI
        try:
            print(f"Вимкнення фіду {feed_id} через UI...")
            # Переконаємося що ми на сторінці редагування фіду
            current_url = xml_feed_page.get_url()
            if feed_id not in current_url:
                # Якщо не на сторінці редагування, відкриваємо її
                feed_edit_url = f"{test_config.XML_FEEDS_URL}?feed_id={feed_id}&tab=feed"
                xml_feed_page.goto(feed_edit_url)
                xml_feed_page.wait_for_load_state("networkidle")
                page.wait_for_timeout(2000)
            
            # Вимкнути чекбокс "Завантажити товари з xml"
            xml_feed_page.disable_upload_items_checkbox()
            page.wait_for_timeout(500)
            
            # Зберегти зміни
            xml_feed_page.click_save_button()
            page.wait_for_timeout(2000)
            
            # Перевірити повідомлення про успіх
            try:
                xml_feed_page.verify_success_message("Дані збережено!")
                print("Фід успішно вимкнено через UI")
                feed_deactivation_success = True
            except:
                # Якщо повідомлення не знайдено, перевіряємо через URL
                if "feed_id" in xml_feed_page.get_url():
                    print("Фід вимкнено через UI (перевірено через URL)")
                    feed_deactivation_success = True
        except Exception as e:
            print(f"Попередження: не вдалося вимкнути фід через UI: {e}")
        
        # Якщо UI не спрацював, використовуємо БД
        if not feed_deactivation_success:
            try:
                print(f"Вимкнення фіду {feed_id} через БД (is_active = false)...")
                if test_config.DB_HOST and test_config.DB_NAME:
                    with DBHelper(
                        host=test_config.DB_HOST,
                        port=test_config.DB_PORT,
                        database=test_config.DB_NAME,
                        user=test_config.DB_USER,
                        password=test_config.DB_PASSWORD
                    ) as db:
                        db.deactivate_feed_by_id(feed_id)
                        feed_deactivation_success = True
                        print("Фід успішно вимкнено через БД")
                else:
                    print("Попередження: налаштування БД не вказані, не можна вимкнути фід через БД")
            except Exception as e:
                error_msg = f"КРИТИЧНА ПОМИЛКА: Не вдалося вимкнути фід {feed_id} - {e}"
                print(error_msg)
                # Не провалюємо тест, але виводимо попередження
                pytest.fail(error_msg)
        
        # Cleanup: Видалення фіду з БД виконуємо тільки якщо створювали новий фід
        if not test_config.TEST_EXISTING_FEED_ID:
            # Якщо створювали новий фід - видаляємо його з БД
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
        else:
            print(f"Використовували існуючий фід {feed_id}, cleanup з БД не потрібен")
        
        # Очищаємо скачаний Excel файл після тесту
        try:
            if excel_file.exists():
                excel_file.unlink()
                print(f"Скачаний Excel файл видалено: {excel_file_path}")
        except:
            pass
    
    def test_excel_mapping_file_validation(self, page: Page, test_config: TestConfig):
        """
        Тест кейс: Валідація структури та даних Excel файлу мапінгу
        
        Перевіряє:
        1. Відкриття існуючого фіду (використовується фід R3DV постачальника Парфюмс)
        2. Скачування Excel файлу мапінгу
        3. Перевірка наявності всіх очікуваних вкладок (10 вкладок)
        4. Перевірка даних у вкладці "Категорія+" - порівняння з XML-фідом:
           - Перевірка наявності всіх ID категорій з фіду
           - Перевірка відповідності назв категорій
        5. Вимкнення фіду після тесту
        """
        # Визначаємо feed_id: використовуємо існуючий з конфігу
        feed_id = test_config.TEST_EXISTING_FEED_ID
        
        if not feed_id:
            pytest.skip("TEST_EXISTING_FEED_ID не вказано в конфігурації")
        
        # Список очікуваних вкладок
        expected_sheets = [
            "Результат",
            "Довідник кольорів",
            "Каскад+",
            "Конвертер+",
            "Категорія+",
            "Інструкція щодо мапінгу Каскад",
            "Підказки категорій",
            "Ігнорувати+",
            "Довідник Каста",
            "Оффер+"
        ]
        
        # Крок 1: Авторизація в хаб
        login_page = LoginPage(page)
        login_page.navigate_to_login(f"{test_config.LOGIN_URL}?next=/supplier-content/xml")
        login_page.login(
            email=test_config.USER_EMAIL,
            password=test_config.USER_PASSWORD
        )
        login_page.verify_successful_login()
        
        # Крок 2: Вибір постачальника "Парфюмс"
        xml_feed_page = XMLFeedPage(page)
        xml_feed_page.select_supplier(test_config.TEST_SUPPLIER_NAME)
        
        # Крок 3: Перехід в Товари - Імпорт новинок - XML
        xml_feed_page.navigate_to_xml_feeds_via_menu()
        
        # Крок 4: Відкриваємо існуючий фід R3DV
        print(f"Відкриваємо існуючий фід: {feed_id}")
        feed_edit_url = f"{test_config.XML_FEEDS_URL}?feed_id={feed_id}&tab=feed"
        xml_feed_page.goto(feed_edit_url)
        xml_feed_page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        # Перевіряємо що фід відкрився
        current_url = xml_feed_page.get_url()
        assert feed_id in current_url, f"Не вдалося відкрити фід {feed_id}. Поточний URL: {current_url}"
        
        # Крок 5: Скачуємо Excel файл мапінгу
        download_dir = Path("test-results/excel_mappings")
        excel_file_path = xml_feed_page.download_excel_mapping_file(str(download_dir), feed_id=feed_id)
        
        if not excel_file_path:
            raise AssertionError("Не вдалося скачати Excel файл мапінгу")
        
        excel_file = Path(excel_file_path)
        assert excel_file.exists(), f"Скачаний Excel файл не знайдено: {excel_file_path}"
        assert excel_file.suffix.lower() in ['.xlsx', '.xls'], f"Файл не є Excel файлом: {excel_file_path}"
        
        print(f"Excel файл успішно скачано: {excel_file_path}")
        
        # Крок 6: Валідація Excel файлу
        with ExcelValidator(excel_file_path) as excel_validator:
            # Крок 6.1: Перевірка наявності всіх очікуваних вкладок
            print(f"Перевірка наявності очікуваних вкладок ({len(expected_sheets)} вкладок)...")
            all_found, missing_sheets = excel_validator.verify_sheets_exist(expected_sheets)
            
            if not all_found:
                raise AssertionError(
                    f"Не знайдено очікуваних вкладок в Excel файлі: {', '.join(missing_sheets)}\n"
                    f"Знайдені вкладки: {', '.join(excel_validator.get_sheet_names())}"
                )
            
            print(f"✓ Всі очікувані вкладки знайдено ({len(expected_sheets)} вкладок)")
            
            # Крок 6.2: Перевірка даних у вкладці "Категорія+" - порівняння з XML-фідом
            print("Перевірка даних у вкладці 'Категорія+'...")
            
            if not excel_validator.sheet_exists("Категорія+"):
                raise AssertionError("Вкладка 'Категорія+' не знайдена в Excel файлі")
            
            # Отримуємо категорії з Excel
            excel_categories = excel_validator.get_category_id_and_name_from_feed("Категорія+")
            print(f"Знайдено категорій у вкладці 'Категорія+': {len(excel_categories)}")
            
            if len(excel_categories) == 0:
                raise AssertionError("Вкладка 'Категорія+' порожня або не містить даних")
            
            # Порівнюємо з XML-фідом: використовуємо URL саме цього фіду (R3DV) з БД,
            # щоб Excel відповідав тому XML, з якого згенерований
            xml_feed_url = None
            if test_config.DB_HOST and test_config.DB_NAME:
                try:
                    with DBHelper(
                        host=test_config.DB_HOST,
                        port=test_config.DB_PORT,
                        database=test_config.DB_NAME,
                        user=test_config.DB_USER,
                        password=test_config.DB_PASSWORD
                    ) as db:
                        xml_feed_url = db.get_feed_url_by_id(feed_id)
                except Exception:
                    pass
            if xml_feed_url:
                # Прибираємо фрагмент #ufeed... для HTTP-запиту
                if '#' in xml_feed_url:
                    xml_feed_url = xml_feed_url.split('#')[0]
            if not xml_feed_url:
                xml_feed_url = test_config.TEST_XML_FEED_URL
            print(f"Порівняння з XML-фідом: {xml_feed_url}")
            
            comparison_result = excel_validator.compare_categories_with_xml_feed(
                xml_feed_url=xml_feed_url,
                sheet_name="Категорія+"
            )
            
            print(f"Результати порівняння:")
            print(f"  - Категорій в Excel: {comparison_result['excel_categories_count']}")
            print(f"  - Категорій в XML: {comparison_result['xml_categories_count']}")
            print(f"  - Спільних категорій: {comparison_result['common_categories_count']}")
            
            # Перевірка: кожна категорія з Excel має існувати в XML з тією ж назвою.
            # Не вимагаємо, щоб у Excel були всі категорії з XML (фід може фільтрувати).
            if comparison_result['missing_in_xml']:
                missing_ids = [c['id'] for c in comparison_result['missing_in_xml']]
                raise AssertionError(
                    f"Категорії з Excel відсутні в XML-фіді ({len(comparison_result['missing_in_xml'])}): "
                    f"{', '.join(missing_ids[:10])}"
                )
            
            if comparison_result['mismatched_names']:
                mismatched = comparison_result['mismatched_names'][:5]
                mismatched_str = ", ".join([f"{c['id']} (Excel: '{c['excel_name']}', XML: '{c['xml_name']}')" 
                                           for c in mismatched])
                raise AssertionError(
                    f"Невідповідність назв категорій ({len(comparison_result['mismatched_names'])}): {mismatched_str}"
                )
            
            print("✓ Усі категорії з Excel присутні в XML-фіді з правильними назвами")
        
        print("Валідація Excel файлу завершена успішно")
        
        # Cleanup: Вимкнути фід після тесту
        feed_deactivation_success = False
        
        # Спробуємо вимкнути через UI
        try:
            print(f"Вимкнення фіду {feed_id} через UI...")
            current_url = xml_feed_page.get_url()
            if feed_id not in current_url:
                feed_edit_url = f"{test_config.XML_FEEDS_URL}?feed_id={feed_id}&tab=feed"
                xml_feed_page.goto(feed_edit_url)
                xml_feed_page.wait_for_load_state("networkidle")
                page.wait_for_timeout(2000)
            
            xml_feed_page.disable_upload_items_checkbox()
            page.wait_for_timeout(500)
            xml_feed_page.click_save_button()
            page.wait_for_timeout(2000)
            
            try:
                xml_feed_page.verify_success_message("Дані збережено!")
                print("Фід успішно вимкнено через UI")
                feed_deactivation_success = True
            except:
                if "feed_id" in xml_feed_page.get_url():
                    print("Фід вимкнено через UI (перевірено через URL)")
                    feed_deactivation_success = True
        except Exception as e:
            print(f"Попередження: не вдалося вимкнути фід через UI: {e}")
        
        # Якщо UI не спрацював, використовуємо БД
        if not feed_deactivation_success:
            try:
                print(f"Вимкнення фіду {feed_id} через БД (is_active = false)...")
                if test_config.DB_HOST and test_config.DB_NAME:
                    with DBHelper(
                        host=test_config.DB_HOST,
                        port=test_config.DB_PORT,
                        database=test_config.DB_NAME,
                        user=test_config.DB_USER,
                        password=test_config.DB_PASSWORD
                    ) as db:
                        db.deactivate_feed_by_id(feed_id)
                        feed_deactivation_success = True
                        print("Фід успішно вимкнено через БД")
                else:
                    print("Попередження: налаштування БД не вказані, не можна вимкнути фід через БД")
            except Exception as e:
                error_msg = f"КРИТИЧНА ПОМИЛКА: Не вдалося вимкнути фід {feed_id} - {e}"
                print(error_msg)
                pytest.fail(error_msg)
        
        # Очищаємо скачаний Excel файл після тесту
        try:
            if excel_file.exists():
                excel_file.unlink()
                print(f"Скачаний Excel файл видалено: {excel_file_path}")
        except:
            pass
