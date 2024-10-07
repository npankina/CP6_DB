from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from contextlib import contextmanager
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash
from logger import logger  # Импорт общего логгера

#--------------------------------------------------------------------------------------------------------------
app = Flask(__name__)
CORS(app)
#--------------------------------------------------------------------------------------------------------------
# Фейковые данные пользователей
users = {
    "admin": {"password": "0000", "role": "admin"},
    "manager": {"password": "1111", "role": "manager"},
    "supplier": {"password": "2222", "role": "supplier"}
}
db_name = "warehouse"
#--------------------------------------------------------------------------------------------------------------




# DB functions
#--------------------------------------------------------------------------------------------------------------
def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname="warehouse",
            user="admin",
            password="0000",
            host="localhost",
            port="5432"
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
                cursor.execute(f"CREATE ROLE {username} WITH LOGIN PASSWORD %s", (password,))

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



# Server functions
#--------------------------------------------------------------------------------------------------------------
# Маршрут для аутентификации
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Проверка пользователя в фейковых данных
    if username in users and users[username]['password'] == password:
        return jsonify({"username": username, "role": users[username]['role']}), 200
        logger.info(f"Успешный вход в систему. Пользователь: {users[username]['role']}")
    else:
        logger.error(f"Ошибка входа в систему. Пользователь: {users[username]['role']}")
        return jsonify({"error": "Неверный логин или пароль"}), 401
#--------------------------------------------------------------------------------------------------------------
@app.route('/create_user', methods=['POST'])
def create_user_endpoint():
    data = request.json
    username = data['username']
    password = data['password'] # ? how to store passwords in db
    role = data['role']

    try:
        create_user(username, password, role)
        logger.info(f"Пользователь {username} успешно создан")
        return jsonify({"message": "User created successfully"}), 200

    except Exception as e:
        logger.error(f"Пользователь {username} не создан, возникла ошибка: {str(e)}")
        return jsonify({"error": str(e)}), 400
#--------------------------------------------------------------------------------------------------------------
@app.route('/products', methods=['GET'])
def fetch_all_products():
    try:
        with connect_to_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = "SELECT * FROM Products"
                cursor.execute(query)
                products = cursor.fetchall()

                logger.info(f"Получено {len(products)}  товаров из списка")
                return jsonify(products), 200

    except Exception as e:
        logger.error(f"Ошибка при получении списка товаров: {e}")
        return jsonify({'error': str(e)}), 500
#--------------------------------------------------------------------------------------------------------------
@app.route('/orders', methods=['GET'])
def get_orders():
    try:
        with connect_to_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = "SELECT * FROM orders"
                cursor.execute(query)
                orders = cursor.fetchall()

                logger.info(f"Получено {len(orders)} заявок")
                return jsonify(orders), 200

    except Exception as e:
        logger.error(f"Ошибка при получении списка заявок: {e}")
        return jsonify({'error': str(e)}), 500
#--------------------------------------------------------------------------------------------------------------
@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    store_id = data['store_id']
    total_sum = data['total_sum']
    status = data['status']

    try:
        with connect_to_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = "INSERT INTO orders (store_id, total_sum, status) VALUES (%s, %s, %s)"
                cursor.execute(query, (store_id, total_sum, status))
                conn.commit()

                logger.info(f"Заявка успешно создана")
                return jsonify({'message': 'Заявка создана'}), 201

    except Exception as e:
        logger.error(f"Ошибка при создании заявки: {e}")
        return jsonify({'error': str(e)}), 500
#--------------------------------------------------------------------------------------------------------------
@app.route('/supplies', methods=['GET'])
def get_supplies():
    try:
        with connect_to_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                            SELECT s.id, p.name AS product_name, s.amount, s.supply_date 
                            FROM supplies s 
                            JOIN products p ON s.product_id = p.id
                        """
                cursor.execute(query)
                supplies = cursor.fetchall()

                logger.info("Список поставок получен")
                return jsonify(supplies), 200

    except Exception as e:
        logger.error(f"Ошибка при получении списка поставок: {e}")
        return jsonify({'error': str(e)}), 500
#--------------------------------------------------------------------------------------------------------------
@app.route('/supplies', methods=['POST'])
def create_supply():
    data = request.get_json()
    product_id = data['product_id']
    amount = data['amount']

    try:
        with connect_to_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = "INSERT INTO supplies (product_id, amount) VALUES (%s, %s)"
                cursor.execute(query, (product_id, amount))
                conn.commit()

                logger.info(f"Добавлена новая поставка для товара ID {product_id}")
                return jsonify({'message': 'Поставка добавлена'}), 201

    except Exception as e:
        logger.error(f"Ошибка при добавлении поставки: {e}")
        return jsonify({'error': str(e)}), 500
#--------------------------------------------------------------------------------------------------------------



# Запуск программы
#--------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    logger.info("Сервер запущен")
    app.run(host='0.0.0.0', port=5000, debug=True)
#--------------------------------------------------------------------------------------------------------------