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
    
    def deactivate_feed_by_id(self, feed_id: str) -> bool:
        """
        Вимкнути фід (встановити is_active = false) в таблиці feed.
        
        Args:
            feed_id: ID фіду для вимкнення
        
        Returns:
            True якщо вимкнення успішне, False якщо ні
        
        Raises:
            Exception: Якщо вимкнення не вдалося
        """
        if not self.connection:
            if not self.connect():
                raise Exception("Не вдалося підключитися до БД")
        
        try:
            cursor = self.connection.cursor()
            
            # Встановлюємо is_active = false для фіду
            print(f"Вимкнення фіду з ID '{feed_id}' (is_active = false)...")
            query = sql.SQL("UPDATE feed SET is_active = false WHERE feed_id = %s")
            cursor.execute(query, (feed_id,))
            rows_updated = cursor.rowcount
            cursor.close()
            
            if rows_updated > 0:
                print(f"Фід з ID '{feed_id}' успішно вимкнено (is_active = false)")
                return True
            else:
                raise Exception(f"Фід з ID '{feed_id}' не знайдено в БД або вже вимкнено")
        except Exception as e:
            error_msg = f"Помилка при вимкненні фіду в БД: {e}"
            print(error_msg)
            raise Exception(error_msg)
    
    def get_feed_url_by_id(self, feed_id: str) -> Optional[str]:
        """
        Отримати URL фіду з таблиці feed по feed_id
        
        Args:
            feed_id: ID фіду
        
        Returns:
            URL фіду або None якщо не знайдено
        
        Raises:
            Exception: Якщо виникла помилка при запиті
        """
        if not self.connection:
            if not self.connect():
                raise Exception("Не вдалося підключитися до БД")
        
        try:
            cursor = self.connection.cursor()
            # Спробуємо різні варіанти назв колонок
            possible_columns = ["feed_url", "url", "xml_url", "source_url"]
            url_value = None
            
            for column_name in possible_columns:
                try:
                    query = sql.SQL("SELECT {} FROM feed WHERE feed_id = %s").format(
                        sql.Identifier(column_name)
                    )
                    cursor.execute(query, (feed_id,))
                    result = cursor.fetchone()
                    if result and result[0]:
                        url_value = result[0]
                        print(f"Знайдено URL в колонці '{column_name}': {url_value}")
                        break
                except Exception as col_error:
                    # Якщо колонка не існує, пробуємо наступну
                    continue
            
            cursor.close()
            
            if url_value:
                return url_value
            else:
                # Якщо не знайдено через колонки, спробуємо отримати всі дані
                cursor = self.connection.cursor()
                query = sql.SQL("SELECT * FROM feed WHERE feed_id = %s LIMIT 1")
                cursor.execute(query, (feed_id,))
                columns = [desc[0] for desc in cursor.description]
                result = cursor.fetchone()
                cursor.close()
                
                if result:
                    print(f"Доступні колонки в таблиці feed: {columns}")
                    # Шукаємо колонку що містить URL
                    for i, col in enumerate(columns):
                        if 'url' in col.lower():
                            url_value = result[i]
                            if url_value:
                                print(f"Знайдено URL в колонці '{col}': {url_value}")
                                return url_value
                
                return None
        except Exception as e:
            error_msg = f"Помилка при отриманні URL фіду з БД: {e}"
            print(error_msg)
            raise Exception(error_msg)
    
    def is_feed_active(self, feed_id: str) -> bool:
        """
        Перевірити чи активний фід (is_active = true) в таблиці feed.

        Args:
            feed_id: ID фіду

        Returns:
            True якщо фід активний, False якщо не активний або не знайдено
        """
        if not self.connection:
            if not self.connect():
                raise Exception("Не вдалося підключитися до БД")

        try:
            cursor = self.connection.cursor()
            # Пробуємо колонку is_active (типово в HUB)
            try:
                query = sql.SQL("SELECT is_active FROM feed WHERE feed_id = %s")
                cursor.execute(query, (feed_id,))
                result = cursor.fetchone()
                cursor.close()
                return result is not None and result[0] is True
            except Exception:
                cursor.close()
                return False
        except Exception as e:
            print(f"Помилка при перевірці is_active фіду: {e}")
            return False

    def feed_exists_by_origin_url(self, url: str) -> bool:
        """
        Перевірити чи існує фід з даним origin_url (або URL що містить цей рядок).
        
        Args:
            url: URL для пошуку (базовий URL без фрагмента #ufeed)
        
        Returns:
            True якщо знайдено запис, False якщо ні
        """
        if not self.connection:
            if not self.connect():
                raise Exception("Не вдалося підключитися до БД")
        
        try:
            cursor = self.connection.cursor()
            base_url = url.split("#")[0].strip()
            query = sql.SQL("SELECT 1 FROM feed WHERE origin_url LIKE %s LIMIT 1")
            cursor.execute(query, (f"%{base_url}%",))
            result = cursor.fetchone()
            cursor.close()
            return result is not None
        except Exception as e:
            print(f"Помилка при перевірці існування фіду по URL: {e}")
            return False
    
    def __enter__(self):
        """Контекстний менеджер: вхід"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстний менеджер: вихід"""
        self.disconnect()
