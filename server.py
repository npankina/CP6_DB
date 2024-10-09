from multiprocessing import Process
import tkinter as tk
from flask import Flask, jsonify, request
from psycopg2.extras import RealDictCursor
from flask_cors import CORS
import requests
import time
from logger import logger  # Импорт общего логгера
from auth import Auth_App
from db_connection import connect_to_db, create_user

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
#--------------------------------------------------------------------------------------------------------------



# Server functions
#--------------------------------------------------------------------------------------------------------------
def run_server():
    # Запуск сервера Flask на localhost и порту 5000
    app.run(port=5000, debug=False)
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
@app.route('/reports/orders_volume', methods=['GET'])
def orders_volume():
    try:
        with connect_to_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                SELECT product_id, SUM(amount) as total_ordered
                FROM Order_items
                WHERE order_date >= date_trunc('month', current_date)
                GROUP BY product_id
                """
                cursor.execute(query)
                result = cursor.fetchall()
                return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
#--------------------------------------------------------------------------------------------------------------
@app.route('/reports/stock_remain', methods=['GET'])
def stock_remain():
    try:
        with connect_to_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                SELECT p.name, p.amount
                FROM Products p
                WHERE p.amount > 0
                """
                cursor.execute(query)
                result = cursor.fetchall()
                return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
#--------------------------------------------------------------------------------------------------------------
@app.route('/reports/store_orders', methods=['GET'])
def store_orders():
    try:
        with connect_to_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                SELECT store_id, product_id, SUM(amount) as total_ordered
                FROM Order_items
                GROUP BY store_id, product_id
                """
                cursor.execute(query)
                result = cursor.fetchall()
                return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
#--------------------------------------------------------------------------------------------------------------
@app.route('/reports/urgent_supply', methods=['GET'])
def urgent_supply():
    try:
        with connect_to_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                SELECT product_id, name, amount
                FROM Products
                WHERE amount < min_amount
                """
                cursor.execute(query)
                result = cursor.fetchall()
                return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
#--------------------------------------------------------------------------------------------------------------
@app.route('/reports/invoice_details', methods=['GET'])
def invoice_details():
    try:
        with connect_to_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                SELECT invoice_id, product_id, amount, price
                FROM Invoices
                JOIN Order_items ON Invoices.id = Order_items.order_id
                """
                cursor.execute(query)
                result = cursor.fetchall()
                return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
#--------------------------------------------------------------------------------------------------------------
