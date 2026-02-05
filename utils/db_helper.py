"""
Утиліта для роботи з базою даних.
Використовується для очищення тестових даних після виконання тестів.
"""
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from typing import Optional


class DBHelper:
    """Клас для роботи з базою даних"""
    
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        """
        Ініціалізація підключення до БД
        
        Args:
            host: Хост БД
            port: Порт БД
            database: Назва бази даних
            user: Користувач БД
            password: Пароль БД
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
    
    def connect(self):
        """Встановити підключення до БД"""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            return True
        except Exception as e:
            print(f"Помилка підключення до БД: {e}")
            return False
    
    def disconnect(self):
        """Закрити підключення до БД"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def delete_feed_by_id(self, feed_id: str) -> bool:
        """
        Видалити фід з таблиці feed по feed_id.
        Спочатку видаляє фото з feed_image_feed, потім сам фід.
        
        Args:
            feed_id: ID фіду для видалення
        
        Returns:
            True якщо видалення успішне, False якщо ні
        
        Raises:
            Exception: Якщо видалення не вдалося
        """
        if not self.connection:
            if not self.connect():
                raise Exception("Не вдалося підключитися до БД")
        
        try:
            cursor = self.connection.cursor()
            
            # Крок 1: Видалення фото з feed_image_feed
            print(f"Видалення фото для фіду з ID '{feed_id}'...")
            query_images = sql.SQL("DELETE FROM feed_image_feed WHERE feed_id = %s")
            cursor.execute(query_images, (feed_id,))
            images_deleted = cursor.rowcount
            print(f"Видалено {images_deleted} записів з feed_image_feed")
            
            # Крок 2: Видалення самого фіду з feed
            print(f"Видалення фіду з ID '{feed_id}'...")
            query_feed = sql.SQL("DELETE FROM feed WHERE feed_id = %s")
            cursor.execute(query_feed, (feed_id,))
            feed_deleted = cursor.rowcount
            cursor.close()
            
            if feed_deleted > 0:
                print(f"Фід з ID '{feed_id}' успішно видалено з БД")
                return True
            else:
                raise Exception(f"Фід з ID '{feed_id}' не знайдено в БД")
        except Exception as e:
            error_msg = f"Помилка при видаленні фіду з БД: {e}"
            print(error_msg)
            raise Exception(error_msg)
    
    def __enter__(self):
        """Контекстний менеджер: вхід"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстний менеджер: вихід"""
        self.disconnect()
