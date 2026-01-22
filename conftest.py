import pytest
from config.settings import TestConfig


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Налаштування контексту браузера"""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
    }


@pytest.fixture(scope="session")
def test_config():
    """
    Фікстура для конфігурації тестів.
    Завантажує налаштування з .env файлу та валідує їх.
    """
    # Валідація конфігурації при завантаженні
    TestConfig.validate()
    return TestConfig
