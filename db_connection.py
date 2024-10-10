import psycopg2
from werkzeug.security import generate_password_hash
from contextlib import contextmanager
from psycopg2.extras import RealDictCursor
from logger import logger  # Импорт общего логгера


db_name = "warehouse"
#--------------------------------------------------------------------------------------------------------------
def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname="warehouse",
            user="admin",
            password="0000",
            host="localhost",
            port="5432",
            client_encoding='WIN1251'  # Установим кодировку Windows-1251 (cp1251)
        )
        logger.info("Подключение к базе данных выполнено успешно")
        return conn

    except Exception as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        return None
#--------------------------------------------------------------------------------------------------------------
def create_user(username, password, role):
    """Добавление нового пользователя в базу данных"""
    hashed_password = generate_password_hash(password)
    try:
        with connect_to_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Создаем пользователя с логином и паролем
                cursor.execute(f"CREATE ROLE {username} WITH LOGIN PASSWORD %s", (hashed_password,))

                # Присваиваем пользователю роль admin или manager
                if role == 'admin':
                    cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {username}")
                    cursor.execute(f"ALTER ROLE {username} WITH SUPERUSER")
                elif role == 'manager':
                    cursor.execute(f"GRANT CONNECT ON DATABASE {db_name} TO {username}")
                    cursor.execute(f"GRANT USAGE ON SCHEMA public TO {username}")
                    cursor.execute(f"GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO {username}")
                    cursor.execute(f"GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {username}")
                    cursor.execute(
                        f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE ON TABLES TO {username}")

                conn.commit()
                logger.info(f"Пользователь {role} успешно добавлен в базу данных.")

    except Exception as e:
        conn.rollback()
        logger.error(f"Ошибка при создании пользователя: {e}")
#--------------------------------------------------------------------------------------------------------------
