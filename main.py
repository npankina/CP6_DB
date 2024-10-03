import tkinter as tk
from auth import Auth_App
from logger import logger  # Импорт общего логгера


if __name__ == "__main__":
    root = tk.Tk()
    app = Auth_App(root)  # Инициализация класса авторизации
    logger.info("Приложение запущено")
    root.mainloop()
