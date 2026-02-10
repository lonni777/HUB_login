"""
Модуль для управління конфігурацією та секретами тестів.
Завантажує дані з .env файлу або змінних середовища.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Шлях до кореня проекту
BASE_DIR = Path(__file__).resolve().parent.parent

# Завантаження змінних з .env файлу (якщо він існує)
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)


class TestConfig:
    """Клас для зберігання конфігурації тестів"""
    
    # URL системи
    BASE_URL = os.getenv("TEST_BASE_URL", "https://hubtest.kasta.ua")
    LOGIN_URL = os.getenv("TEST_LOGIN_URL", f"{BASE_URL}/user/login")
    
    # Дані для логіну
    USER_EMAIL = os.getenv("TEST_USER_EMAIL", "")
    USER_PASSWORD = os.getenv("TEST_USER_PASSWORD", "")
    
    # Дані для негативних тестів
    # Email користувача, якого не існує в системі (для негативних кейсів)
    NON_EXISTENT_USER_EMAIL = os.getenv("TEST_NON_EXISTENT_USER_EMAIL", "")
    
    # URL після успішного логіну
    DASHBOARD_URL = os.getenv("TEST_DASHBOARD_URL", "")
    
    # URL для XML-фідів
    XML_FEEDS_URL = os.getenv("TEST_XML_FEEDS_URL", f"{BASE_URL}/supplier-content/xml")
    XML_FEED_ADD_URL = os.getenv("TEST_XML_FEED_ADD_URL", f"{BASE_URL}/supplier-content/xml?feed_id=%20%20%20&tab=feed")
    
    # Тестовий XML-фід URL (з Git Gist)
    TEST_XML_FEED_URL = os.getenv("TEST_XML_FEED_URL", "https://gist.github.com/lonni777/1eb5d08a1dfd4ad0fdf8666ab78ab5be/raw")
    
    # Постачальник для тестування XML-фідів
    TEST_SUPPLIER_NAME = os.getenv("TEST_SUPPLIER_NAME", "Braggart")
    
    # Існуючий feed_id для тестування Excel мапінгу (для оптимізації - використовуємо замість створення нового)
    # Використовується фід постачальника Braggart з ID R2K3
    TEST_EXISTING_FEED_ID = os.getenv("TEST_EXISTING_FEED_ID", "R2K3")
    
    # Налаштування бази даних для очищення тестових даних
    DB_HOST = os.getenv("TEST_DB_HOST", "")
    DB_PORT = int(os.getenv("TEST_DB_PORT", "5432"))
    DB_NAME = os.getenv("TEST_DB_NAME", "")
    DB_USER = os.getenv("TEST_DB_USER", "")
    DB_PASSWORD = os.getenv("TEST_DB_PASSWORD", "")
    
    @classmethod
    def validate(cls):
        """Перевірка наявності обов'язкових змінних"""
        missing = []
        
        if not cls.USER_EMAIL:
            missing.append("TEST_USER_EMAIL")
        if not cls.USER_PASSWORD:
            missing.append("TEST_USER_PASSWORD")
        if not cls.NON_EXISTENT_USER_EMAIL:
            missing.append("TEST_NON_EXISTENT_USER_EMAIL")
        
        if missing:
            raise ValueError(
                f"Відсутні обов'язкові змінні середовища: {', '.join(missing)}\n"
                f"Створіть файл .env на основі .env.example та заповніть необхідні дані."
            )
