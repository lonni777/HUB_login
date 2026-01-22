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
    NON_EXISTENT_USER_EMAIL = os.getenv("TEST_NON_EXISTENT_USER_EMAIL", "nonexistent_user@kasta.ua")
    
    # URL після успішного логіну
    DASHBOARD_URL = os.getenv("TEST_DASHBOARD_URL", "")
    
    @classmethod
    def validate(cls):
        """Перевірка наявності обов'язкових змінних"""
        missing = []
        
        if not cls.USER_EMAIL:
            missing.append("TEST_USER_EMAIL")
        if not cls.USER_PASSWORD:
            missing.append("TEST_USER_PASSWORD")
        
        if missing:
            raise ValueError(
                f"Відсутні обов'язкові змінні середовища: {', '.join(missing)}\n"
                f"Створіть файл .env на основі .env.example та заповніть необхідні дані."
            )
