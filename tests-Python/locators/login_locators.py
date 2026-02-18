"""
Локатори для сторінки логіну.
Всі селектори зберігаються тут для легкого оновлення.
"""


class LoginLocators:
    """Клас з локаторами для сторінки логіну"""
    
    # Поля форми
    EMAIL_INPUT = "#email"
    PASSWORD_INPUT = "#password"
    
    # Кнопки
    # Кнопка "Увійти" - використовуємо role-based селектор
    LOGIN_BUTTON = "role=button[name='Увійти']"
    # Альтернативні варіанти (якщо потрібні):
    # LOGIN_BUTTON = "form > button"  # Спрощений варіант (може не працювати якщо є кілька форм)
    # LOGIN_BUTTON = "button:has-text('Увійти')"  # Пошук по тексту
    
    # Повідомлення про помилки
    # Alert помилка над формою логіну/реєстрації
    ERROR_ALERT = "form .ant-alert.ant-alert-error"
    # Альтернативний повний селектор (якщо потрібен більш специфічний):
    # ERROR_ALERT = "#root-content > div:nth-child(2) > form > div.ant-alert.ant-alert-error"
    
    # Помилка валідації під полем (Обов'язкове поле)
    # Використовуємо загальний селектор для помилок валідації Ant Design форм
    FIELD_VALIDATION_ERROR = "form .ant-form-item-explain-error"
    
    # Інші елементи сторінки
    # LOGIN_FORM = "form"  # Приклад додаткового локатора
