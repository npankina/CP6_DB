import psycopg2
from werkzeug.security import generate_password_hash
from contextlib import contextmanager
from psycopg2.extras import RealDictCursor
from datetime import datetime
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
def format_date(date_str):
    """Функция для форматирования даты из строки в нужный формат"""
    try:
        # Преобразуем строку даты в объект datetime
        date_obj = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z")
        # Возвращаем дату в формате "число, месяц, год"
        return date_obj.strftime("%d, %B %Y")  # Например, "28, March 2023"
    except ValueError as e:
        logger.error(f"Ошибка форматирования даты: {e}")
        return date_str  # Возвращаем исходную строку в случае ошибки
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
class Report_Queries:
    """Класс для выполнения запросов к базе данных для отчетов"""

    @staticmethod
    def report_1(month):
        """Отчет #1: Объемы заказов по каждому из товаров за указанный месяц"""
        query = """
            SELECT p.name AS product_name, SUM(oi.amount) AS total_quantity
            FROM products p
            JOIN order_items oi ON p.id = oi.product_id
            JOIN orders o ON o.id = oi.order_id
            WHERE EXTRACT(MONTH FROM o.order_date) = %s
            GROUP BY p.name;
        """
        try:
            conn = connect_to_db()
            cursor = conn.cursor()
            cursor.execute(query, (month,))
            result = cursor.fetchall()

            # Логируем результат запроса
            logger.info(f"Результат запроса для отчета #1: {result}")

            if not result:
                return None
            # Преобразуем результат в список словарей
            data = [{'product_name': row[0], 'total_quantity': row[1]} for row in result]
            return data

        except Exception as e:
            logger.error(f"Ошибка при выполнении запроса к БД для отчета #1: {e}")
            raise

        finally:
            cursor.close()
            conn.close()


    @staticmethod
    def report_2():
        """Отчет #2: Сколько и каких товаров было отгружено каждому из магазинов"""
        query = """
            SELECT s.name AS store_name, p.name AS product_name, SUM(oi.amount) AS total_quantity
            FROM stores s
            JOIN orders o ON s.id = o.store_id
            JOIN order_items oi ON o.id = oi.order_id
            JOIN products p ON oi.product_id = p.id
            GROUP BY s.name, p.name
            ORDER BY s.name, p.name;
        """
        try:
            conn = connect_to_db()
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()

            # Преобразуем результат в список словарей
            data = [{'store_name': row[0], 'product_name': row[1], 'total_quantity': row[2]} for row in result]
            return data

        except Exception as e:
            logger.error(f"Ошибка при выполнении запроса к БД для отчета #2: {e}")
            raise

        finally:
            cursor.close()
            conn.close()


    @staticmethod
    def report_3(is_stock):
        """Отчет #3: Остатки на складе и магазины, заказывавшие товары"""
        if is_stock: # Запрос на остатки товаров на складе
            query = """
                       SELECT p.name AS product_name, p.amount
                       FROM products p
                       WHERE p.amount > 0
                       """
        else: # Запрос на магазины, которые заказывали товары
            query = """
                        SELECT p.name AS product_name, s.name AS store_name, SUM(oi.amount) AS quantity_ordered
                        FROM products p
                        JOIN order_items oi ON p.id = oi.product_id
                        JOIN orders o ON o.id = oi.order_id
                        JOIN stores s ON s.id = o.store_id
                        WHERE p.amount > 0
                        GROUP BY p.name, s.name
                        ORDER BY p.name;
                        """
        try:
            conn = connect_to_db()
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()

            # Форматируем результат
            if is_stock:
                data = [{'product_name': row[0], 'quantity_in_stock': row[1]} for row in result]
            else:
                data = [{'product_name': row[0], 'store_name': row[1], 'quantity_ordered': row[2]} for row in result]

            return data

        except Exception as e:
            logger.error(f"Ошибка при выполнении запроса к БД для отчета #3: {e}")
            raise

        finally:
            cursor.close()
            conn.close()


    @staticmethod
    def report_4(product_name):
        """Отчет #4: Полная информация о магазинах, заказывавших определенный товар"""
        query = """
            SELECT 
                s.name AS store_name, 
                CONCAT(str.street, ', д. ', st.building, ', ', ci.city) AS full_address, 
                o.document_number, 
                o.order_date, 
                oi.amount, 
                c.first_name || ' ' || c.last_name as contact, 
                c.email
            FROM 
                stores s
            JOIN 
                orders o ON s.id = o.store_id
            JOIN 
                order_items oi ON o.id = oi.order_id
            JOIN 
                products p ON oi.product_id = p.id
            JOIN 
                contacts c ON s.contacts_id = c.id
            JOIN 
                addresses st ON s.address_id = st.id
            JOIN 
                streets str ON st.street_id = str.id
            JOIN 
                cities ci ON st.city_id = ci.id
            WHERE 
                p.name ILIKE %s;
        """

        try:
            conn = connect_to_db()
            cursor = conn.cursor()
            cursor.execute(query, (product_name,))
            result = cursor.fetchall()

            data = [{'store_name': row[0],
                     'full_address': row[1],
                     'document_number': row[2],
                     'order_date': row[3],
                     'amount': row[4],
                     'contact': row[5],
                     'email': row[6]} for row in result]
            return data

        except Exception as e:
            logger.error(f"Ошибка при выполнении запроса к БД для отчета #4: {e}")
            raise

        finally:
            cursor.close()
            conn.close()


    @staticmethod
    def report_5():
        """Отчет #5: Товары, которые нужно срочно завезти на склад"""
        query = """
               SELECT p.name AS product_name, p.amount, p.min_amount
               FROM products p
               WHERE p.amount < p.min_amount
           """
        try:
            conn = connect_to_db()
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()

            data = [{'product_name': row[0],
                     'amount': row[1],
                     'min_amount': row[2]} for row in result]
            return data

        except Exception as e:
            logger.error(f"Ошибка при выполнении запроса к БД для отчета #5: {e}")
            raise

        finally:
            cursor.close()
            conn.close()


    @staticmethod
    def report_6(invoice_id):
        """Отчет #6: Товары, отпущенные по конкретной накладной"""
        query = """
               SELECT p.name AS product_name, i.quantity
               FROM products p
               JOIN invoices i ON p.id = i.product_id
               WHERE i.id = %s
           """
        try:
            conn = connect_to_db()
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()

            data = [{'product_name': row[0],
                     'quantity': row[1]} for row in result]
            return data

        except Exception as e:
            logger.error(f"Ошибка при выполнении запроса к БД для отчета #6: {e}")
            raise

        finally:
            cursor.close()
            conn.close()


    @staticmethod
    def report_7(order_id):
        """Отчет #7: Товары, входящие в определенный заказ"""
        query = """
               SELECT p.name AS product_name, o.quantity
               FROM products p
               JOIN order_details o ON p.id = o.product_id
               WHERE o.order_id = %s
           """
        try:
            conn = connect_to_db()
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()

            data = [{'product_name': row[0],
                     'order_details': row[1]} for row in result]
            return data

        except Exception as e:
            logger.error(f"Ошибка при выполнении запроса к БД для отчета #7: {e}")
            raise

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def report_8(store_id):
        """Отчет #8: Заказы, сделанные определённым магазином, и товары, не пользующиеся спросом"""
        query_orders = """
               SELECT p.name AS product_name, o.order_date
               FROM products p
               JOIN orders o ON p.id = o.product_id
               WHERE o.store_id = %s
           """
        query_no_demand = """
               SELECT p.name AS product_name
               FROM products p
               LEFT JOIN orders o ON p.id = o.product_id
               WHERE o.product_id IS NULL
           """

        try:
            conn = connect_to_db()
            cursor = conn.cursor()
            cursor.execute(query_orders)
            result = cursor.fetchall()

            data = [{'product_name': row[0],
                     'order_details': row[1]} for row in result]
            return data

        except Exception as e:
            logger.error(f"Ошибка при выполнении запроса к БД для отчета #8: {e}")
            raise

        finally:
            cursor.close()
            conn.close()
#--------------------------------------------------------------------------------------------------------------