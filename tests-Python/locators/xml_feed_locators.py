"""
Локатори для сторінки XML-фідів.
Всі селектори зберігаються тут для легкого оновлення.
"""


class XMLFeedLocators:
    """Клас з локаторами для сторінки XML-фідів"""
    
    # Навігація
    PRODUCTS_MENU = "text=Товари"
    IMPORT_NEW_ITEMS_LINK = "role=link[name='Імпорт новинок']"
    XML_TAB_LINK = "role=link[name='XML']"
    
    # Вибір постачальника
    USER_MENU = "text=Ilona / Ілона Karpenko"  # Може бути динамічним
    ALL_SUPPLIERS_OPTION = "text=Всі (8859)"  # Може бути динамічним
    SUPPLIERS_SEARCH_INPUT = "[placeholder*='Постачальник']"  # Використовуємо частину тексту через атрибут
    SUPPLIER_OPTION = "text=v4Парфюмс"  # Приклад: динамічний локатор, метод select_supplier використовує пошук по тексту
    
    # Кнопки
    ADD_NEW_FEED_BUTTON = "role=button[name='Додати новий фід']"
    SAVE_BUTTON = "role=button[name='Зберегти']"
    
    # Поля форми додавання XML-фіду
    FEED_URL_INPUT = "placeholder=https://127.0.0.1:8000/fmt."
    
    # Чекбокси
    # Чекбокс "Завантажити товари з xml" - використовуємо складний локатор через filter
    UPLOAD_ITEMS_CHECKBOX = "div:has-text('Завантажити товари з xml') >> label"
    
    # Повідомлення про успіх/помилки
    SUCCESS_MESSAGE = "text=Дані збережено!"
    
    # Таблиця XML-фідів
    FEEDS_TABLE = "#root-content"
    FEED_ID_COLUMN = "div:nth-child(3) > .ag-header-cell-comp-wrapper > .ag-cell-label-container > .ag-header-cell-label"
    FEED_LINK_COLUMN_HEADER = "text=Лінк фіду"  # Заголовок стовпця "Лінк фіду"
    LAST_UPLOAD_COLUMN_HEADER = "text=Останнє завантаження"  # Стовпець для сортування найсвіжіших фідів
    FEED_LINK_FILTER_ICON = "div:nth-child(4) > .ag-header-cell-comp-wrapper > .ag-cell-label-container > .ag-header-icon > .ag-icon"  # Іконка фільтра для "Лінк фіду"
    FEED_LINK_FILTER_INPUT = "placeholder=Фільтр"  # Поле фільтра
    MANAGEMENT_BUTTON = "text=Управління[exact=true]"  # Кнопка "Управління"
    EDIT_BUTTON = "role=button[name=' Редагувати']"  # Кнопка редагування (з пробілом перед текстом!)
    
    # Excel мапінг
    DOWNLOAD_EXCEL_MAPPING_BUTTON = "text=Отримати файл для ручного мапінгу"  # Кнопка скачування Excel файлу мапінгу
    UPLOAD_EXCEL_MAPPING_BUTTON = "text=Завантажити ручний мапінг категорій"  # Кнопка завантаження Excel файлу мапінгу
    UPLOAD_EXCEL_INPUT = "input[type='file']"  # Поле для завантаження Excel файлу (може бути приховане)
