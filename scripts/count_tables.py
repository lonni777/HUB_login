"""
Одноразовий скрипт: підключення до тестової БД Hub і виведення кількості таблиць.
Використовує TEST_DB_* з .env у корені репозиторію.
"""
import os
import sys
from pathlib import Path

# корінь репозиторію
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "tests-Python"))

from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")

import psycopg2

def main():
    host = os.getenv("TEST_DB_HOST", "")
    port = int(os.getenv("TEST_DB_PORT", "5432"))
    database = os.getenv("TEST_DB_NAME", "")
    user = os.getenv("TEST_DB_USER", "")
    password = os.getenv("TEST_DB_PASSWORD", "")

    if not host or not database:
        print("Помилка: у .env не задані TEST_DB_HOST та/або TEST_DB_NAME.")
        sys.exit(1)

    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user or None,
            password=password or None,
        )
        cur = conn.cursor()
        # Таблиці в схемах public + усі несистемні (без pg_*, information_schema)
        cur.execute("""
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
            ORDER BY table_schema, table_name
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        by_schema = {}
        for schema, name in rows:
            by_schema.setdefault(schema, []).append(name)

        total = len(rows)
        print(f"Всього таблиць у проекті Hub (БД {database}): {total}\n")
        for schema in sorted(by_schema.keys()):
            tables = by_schema[schema]
            print(f"  Схема '{schema}': {len(tables)} таблиць")
            for t in sorted(tables):
                print(f"    - {t}")
    except Exception as e:
        print(f"Помилка підключення до БД: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
