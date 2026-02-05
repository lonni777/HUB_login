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
    
    def enable_upload_items_checkbox(self):
        """Увімкнути чекбокс 'Завантажити товари з xml'"""
        # Використовуємо складний локатор через filter
        checkbox = self.page.locator("div").filter(
            has_text=re.compile(r"^Завантажити товари з xml.*")
        ).get_by_label("").first
        checkbox.check()
    
    def click_save_button(self):
        """Натиснути кнопку 'Зберегти' та очікувати навігацію"""
        save_button = self.page.locator(self.locators.SAVE_BUTTON)
        save_button.click()
        # Чекаємо на появу повідомлення про успіх або редирект
        self.page.wait_for_timeout(2000)
    
    def verify_success_message(self, expected_text: str = "Дані збережено!"):
        """
        Перевірити повідомлення про успішне збереження
        
        Args:
            expected_text: Очікуваний текст повідомлення
        """
        # Чекаємо трохи більше часу на появу повідомлення
        self.page.wait_for_timeout(2000)
        
        # Спробуємо кілька варіантів локаторів для повідомлення
        success_found = False
        
        # Варіант 1: Точний текст
        try:
            success_message = self.page.locator(f"text={expected_text}")
            if success_message.is_visible(timeout=3000):
                expect(success_message).to_be_visible()
                success_found = True
        except:
            pass
        
        # Варіант 2: Через локатор з класу
        if not success_found:
            try:
                success_message = self.page.locator(self.locators.SUCCESS_MESSAGE)
                if success_message.is_visible(timeout=3000):
                    expect(success_message).to_be_visible()
                    success_found = True
            except:
                pass
        
        # Варіант 3: Шукаємо будь-яке повідомлення що містить частину тексту
        if not success_found:
            try:
                # Шукаємо по частині тексту
                partial_text = "збережено" if "збережено" in expected_text.lower() else expected_text[:5]
                success_message = self.page.locator(f"text=/{partial_text}/i")
                if success_message.is_visible(timeout=3000):
                    expect(success_message).to_be_visible()
                    success_found = True
            except:
                pass
        
        if not success_found:
            # Якщо не знайдено, виводимо що є на сторінці для дебагу
            page_text = self.page.locator("body").text_content()[:500]
            raise AssertionError(
                f"Повідомлення про успіх '{expected_text}' не знайдено на сторінці. "
                f"Видимий текст: {page_text}"
            )
    
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
