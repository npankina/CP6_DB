import tkinter as tk
import time
from multiprocessing import Process
from logger import logger  # Импорт общего логгера
from server import run_server  # Импортируем функцию запуска сервера Flask
from auth import Auth_App

def start_server():
    """Функция для запуска Flask-сервера"""
    flask_process = Process(target=run_server)  # Запуск Flask-сервера в отдельном процессе
    flask_process.start()
    time.sleep(2)  # Даем время серверу для запуска
    return flask_process

if __name__ == "__main__":
    # Запускаем сервер Flask
    flask_process = start_server()

    # Запуск Tkinter интерфейса
    root = tk.Tk()
    app = Auth_App(root)  # Инициализация класса авторизации
    logger.info("Приложение запущено")
    root.mainloop()

    # Завершаем сервер после закрытия приложения
    flask_process.terminate()
