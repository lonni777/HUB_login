"""
Базовий клас для всіх Page Objects.
Містить загальні методи для роботи зі сторінками.
"""
from playwright.sync_api import Page, expect


class BasePage:
    """Базовий клас для всіх сторінок"""
    
    def __init__(self, page: Page):
        """
        Ініціалізація базової сторінки
        
        Args:
            page: Екземпляр Playwright Page
        """
        self.page = page
    
    def goto(self, url: str):
        """Перехід на сторінку"""
        self.page.goto(url)
    
    def get_url(self) -> str:
        """Отримати поточний URL"""
        return self.page.url
    
    def wait_for_load_state(self, state: str = "networkidle"):
        """Чекати завантаження сторінки"""
        self.page.wait_for_load_state(state)
    
    def take_screenshot(self, path: str):
        """Зробити скріншот сторінки"""
        self.page.screenshot(path=path)
