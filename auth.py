import requests
import tkinter as tk
from tkinter import messagebox
from interfaces.admin import Admin_Interface
from logger import logger # общий логгер
from functions import center_window, Config


class Auth_App:
    BASE_URL = Config.Base_url

    def __init__(self, root):
        self.root = root
        self.root.title("Вход в систему")
        center_window(self.root, 300, 200)

        self.username_entry = self.create_entry("Логин", 0)
        self.password_entry = self.create_entry("Пароль", 1, show="*")
        username = 'admin'
        password = 'admin_password'  # Можно оставить любой пароль

        self.login_button = self.create_button("Войти", 2, self.authenticate_user)


    def create_entry(self, label, row, show=None):
        from tkinter import Label, Entry
        Label(self.root, text=label).grid(row=row, column=0, padx=10, pady=10)
        entry = Entry(self.root, show=show) if show else Entry(self.root)
        entry.grid(row=row, column=1, padx=10, pady=10)
        return entry


    def create_button(self, label, row, command):
        from tkinter import Button
        button = Button(self.root, text=label, command=command)
        button.grid(row=row, column=1, padx=10, pady=10)
        return button


    def authenticate_user(self):
        """Функция для временной автоматической авторизации от имени администратора"""
        user_data = {
            'username': 'admin',
            'role': 'admin'
        }

        self.open_interface_by_role(user_data['role'])


    def authenticate_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль")
            logger.warning("Попытка входа без логина или пароля")
            return

        try:
            response = requests.post(f'{self.BASE_URL}/login', json={'username': username, 'password': password})
            response.raise_for_status()
            user_data = response.json()

            logger.info(f"Успешный вход: {username}, роль: {user_data['role']}")
            self.open_interface_by_role(user_data['role'])
        except requests.RequestException as e:
            messagebox.showerror("Ошибка", f"Ошибка аутентификации: {e}")
            logger.error(f"Ошибка аутентификации для {username}: {e}")


    def open_interface_by_role(self, role):
        if role == 'admin':
            self.open_admin_interface()
        elif role == 'manager':
            self.open_manager_interface()
        elif role == 'supplier':
            self.open_supplier_interface()
        else:
            messagebox.showerror("Ошибка", "Неизвестная роль")
            logger.warning(f"Неизвестная роль: {role}")


    def open_admin_interface(self):
        logger.info("Открыт интерфейс администратора")
        self.root.withdraw()  # Закрываем окно входа
        admin_window = tk.Toplevel(self.root)
        Admin_Interface(admin_window)


    def open_manager_interface(self):
        logger.info("Открыт интерфейс менеджера")
        self.root.withdraw()
        manager_window = tk.Toplevel(self.root)
        Manager_Interface(manager_window)
    

    def open_supplier_interface(self):
        logger.info("Открыт интерфейс поставщика")
        self.root.withdraw()
        supplier_window = tk.Toplevel(self.root)
        Supplier_Interface(supplier_window)