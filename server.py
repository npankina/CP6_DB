from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from logger import logger  # Импорт общего логгера

app = Flask(__name__)
CORS(app)

# Фейковые данные пользователей
users = {
    "admin": {"password": "0000", "role": "admin"},
    "manager": {"password": "1111", "role": "manager"},
    "supplier": {"password": "2222", "role": "supplier"}
}

def connect_to_db():
    conn = psycopg2.connect(
        dbname="warehouse",
        user="admin",
        password="0000",
        host="localhost",
        port="5432"
    )
    return conn


# Маршрут для аутентификации
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Проверка пользователя в фейковых данных
    if username in users and users[username]['password'] == password:
        return jsonify({"username": username, "role": users[username]['role']}), 200
    else:
        return jsonify({"error": "Неверный логин или пароль"}), 401


@app.route('/orders', methods=['GET'])
def get_orders():
    try:
        conn = connect_to_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM orders")
        orders = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(orders), 200
    except Exception as e:
        logger.error(f"Ошибка при получении списка заявок: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    store_id = data['store_id']
    total_sum = data['total_sum']
    status = data['status']

    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orders (store_id, total_sum, status) VALUES (%s, %s, %s)",
                       (store_id, total_sum, status))
        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"Создана новая заявка с ID магазина {store_id}")
        return jsonify({'message': 'Заявка создана'}), 201
    except Exception as e:
        logger.error(f"Ошибка при создании заявки: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/supplies', methods=['GET'])
def get_supplies():
    try:
        conn = connect_to_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT s.id, p.name AS product_name, s.amount, s.supply_date FROM supplies s JOIN products p ON s.product_id = p.id")
        supplies = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(supplies), 200
    except Exception as e:
        logger.error(f"Ошибка при получении списка поставок: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/supplies', methods=['POST'])
def create_supply():
    data = request.get_json()
    product_id = data['product_id']
    amount = data['amount']

    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO supplies (product_id, amount) VALUES (%s, %s)",
                       (product_id, amount))
        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"Добавлена новая поставка для товара ID {product_id}")
        return jsonify({'message': 'Поставка добавлена'}), 201
    except Exception as e:
        logger.error(f"Ошибка при добавлении поставки: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logger.info("Сервер запущен")
    app.run(host='0.0.0.0', port=5000, debug=True)
