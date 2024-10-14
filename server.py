import psycopg2
import requests
from flask import Flask, jsonify, request
from psycopg2.extras import RealDictCursor
from flask_cors import CORS

from functions import Config
from logger import logger  # Импорт общего логгера
from db_connection import connect_to_db, create_user, Report_Queries

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
@app.route('/login', methods=['POST'])
def login():
    # Временное решение входа как админ
    return jsonify({"username": "admin", "role": "admin"}), 200

# # Маршрут для аутентификации
# @app.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     username = data.get('username')
#     password = data.get('password')
#
#     # Проверка пользователя в фейковых данных
#     if username in users and users[username]['password'] == password:
#         return jsonify({"username": username, "role": users[username]['role']}), 200
#         logger.info(f"Успешный вход в систему. Пользователь: {users[username]['role']}")
#     else:
#         logger.error(f"Ошибка входа в систему. Пользователь: {users[username]['role']}")
#         return jsonify({"error": "Неверный логин или пароль"}), 401
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
                query = """
                    SELECT o.id, o.document_number, o.order_date, o.total_sum, s.name AS store_name, o.status
                    FROM Orders o
                    JOIN Stores s ON o.store_id = s.id
                """
                cursor.execute(query)
                orders = cursor.fetchall()

                logger.info(f"Получено {len(orders)} заявок")
                return jsonify(orders), 200

    except psycopg2.Error as db_error:
        logger.error(f"Ошибка базы данных при получении списка заявок: {db_error}")
        return jsonify({'error': 'Ошибка базы данных'}), 500

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
@app.route('/report_1', methods=['GET'])
def report_1():
    try:
        month = int(request.args.get('month')) # Получаем параметр month из запроса
        logger.info(f"Запрос на отчет #1 для месяца: {month}")

        report_queries = Report_Queries()
        data = report_queries.report_1(month)

        if not data:
            return jsonify({'error': f'Нет данных для месяца {month}'}), 404

        return jsonify(data), 200

    except ValueError as ve:
        logger.error(f"Ошибка в запросе: {ve}")
        return jsonify({'error': str(ve)}), 400

    except Exception as e:
        logger.error(f"Ошибка при генерации отчета #1: {e}")
        return jsonify({'error': 'Не удалось сгенерировать отчет #1'}), 500
#--------------------------------------------------------------------------------------------------------------
@app.route('/report_2', methods=['GET'])
def report_2():
    """Отчет #2: Сколько и каких товаров было отгружено каждому из магазинов"""
    try:
        report_queries = Report_Queries()
        data = report_queries.report_2()

        if not data:
            return jsonify({'message': 'Нет данных для отчета'}), 404

        return jsonify(data), 200

    except Exception as e:
        logger.error(f"Ошибка при генерации отчета #2: {e}")
        return jsonify({'error': 'Не удалось сгенерировать отчет #2'}), 500
#--------------------------------------------------------------------------------------------------------------
@app.route('/report_3', methods=['GET'])
def report_3():
    """Отчет: Остатки на складе или магазины, заказывавшие товары"""
    try:
        is_stock  = request.args.get('is_stock', default='true').lower() == 'true'
        report_queries = Report_Queries()
        data = report_queries.report_3(is_stock)

        if not data:
            return jsonify({'message': 'Нет данных для отчета'}), 404


        return jsonify(data), 200

    except Exception as e:
        logger.error(f"Ошибка при генерации отчета #3: {e}")
        return jsonify({'error': 'Не удалось сгенерировать отчет #3'}), 500
#--------------------------------------------------------------------------------------------------------------
@app.route('/report_4', methods=['GET'])
def report_4():
    try:
        product_name = request.args.get('product_name')
        if not product_name:
            return jsonify({"error": "Необходимо указать имя продукта"}), 400

        report_queries = Report_Queries()
        data = report_queries.report_4(product_name)

        if not data:
            return jsonify({'message': 'Нет данных для отчета'}), 404

        return jsonify(data), 200
    except Exception as e:
        logger.error(f"Ошибка при генерации отчета #4: {e}")
        return jsonify({"error": "Ошибка сервера"}), 500

#--------------------------------------------------------------------------------------------------------------
@app.route('/report_5', methods=['GET'])
def report_5():
    try:
        report_query = Report_Queries()
        data = report_query.report_5()

        if not data:
            return jsonify({'message': 'Нет данных для отчета'}), 404

        return jsonify(data), 200

    except Exception as e:
        logger.error(f"Ошибка при генерации отчета #5: {e}")
        return jsonify({"error": "Ошибка сервера"}), 500
#--------------------------------------------------------------------------------------------------------------
@app.route('/report_6', methods=['GET'])
def report_6():
    try:
        report_query = Report_Queries()
        data = report_query.report_6()

        if not data:
            return jsonify({'message': 'Нет данных для отчета'}), 404

        return jsonify(data), 200

    except Exception as e:
        logger.error(f"Ошибка при генерации отчета #6: {e}")
        return jsonify({"error": "Ошибка сервера"}), 500
#--------------------------------------------------------------------------------------------------------------
@app.route('/report_7', methods=['GET'])
def report_7():
    try:
        report_query = Report_Queries()
        data = report_query.report_7()

        if not data:
            return jsonify({'message': 'Нет данных для отчета'}), 404

        return jsonify(data), 200

    except Exception as e:
        logger.error(f"Ошибка при генерации отчета #7: {e}")
        return jsonify({"error": "Ошибка сервера"}), 500
# #--------------------------------------------------------------------------------------------------------------
@app.route('/report_8', methods=['GET'])
def report_8():
    try:
        report_query = Report_Queries()
        data = report_query.report_8()

        if not data:
            return jsonify({'message': 'Нет данных для отчета'}), 404

        return jsonify(data), 200

    except Exception as e:
        logger.error(f"Ошибка при генерации отчета #8: {e}")
        return jsonify({"error": "Ошибка сервера"}), 500
# --------------------------------------------------------------------------------------------------------------