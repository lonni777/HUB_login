"""
Page Object для сторінки XML-фідів.
Містить методи для роботи зі сторінкою завантаження та валідації XML-фідів.
"""
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from locators.xml_feed_locators import XMLFeedLocators


class XMLFeedPage(BasePage):
    """Page Object для сторінки XML-фідів"""
    
    def __init__(self, page: Page):
        """
        Ініціалізація сторінки XML-фідів
        
        Args:
            page: Екземпляр Playwright Page
        """
        super().__init__(page)
        self.locators = XMLFeedLocators()
    
    def navigate_to_xml_feeds(self, xml_feeds_url: str):
        """
        Перехід на сторінку XML-фідів
        
        Args:
            xml_feeds_url: URL сторінки XML-фідів
        """
        self.goto(xml_feeds_url)
        self.wait_for_load_state("networkidle")
    
    def navigate_to_xml_feeds_via_menu(self):
        """
        Перехід на сторінку XML-фідів через меню навігації
        Товари → Імпорт новинок → XML
        """
        # Клік на меню "Товари"
        self.page.locator(self.locators.PRODUCTS_MENU).click()
        self.page.wait_for_timeout(500)
        
        # Клік на "Імпорт новинок"
        self.page.locator(self.locators.IMPORT_NEW_ITEMS_LINK).click()
        self.page.wait_for_timeout(500)
        
        # Клік на вкладку "XML"
        self.page.locator(self.locators.XML_TAB_LINK).click()
        self.wait_for_load_state("networkidle")
    
    def open_feed_from_table_by_id(self, feed_id: str):
        """
        Відкрити фід для редагування, клікнувши кнопку "Редагувати" в рядку таблиці.
        Потрібно бути на сторінці з таблицею фідів.
        """
        self.page.wait_for_timeout(3000)
        row = self.page.get_by_role("row").filter(has_text=feed_id).first
        row.wait_for(state="visible", timeout=10000)
        edit_btn = row.get_by_role("button", name=re.compile(r"Редагувати", re.I))
        edit_btn.click()
        self.wait_for_load_state("networkidle")
    
    def sort_table_by_last_upload_desc(self):
        """
        Відсортувати таблицю фідів по стовпцю "Останнє завантаження" (найсвіжіші зверху).
        Клік двічі: перший клік — asc, другий — desc (найновіші зверху).
        """
        self.page.wait_for_selector(".ag-row", timeout=10000)
        header = self.page.locator(self.locators.LAST_UPLOAD_COLUMN_HEADER).first
        header.wait_for(state="visible", timeout=5000)
        header.click()
        self.page.wait_for_timeout(1500)
        header.click()  # Другий клік — descending (найсвіжіші зверху)
        self.page.wait_for_timeout(2000)
    
    def get_first_n_feed_ids(self, n: int = 4) -> list:
        """
        Отримати feed_id з перших n рядків таблиці (після сортування).
        
        Args:
            n: Кількість feed_id для отримання
        
        Returns:
            Список feed_id (наприклад ['R3DV', 'R2K3', ...])
        """
        self.page.wait_for_selector(".ag-row", timeout=10000)
        rows = self.page.locator(".ag-row").all()
        feed_ids = []
        for i, row in enumerate(rows):
            if i >= n:
                break
            try:
                cells = row.locator(".ag-cell").all()
                feed_id = None
                for cell in cells[:4]:  # Перевіряємо перші 4 комірки
                    text = (cell.text_content() or "").strip()
                    if text and re.match(r"^[A-Za-z][A-Za-z0-9]{2,9}$", text) and text not in feed_ids:
                        feed_id = text
                        break
                if feed_id:
                    feed_ids.append(feed_id)
            except Exception:
                continue
        return feed_ids
    
    def get_feeds_table_row_count(self) -> int:
        """
        Отримати кількість рядків у таблиці фідів.
        Потрібно бути на сторінці з таблицею фідів.
        """
        self.page.wait_for_selector(".ag-row", timeout=10000)
        return self.page.locator(".ag-row").count()
    
    def select_supplier(self, supplier_name: str):
        """
        Вибір постачальника зі списку
        
        Args:
            supplier_name: Назва постачальника (наприклад, "Парфюмс")
        """
        # Клік на меню користувача (може бути динамічним)
        try:
            user_menu = self.page.locator(self.locators.USER_MENU)
            if user_menu.is_visible(timeout=2000):
                user_menu.click()
                self.page.wait_for_timeout(500)
        except:
            # Якщо меню користувача не знайдено, спробуємо знайти інший спосіб
            # Можливо, меню вже відкрите або постачальник вже вибрано
            pass
        
        # Клік на "Всі" для відкриття списку постачальників
        try:
            all_suppliers = self.page.locator(self.locators.ALL_SUPPLIERS_OPTION)
            if all_suppliers.is_visible(timeout=2000):
                all_suppliers.click()
                self.page.wait_for_timeout(500)
        except:
            # Якщо "Всі" не знайдено, можливо список вже відкритий
            pass
        
        # Введення назви постачальника в поле пошуку
        # Використовуємо get_by_placeholder для надійності
        try:
            search_input = self.page.get_by_placeholder("Постачальники")
            search_input.click()
            search_input.fill(supplier_name)
        except:
            # Альтернативний спосіб через локатор
            search_input = self.page.locator(self.locators.SUPPLIERS_SEARCH_INPUT)
            search_input.click()
            search_input.fill(supplier_name)
        self.page.wait_for_timeout(1000)
        
        # Вибір постачальника зі списку (шукаємо по тексту, що містить назву)
        # Спробуємо кілька варіантів локаторів
        supplier_found = False
        try:
            # Варіант 1: Точний текст
            supplier_option = self.page.locator(f"text={supplier_name}").first
            if supplier_option.is_visible(timeout=2000):
                supplier_option.click()
                supplier_found = True
        except:
            pass
        
        if not supplier_found:
            try:
                # Варіант 2: Текст з префіксом (як в коді: "v4Парфюмс")
                supplier_option = self.page.locator(f"text=/.*{supplier_name}.*/i").first
                if supplier_option.is_visible(timeout=2000):
                    supplier_option.click()
                    supplier_found = True
            except:
                pass
        
        if not supplier_found:
            # Варіант 3: Будь-який елемент що містить назву
            supplier_option = self.page.locator(f"text=/.*{supplier_name}.*/i").first
            supplier_option.click()
        
        self.wait_for_load_state("networkidle")
    
    def click_add_new_feed_button(self):
        """Натиснути кнопку 'Додати новий фід'"""
        # Використовуємо get_by_role з exact для точної відповідності
        add_button = self.page.get_by_role("button", name="Додати новий фід", exact=True)
        add_button.click()
        self.page.wait_for_timeout(1000)
    
    def fill_feed_url(self, url: str):
        """
        Заповнити поле URL XML-фіду
        
        Args:
            url: URL XML-фіду
        """
        # Використовуємо get_by_placeholder для надійності
        try:
            url_input = self.page.get_by_placeholder("https://127.0.0.1:8000/fmt.")
            url_input.click()
            url_input.fill(url)
        except:
            # Альтернативний спосіб через локатор з частиною тексту
            url_input = self.page.locator("input[placeholder*='fmt']")
            url_input.click()
            url_input.fill(url)
    
    def clear_feed_url(self):
        """Очистити поле URL XML-фіду (залишити порожнім)"""
        try:
            url_input = self.page.get_by_placeholder("https://127.0.0.1:8000/fmt.")
            url_input.click()
            url_input.fill("")
        except:
            url_input = self.page.locator("input[placeholder*='fmt']")
            url_input.click()
            url_input.fill("")
    
    def enable_upload_items_checkbox(self):
        """Увімкнути чекбокс 'Завантажити товари з xml'"""
        # Використовуємо складний локатор через filter
        checkbox = self.page.locator("div").filter(
            has_text=re.compile(r"^Завантажити товари з xml.*")
        ).get_by_label("").first
        checkbox.check()
    
    def disable_upload_items_checkbox(self):
        """Вимкнути чекбокс 'Завантажити товари з xml'"""
        # Використовуємо складний локатор через filter
        checkbox = self.page.locator("div").filter(
            has_text=re.compile(r"^Завантажити товари з xml.*")
        ).get_by_label("").first
        checkbox.uncheck()

    def is_upload_items_checkbox_checked(self) -> bool:
        """
        Перевірити чи увімкнений чекбокс 'Завантажити товари з xml'.

        Returns:
            True якщо чекбокс увімкнений, False якщо вимкнений
        """
        try:
            # Шукаємо input checkbox поруч з текстом "Завантажити товари з xml"
            container = self.page.locator("div").filter(
                has_text=re.compile(r"^Завантажити товари з xml.*")
            ).first
            if container.is_visible(timeout=3000):
                checkbox_input = container.locator("input[type='checkbox']").first
                if checkbox_input.is_visible(timeout=2000):
                    return checkbox_input.is_checked()
            return False
        except Exception:
            return False
    
    def click_save_button(self):
        """Натиснути кнопку 'Зберегти' та очікувати навігацію"""
        save_button = self.page.locator(self.locators.SAVE_BUTTON)
        save_button.click()
        # Чекаємо на появу повідомлення про успіх або редирект
        self.page.wait_for_timeout(5000)
    
    def verify_success_message(self, expected_text: str = "Дані збережено!"):
        """
        Перевірити повідомлення про успішне збереження
        
        Args:
            expected_text: Очікуваний текст повідомлення
        """
        # Чекаємо більше часу на появу повідомлення (може з'явитися після редиректу)
        self.page.wait_for_timeout(10000)
        
        # Спробуємо кілька варіантів локаторів для повідомлення
        success_found = False
        
        # Варіант 1: Точний текст
        try:
            success_message = self.page.locator(f"text={expected_text}")
            if success_message.is_visible(timeout=10000):
                expect(success_message).to_be_visible()
                success_found = True
                print(f"✓ Знайдено повідомлення про успіх: '{expected_text}'")
        except:
            pass
        
        # Варіант 2: Через локатор з класу
        if not success_found:
            try:
                success_message = self.page.locator(self.locators.SUCCESS_MESSAGE)
                if success_message.is_visible(timeout=10000):
                    expect(success_message).to_be_visible()
                    success_found = True
                    print(f"✓ Знайдено повідомлення про успіх через локатор")
            except:
                pass
        
        # Варіант 3: Шукаємо будь-яке повідомлення що містить частину тексту
        if not success_found:
            try:
                # Шукаємо по частині тексту
                partial_text = "збережено" if "збережено" in expected_text.lower() else expected_text[:5]
                success_message = self.page.locator(f"text=/{partial_text}/i")
                if success_message.is_visible(timeout=10000):
                    expect(success_message).to_be_visible()
                    success_found = True
                    print(f"✓ Знайдено повідомлення про успіх з текстом '{partial_text}'")
            except:
                pass
        
        # Варіант 4: Перевіряємо чи є редирект на сторінку зі списком фідів (ознака успіху)
        if not success_found:
            current_url = self.get_url()
            if "/supplier-content/xml" in current_url and "feed_id" not in current_url:
                # Якщо ми на сторінці зі списком фідів без feed_id - це означає успішне збереження
                print("✓ Редирект на сторінку зі списком фідів - фід збережено успішно")
                success_found = True
        
        if not success_found:
            # Якщо не знайдено, виводимо що є на сторінці для дебагу
            page_text = self.page.locator("body").text_content()[:500]
            raise AssertionError(
                f"Повідомлення про успіх '{expected_text}' не знайдено на сторінці. "
                f"Поточний URL: {self.get_url()}. "
                f"Видимий текст: {page_text}"
            )
    
    def has_validation_error_message(self, contains_text: str) -> bool:
        """
        Перевірити чи є на сторінці текст помилки (без raise).
        
        Returns:
            True якщо текст знайдено, False якщо ні
        """
        page_content = self.page.locator("body").text_content() or ""
        return contains_text.lower() in page_content.lower()
    
    def verify_validation_error_message(self, contains_text: str, timeout: int = 10000):
        """
        Перевірити що на сторінці відображається повідомлення про помилку валідації,
        що містить очікуваний текст.
        
        Args:
            contains_text: Частина тексту помилки (наприклад "Помилка валідації xml структури фіду")
            timeout: Таймаут очікування в мс
        """
        self.page.wait_for_timeout(3000)
        page_content = self.page.locator("body").text_content() or ""
        if contains_text.lower() not in page_content.lower():
            raise AssertionError(
                f"Повідомлення про помилку з текстом '{contains_text}' не знайдено на сторінці. "
                f"Поточний URL: {self.get_url()}. "
                f"Видимий текст (фрагмент): {page_content[:800]}"
            )
        print(f"Знайдено повідомлення про помилку валідації з текстом: '{contains_text}'")
    
    def verify_redirect_to_feeds_list(self, expected_url: str):
        """
        Перевірити редирект на сторінку зі списком фідів
        
        Args:
            expected_url: Очікуваний URL сторінки зі списком фідів
        """
        expect(self.page).to_have_url(expected_url, timeout=10000)
    
    def navigate_to_feeds_table(self, feeds_url: str):
        """
        Перейти на сторінку зі списком фідів
        
        Args:
            feeds_url: URL сторінки зі списком фідів
        """
        self.goto(feeds_url)
        self.wait_for_load_state("networkidle")
        # Чекаємо поки таблиця завантажиться
        self.page.wait_for_timeout(2000)
    
    def get_feed_url_from_input(self) -> str:
        """
        Отримати URL фіду з поля введення на сторінці редагування фіду
        
        Returns:
            URL фіду з поля введення або порожній рядок якщо не знайдено
        """
        try:
            # Чекаємо поки поле з'явиться
            self.page.wait_for_timeout(1000)
            
            # Отримуємо значення з поля URL
            url_input = self.page.get_by_placeholder("https://127.0.0.1:8000/fmt.")
            if url_input.is_visible(timeout=3000):
                url_value = url_input.input_value()
                return url_value.strip() if url_value else ""
            
            # Альтернативний спосіб через локатор
            url_input_alt = self.page.locator(self.locators.FEED_URL_INPUT)
            if url_input_alt.is_visible(timeout=2000):
                url_value = url_input_alt.input_value()
                return url_value.strip() if url_value else ""
            
            return ""
        except Exception as e:
            print(f"Помилка при отриманні URL з поля введення: {e}")
            return ""
    
    def filter_feeds_by_link(self, feed_url: str):
        """
        Фільтрувати фіди в таблиці по стовпцю "Лінк фіду"
        
        Args:
            feed_url: URL фіду для фільтрації (оригінальне посилання без пробілів)
        """
        try:
            # Крок 1: Клік на заголовок "Лінк фіду"
            link_column_header = self.page.locator(self.locators.FEED_LINK_COLUMN_HEADER)
            link_column_header.click()
            self.page.wait_for_timeout(500)
            
            # Крок 2: Клік на іконку фільтра
            filter_icon = self.page.locator(self.locators.FEED_LINK_FILTER_ICON)
            filter_icon.click()
            self.page.wait_for_timeout(500)
            
            # Крок 3: Заповнення поля фільтра
            # Видаляємо "/raw" з кінця URL для фільтрації (як в рекордері)
            filter_url = feed_url.replace("/raw", "").strip()
            
            filter_input = self.page.get_by_placeholder("Фільтр")
            filter_input.fill(filter_url)
            self.page.wait_for_timeout(2000)  # Чекаємо поки таблиця відфільтрується
            
        except Exception as e:
            print(f"Помилка при фільтрації фідів: {e}")
            raise
    
    def get_feed_id_from_filtered_table(self) -> str:
        """
        Отримати feed_id з відфільтрованої таблиці (знаходимо span з feed_id)
        
        Returns:
            feed_id або порожній рядок якщо не знайдено
        """
        try:
            # Чекаємо поки таблиця завантажиться
            self.page.wait_for_selector(".ag-row", timeout=5000)
            
            # Знаходимо перший рядок з таблиці (після фільтрації)
            first_row = self.page.locator(".ag-row").first
            
            if first_row.is_visible(timeout=3000):
                # Шукаємо span з feed_id (як в рекордері: span з текстом feed_id)
                # feed_id зазвичай в першій або другій колонці
                cells = first_row.locator(".ag-cell").all()
                
                # Перевіряємо перші кілька комірок
                for cell in cells[:3]:
                    # Шукаємо span з текстом що виглядає як feed_id (наприклад R3E8)
                    spans = cell.locator("span").all()
                    for span in spans:
                        text = span.text_content()
                        if text and text.strip():
                            # Перевіряємо чи це схоже на feed_id (починається з літери та містить цифри)
                            feed_id_candidate = text.strip()
                            if len(feed_id_candidate) > 0 and (feed_id_candidate[0].isalpha() or feed_id_candidate[0].isdigit()):
                                # Перевіряємо що це не просто число або довгий текст
                                if len(feed_id_candidate) <= 10:  # feed_id зазвичай короткий
                                    print(f"Знайдено feed_id з відфільтрованої таблиці: '{feed_id_candidate}'")
                                    return feed_id_candidate
                
                # Альтернативний спосіб - беремо текст з першої комірки
                if len(cells) > 0:
                    first_cell_text = cells[0].text_content()
                    if first_cell_text:
                        feed_id = first_cell_text.strip()
                        if feed_id and len(feed_id) <= 10:
                            print(f"Знайдено feed_id з першої комірки: '{feed_id}'")
                            return feed_id
        except Exception as e:
            print(f"Помилка при отриманні feed_id з таблиці: {e}")
        
        return ""
    
    def click_edit_button(self):
        """Натиснути кнопку 'Редагувати' для відкриття фіду"""
        try:
            # Спочатку клікаємо на "Управління" (як в рекордері)
            management_button = self.page.locator(self.locators.MANAGEMENT_BUTTON)
            if management_button.is_visible(timeout=3000):
                management_button.click()
                self.page.wait_for_timeout(500)
            
            # Потім клікаємо на кнопку "Редагувати" (з пробілом перед текстом як в рекордері)
            edit_button = self.page.get_by_role("button", name=" Редагувати")
            if edit_button.is_visible(timeout=3000):
                edit_button.click()
                self.wait_for_load_state("networkidle")
                self.page.wait_for_timeout(2000)
                return
            
            # Альтернативний спосіб якщо не знайдено
            edit_button_alt = self.page.locator("button:has-text('Редагувати')").first
            if edit_button_alt.is_visible(timeout=2000):
                edit_button_alt.click()
                self.wait_for_load_state("networkidle")
                self.page.wait_for_timeout(2000)
                return
                
        except Exception as e:
            print(f"Помилка при натисканні кнопки 'Редагувати': {e}")
            raise Exception(f"Не вдалося знайти або натиснути кнопку 'Редагувати': {e}")
    
    def open_feed_for_editing(self, feed_id: str):
        """
        Відкрити фід для редагування по feed_id
        
        Args:
            feed_id: ID фіду для відкриття
        """
        # Формуємо URL для редагування фіду
        edit_url = f"{self.get_url().split('?')[0]}?feed_id={feed_id}&tab=feed"
        self.goto(edit_url)
        self.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
    
    def get_feed_id_by_url_from_table(self, feed_url: str) -> str:
        """
        Отримати feed_id з таблиці фідів по URL фіду
        
        Args:
            feed_url: URL XML-фіду для пошуку
        
        Returns:
            feed_id або порожній рядок якщо не знайдено
        """
        try:
            # Чекаємо поки таблиця з'явиться
            self.page.wait_for_selector(".ag-row", timeout=10000)
            
            # Шукаємо рядки в таблиці
            table_rows = self.page.locator(".ag-row").all()
            
            if len(table_rows) == 0:
                print("Таблиця фідів порожня")
                return ""
            
            # Шукаємо рядок з нашим URL
            for row in table_rows:
                row_text = row.text_content() or ""
                
                # Перевіряємо чи містить рядок наш URL
                # Можемо шукати по повному URL або по частині
                url_parts = feed_url.split("/")
                url_key = url_parts[-1] if len(url_parts) > 0 else feed_url
                
                if feed_url in row_text or url_key in row_text:
                    # Знайшли рядок з нашим URL
                    cells = row.locator(".ag-cell").all()
                    if len(cells) > 0:
                        # Перша колонка зазвичай містить feed_id
                        feed_id = cells[0].text_content()
                        if feed_id:
                            feed_id = feed_id.strip()
                            if feed_id:
                                print(f"Знайдено feed_id '{feed_id}' для URL '{feed_url}'")
                                return feed_id
                    
                    # Якщо не знайшли в першій колонці, шукаємо посилання на фід
                    # Посилання може містити feed_id в href
                    try:
                        link = row.locator("a[href*='feed_id']").first
                        if link.is_visible(timeout=2000):
                            href = link.get_attribute("href")
                            if href and "feed_id=" in href:
                                match = re.search(r'feed_id=([^&]+)', href)
                                if match:
                                    feed_id = match.group(1).strip()
                                    feed_id = feed_id.replace("%20", " ").strip()
                                    if feed_id:
                                        print(f"Знайдено feed_id '{feed_id}' з посилання для URL '{feed_url}'")
                                        return feed_id
                    except:
                        pass
            
            print(f"Не знайдено feed_id для URL '{feed_url}' в таблиці")
            return ""
            
        except Exception as e:
            print(f"Помилка при пошуку feed_id в таблиці: {e}")
            return ""
    
    def verify_feed_has_unique_id(self, feed_url: str = None) -> bool:
        """
        Перевірити що новододаний фід отримав унікальний ID в таблиці фідів
        
        Args:
            feed_url: URL фіду для пошуку в таблиці (опціонально)
        
        Returns:
            True якщо ID знайдено в таблиці, False якщо ні
        """
        # Чекаємо поки таблиця завантажиться
        self.page.wait_for_timeout(2000)
        
        # Перевіряємо наявність таблиці фідів
        try:
            # Шукаємо колонку з ID фідів в таблиці
            # Згідно з кодом, колонка має локатор: FEED_ID_COLUMN
            feed_id_column = self.page.locator(self.locators.FEED_ID_COLUMN)
            if feed_id_column.is_visible(timeout=3000):
                # Якщо колонка видима, це означає що таблиця завантажена
                # Тепер шукаємо рядки з даними в таблиці
                # AG Grid таблиця має структуру з рядками
                table_rows = self.page.locator(".ag-row").all()
                if len(table_rows) > 0:
                    # Перевіряємо що є хоча б один рядок з ID
                    # ID фіду зазвичай відображається в першій або другій колонці
                    for row in table_rows[:5]:  # Перевіряємо перші 5 рядків
                        cells = row.locator(".ag-cell").all()
                        if len(cells) > 0:
                            # Перша колонка зазвичай містить ID
                            first_cell_text = cells[0].text_content()
                            if first_cell_text and first_cell_text.strip():
                                # Перевіряємо що ID не порожній і не складається з пробілів
                                feed_id = first_cell_text.strip()
                                if feed_id and feed_id != "":
                                    return True
        except Exception as e:
            # Якщо не вдалося знайти через таблицю, спробуємо через URL
            pass
        
        # Альтернативна перевірка через URL (якщо після збереження є редирект на сторінку фіду)
        current_url = self.get_url()
        if "feed_id=" in current_url:
            match = re.search(r'feed_id=([^&]+)', current_url)
            if match:
                feed_id = match.group(1).strip()
                if feed_id and feed_id != "%20%20%20" and feed_id != "":
                    return True
        
        return False
    
    def get_feed_id_from_table(self, feed_url: str = None) -> str:
        """
        Отримати ID фіду з таблиці фідів
        
        Args:
            feed_url: URL фіду для пошуку в таблиці (опціонально)
        
        Returns:
            ID фіду або порожній рядок якщо не знайдено
        """
        # Чекаємо поки таблиця завантажиться
        self.page.wait_for_timeout(3000)
        
        # Спочатку перевіряємо чи є редирект на сторінку конкретного фіду
        current_url = self.get_url()
        if "feed_id=" in current_url:
            match = re.search(r'feed_id=([^&]+)', current_url)
            if match:
                feed_id = match.group(1).strip()
                feed_id = feed_id.replace("%20", " ").strip()
                if feed_id and feed_id != "":
                    return feed_id
        
        # Якщо не знайдено в URL, шукаємо в таблиці
        try:
            # Чекаємо поки таблиця з'явиться
            self.page.wait_for_selector(".ag-row", timeout=5000)
            
            # Шукаємо рядки в таблиці
            table_rows = self.page.locator(".ag-row").all()
            if len(table_rows) > 0:
                # Перевіряємо перші рядки
                for row in table_rows[:10]:  # Перевіряємо перші 10 рядків
                    cells = row.locator(".ag-cell").all()
                    if len(cells) > 0:
                        # Якщо вказано feed_url, шукаємо рядок з цим URL
                        if feed_url:
                            row_text = row.text_content()
                            # Перевіряємо чи містить рядок URL (може бути скорочений)
                            url_short = feed_url.split("/")[-1] if "/" in feed_url else feed_url
                            if feed_url in row_text or url_short in row_text:
                                # Знайшли рядок з нашим URL, беремо ID з першої колонки
                                first_cell_text = cells[0].text_content()
                                if first_cell_text:
                                    return first_cell_text.strip()
                        else:
                            # Беремо ID з першого рядка (найновіший фід)
                            first_cell_text = cells[0].text_content()
                            if first_cell_text and first_cell_text.strip():
                                feed_id = first_cell_text.strip()
                                # Перевіряємо що це дійсно ID (не порожній рядок)
                                if feed_id and len(feed_id) > 0:
                                    return feed_id
        except Exception as e:
            # Якщо не вдалося знайти через таблицю, повертаємо порожній рядок
            pass
        
        return ""
    
    def download_excel_mapping_file(self, download_path: str, feed_id: str = None) -> str:
        """
        Скачати Excel файл мапінгу для фіду
        
        Args:
            download_path: Шлях до папки для збереження файлу
            feed_id: ID фіду для іменування файлу (опціонально)
        
        Returns:
            Шлях до скачаного файлу або порожній рядок якщо не вдалося
        """
        try:
            from datetime import datetime
            from pathlib import Path
            
            # Створюємо папку для завантажень якщо її немає
            download_dir = Path(download_path)
            download_dir.mkdir(parents=True, exist_ok=True)
            
            # Очікуємо появу кнопки скачування
            download_button = self.page.locator(self.locators.DOWNLOAD_EXCEL_MAPPING_BUTTON)
            if not download_button.is_visible(timeout=10000):
                # Спробуємо альтернативний локатор через filter
                download_button = self.page.locator("button").filter(has_text="Отримати файл для ручного мапінгу")
                if not download_button.is_visible(timeout=5000):
                    raise Exception("Кнопка скачування Excel файлу мапінгу не знайдена")
            
            # Перевіряємо що кнопка клікабельна
            download_button.wait_for(state="visible", timeout=5000)
            download_button.wait_for(state="attached", timeout=5000)
            self.page.wait_for_timeout(2000)  # Додаткове очікування перед кліком
            
            print("Клікаємо на кнопку скачування Excel файлу...")
            # Збільшений таймаут для кліку (завантаження файлу може тривати)
            with self.page.expect_download(timeout=90000) as download_info:
                download_button.click(timeout=60000)
                self.page.wait_for_timeout(3000)
            
            download = download_info.value
            print(f"Завантаження почалося: {download.suggested_filename}")
            
            # Формуємо ім'я файлу: feed_id + дата (якщо feed_id вказано)
            if feed_id:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_name = f"{feed_id}_{timestamp}.xlsx"
            else:
                # Використовуємо оригінальне ім'я з додаванням дати
                original_name = download.suggested_filename
                if not original_name.endswith('.xlsx') and not original_name.endswith('.xls'):
                    original_name = original_name + '.xlsx'
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name_parts = Path(original_name).stem
                file_name = f"{name_parts}_{timestamp}.xlsx"
            
            # Зберігаємо файл з новим ім'ям
            file_path = download_dir / file_name
            download.save_as(file_path)
            
            # Перевіряємо що файл існує
            if file_path.exists():
                print(f"Excel файл успішно скачано: {file_path}")
                return str(file_path)
            else:
                print("Файл не знайдено після скачування")
                return ""
                
        except Exception as e:
            print(f"Помилка при скачуванні Excel файлу: {e}")
            return ""
    
    def upload_excel_mapping_file(self, file_path: str) -> bool:
        """
        Завантажити Excel файл мапінгу для фіду
        
        Args:
            file_path: Шлях до Excel файлу для завантаження
        
        Returns:
            True якщо файл успішно завантажено, False якщо ні
        """
        try:
            from pathlib import Path
            
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise Exception(f"Файл не знайдено: {file_path}")
            
            # Знаходимо поле для завантаження файлу (input[type='file'])
            # Input може бути прихований через CSS, тому шукаємо незалежно від видимості
            file_input = None
            
            # Варіант 1: Шукаємо будь-який input[type='file'] на сторінці
            file_inputs = self.page.locator("input[type='file']").all()
            if len(file_inputs) > 0:
                file_input = file_inputs[0]
            else:
                # Варіант 2: Спробуємо знайти input поруч з кнопкою завантаження
                upload_button = self.page.locator(self.locators.UPLOAD_EXCEL_MAPPING_BUTTON)
                if upload_button.is_visible(timeout=3000):
                    # Шукаємо input в батьківському елементі або поруч
                    # Можливо input знаходиться в label або в тому ж контейнері
                    parent = upload_button.locator("..")
                    file_inputs_near_button = parent.locator("input[type='file']").all()
                    if len(file_inputs_near_button) > 0:
                        file_input = file_inputs_near_button[0]
                    else:
                        # Шукаємо в label якщо кнопка в label
                        label = upload_button.locator("xpath=ancestor::label").first
                        if label.count() > 0:
                            file_inputs_in_label = label.locator("input[type='file']").all()
                            if len(file_inputs_in_label) > 0:
                                file_input = file_inputs_in_label[0]
            
            if file_input is None:
                raise Exception("Поле для завантаження файлу (input[type='file']) не знайдено")
            
            # Завантажуємо файл (input може бути прихований, але set_input_files все одно працює)
            file_input.set_input_files(str(file_path_obj))
            self.page.wait_for_timeout(2000)
            
            # Після завантаження файлу може знадобитися натиснути кнопку завантаження
            # (якщо файл не завантажується автоматично)
            try:
                upload_button = self.page.locator(self.locators.UPLOAD_EXCEL_MAPPING_BUTTON)
                if upload_button.is_visible(timeout=2000):
                    # Можливо після вибору файлу потрібно натиснути кнопку
                    upload_button.click()
                    self.page.wait_for_timeout(2000)
            except:
                # Якщо кнопка не знайдена або не потрібна, продовжуємо
                pass
            
            print(f"Excel файл успішно завантажено: {file_path}")
            return True
            
        except Exception as e:
            print(f"Помилка при завантаженні Excel файлу: {e}")
            return False