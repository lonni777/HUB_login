import pytest
from datetime import datetime
from pathlib import Path
from config.settings import TestConfig


def pytest_configure(config):
    """
    Налаштування pytest перед запуском тестів.
    Генерує унікальне ім'я звіту з timestamp для збереження історії запусків.
    """
    # Створюємо папку reports якщо її немає
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Генеруємо timestamp для унікального імені звіту
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = reports_dir / f"report_{timestamp}.html"
    
    # Замінюємо шлях до звіту на версію з timestamp
    # pytest-html зберігає шлях в config.option.htmlpath
    if hasattr(config.option, 'htmlpath') and config.option.htmlpath:
        # Замінюємо стандартний шлях на версію з timestamp
        config.option.htmlpath = str(report_path)
    else:
        # Якщо htmlpath не встановлено, встановлюємо його
        config.option.htmlpath = str(report_path)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Налаштування контексту браузера"""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
    }


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Хук для збереження скріншотів та trace при помилках тестів.
    Автоматично зберігає артефакти після кожного тесту.
    """
    outcome = yield
    rep = outcome.get_result()
    
    # Зберігаємо скріншот та trace тільки якщо тест завершився з помилкою або failed
    if rep.when == "call" and rep.failed:
        # Отримуємо page з тесту (якщо доступний)
        if "page" in item.fixturenames:
            page = item.funcargs.get("page")
            if page:
                # Створюємо папку для збереження артефактів
                screenshots_dir = Path("test-results/screenshots")
                screenshots_dir.mkdir(parents=True, exist_ok=True)
                
                # Генеруємо унікальне ім'я файлу
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                test_name = item.name.replace("::", "_").replace("[", "_").replace("]", "")
                screenshot_path = screenshots_dir / f"{test_name}_{timestamp}.png"
                
                try:
                    # Зберігаємо скріншот
                    page.screenshot(path=str(screenshot_path), full_page=True)
                    # Додаємо шлях до скріншота в звіт
                    rep.extra = [{"type": "image", "name": "Screenshot", "value": str(screenshot_path)}]
                except Exception as e:
                    # Якщо не вдалося зробити скріншот, ігноруємо помилку
                    pass


@pytest.fixture(scope="session")
def test_config():
    """
    Фікстура для конфігурації тестів.
    Завантажує налаштування з .env файлу та валідує їх.
    """
    # Валідація конфігурації при завантаженні
    TestConfig.validate()
    return TestConfig
