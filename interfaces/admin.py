import tkinter as tk
from tkinter import ttk, messagebox
import requests
from interfaces.base import Base_Interface
from logger import logger
from functions import center_window, Config


class Admin_Interface(Base_Interface):
    def __init__(self, root):
        super().__init__(root)
        # Добавляем вкладку для создания пользователей только для администратора
        self.user_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.user_tab, text="Пользователи")

        # Вызываем метод для создания интерфейса добавления пользователей
        self.create_user_view()


    def create_user_view(self):
        """Создание интерфейса для добавления пользователей"""
        tk.Label(self.user_tab, text="Имя пользователя").grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(self.user_tab)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.user_tab, text="Пароль").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(self.user_tab, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.user_tab, text="Роль").grid(row=2, column=0, padx=5, pady=5)
        self.role_var = tk.StringVar(value="manager")
        tk.Radiobutton(self.user_tab, text="Admin", variable=self.role_var, value="admin").grid(row=2, column=1,
                                                                                                sticky='w', padx=5,
                                                                                                pady=5)
        tk.Radiobutton(self.user_tab, text="Manager", variable=self.role_var, value="manager").grid(row=2, column=1,
                                                                                                    sticky='e', padx=5,
                                                                                                    pady=5)

        # Кнопка "Создать пользователя" размещается на 3-й строке и 1-й колонке
        tk.Button(self.user_tab, text="Создать пользователя", command=self.on_create_user).grid(row=3, column=1,
                                                                                                pady=10)

    def on_create_user(self):
        """Функция для создания нового пользователя"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()

        if not username or not password:
            messagebox.showerror("Ошибка", "Заполните все поля")
            return

        # Логика создания пользователя
        try:
            response = requests.post(Config.Add_User_Url, json={
                'username': username,
                'password': password,
                'role': role
            })
            if response.status_code == 201:
                messagebox.showinfo("Успешно", "Пользователь успешно создан")
            else:
                messagebox.showerror("Ошибка", f"Не удалось создать пользователя: {response.text}")
        except Exception as e:
            logger.error(f"Ошибка создания пользователя: {e}")
            messagebox.showerror("Ошибка", "Произошла ошибка при создании пользователя")

    def show_store_orders(self):
        """Показать заказы магазинов на товары"""
        try:
            # Отправляем запрос на сервер для получения данных
            response = requests.get(f'{Config.Reports_url}/store_orders')
            response.raise_for_status()
            data = response.json()

            # Отображаем данные в окне отчета
            self.display_report(data, "Заказы магазинов на товары")
        except Exception as e:
            logger.error(f"Ошибка при загрузке отчета: {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить отчет")

    def display_report(self, data, title):
        """Отображение данных отчета в отдельном окне"""
        report_window = tk.Toplevel(self.root)
        report_window.title(title)
        report_tree = ttk.Treeview(report_window, show='headings')
        report_tree.pack(fill=tk.BOTH, expand=True)

        # Создаем заголовки колонок на основе ключей данных
        if data:
            columns = list(data[0].keys())
            report_tree["columns"] = columns
            for col in columns:
                report_tree.heading(col, text=col)

            # Вставляем данные в таблицу
            for row in data:
                report_tree.insert("", "end", values=tuple(row.values()))

        report_window.geometry("800x400")
