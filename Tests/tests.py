import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify, request

from server import app
class Config:
    Login = '/login'
    Products_url = '/products'

    Connect_db = 'server.connect_to_db'
    Error_connect_db = 'server.connect_to_db'

#--------------------------------------------------------------------------------------------------------------
@pytest.fixture
def valid_user_data():
    """Фикстура для успешных данных входа"""
    return {
        'username': 'admin',
        'password': '0000',
        'role': 'admin'
    }
#--------------------------------------------------------------------------------------------------------------
@pytest.fixture
def invalid_user_data():
    """Фикстура для неудачных данных входа"""
    return {
        'username': 'admin',
        'password': 'wrong_password',
        'role': 'admin'
    }
#--------------------------------------------------------------------------------------------------------------
@pytest.fixture
def client():
    """Фикстура для создания тестового клиента Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client  # Тесты будут использовать этот клиент для отправки запросов
#--------------------------------------------------------------------------------------------------------------
def test_login_success(client, valid_user_data):
    """Тест успешного логина с правильными данными"""
    responce = client.post(Config.Login, json=valid_user_data)
    assert responce.status_code == 200
    data = responce.get_json()
    assert data['username'] == valid_user_data['username']
    assert data['role'] == valid_user_data['role']
#--------------------------------------------------------------------------------------------------------------
def test_login_error(client, invalid_user_data):
    """Тест неудачного логина с неправильным паролем"""
    responce = client.post(Config.Login, json=invalid_user_data)
    assert responce.status_code == 401 # статус код 401 (ошибка аутентификации)
    data = responce.get_json()
    assert data['error'] == 'Неверный логин или пароль'
#--------------------------------------------------------------------------------------------------------------
@pytest.fixture
def mock_db_success():
    """Мок для успешного подключения к базе данных"""
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {"id": 1, "name": "Product 1", "amount": 100, "price": 100.50},
        {"id": 2, "name": "Product 2", "amount": 200, "price": 200.75}
    ]

    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor # конструкция для имитации работы через with

    with patch(Config.Connect_db, return_value=mock_conn):
        yield mock_conn
#--------------------------------------------------------------------------------------------------------------
@pytest.fixture
def mock_db_error():
    """Мок для подключения к базе данных, вызывающего ошибку"""
    with patch(Config.Error_connect_db, side_effect=Exception("Database error")): # с помощью patch, мы временно заменяем функцию connect_to_db, которая находится в модуле server.
        yield # элемент указывает, что этот блок является частью фикстуры
#--------------------------------------------------------------------------------------------------------------
class Test_Product_API:
    @pytest.mark.usefixtures("client", "mock_db_success")
    def test_fetch_all_products_succes(self, client):
        """Тест успешного получения списка товаров"""
        response = client.get(Config.Products_url)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2 # Ожидаем два товара в списке
        assert data[0]['name'] == 'Product 1'
        assert data[1]['name'] == 'Product 2'


    @pytest.mark.usefixtures("client", "mock_db_error")
    def test_fetch_all_products_error(self, client):
        """Тест обработки ошибки при запросе к базе данных"""
        response = client.get(Config.Products_url)
        assert response.status_code == 500
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'Database error'



#--------------------------------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------------------------------
