import tkinter as tk
from tkinter import ttk, messagebox
import requests
from logger import logger
from functions import center_window, Config


class Admin_Interface:
    def __init__(self, root):
        self.root = root
        self.root.title("Интерфейс администратора")
        center_window(self.root, Config.Width, Config.Height)

        tab_control = ttk.Notebook(self.root)
        self.products_tab = ttk.Frame(tab_control)
        self.orders_tab = ttk.Frame(tab_control)
        self.supplies_tab = ttk.Frame(tab_control)
        self.users_tab = ttk.Frame(tab_control)

        tab_control.add(self.users_tab, text="Пользователи")
        tab_control.add(self.products_tab, text="Товары")
        tab_control.add(self.orders_tab, text="Заявки")
        tab_control.add(self.supplies_tab, text="Поставки")

        tab_control.pack(expand=1, fill='both')

        self.create_products_view()
        self.create_orders_view()
        self.create_supplies_view()
        self.create_user_view()


    def create_products_view(self):
        tree = ttk.Treeview(self.products_tab, columns=('ID', 'Название', 'Количество', 'Мин. запас'), show='headings')
        tree.heading('ID', text='ID')
        tree.heading('Название', text='Название')
        tree.heading('Количество', text='Количество')
        tree.heading('Мин. запас', text='Мин. запас')
        tree.pack(fill=tk.BOTH, expand=True)

        try:
            response = requests.get(Config.Products_url)
            response.raise_for_status()
            products = response.json()
            logger.info(f"Загружено {len(products)} товаров")

            for product in products:
                tree.insert('', 'end',
                            values=(product['id'], product['name'], product['amount'], product['min_amount']))
        except Exception as e:
            logger.error(f"Ошибка при загрузке товаров: {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить товары")


    # Отображение заявок
    def create_orders_view(self):
        # Создание таблицы (Treeview)
        tree = ttk.Treeview(self.orders_tab, columns=('ID', 'Магазин', 'Сумма', 'Статус', 'Дата'), show='headings')
        tree.heading('ID', text='ID')
        tree.heading('Магазин', text='Магазин')
        tree.heading('Сумма', text='Сумма')
        tree.heading('Статус', text='Статус')
        tree.heading('Дата', text='Дата')
        tree.pack(fill=tk.BOTH, expand=True)

        # Добавление полосы прокрутки для таблицы
        scrollbar = ttk.Scrollbar(self.orders_tab, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        try:
            # Получение данных с сервера
            response = requests.get(Config.Orders_url)
            response.raise_for_status()
            orders = response.json()

            # Логирование успешной загрузки данных
            logger.info(f"Загружено {len(orders)} заявок")

            # Вставка данных в таблицу
            for order in orders:
                tree.insert('', 'end', values=(
                order['id'], order['store_id'], order['total_sum'], order['status'], order['order_date']))

            # Добавление возможности выбора и отображения деталей заявки
            tree.bind("<Double-1>", lambda event: self.show_order_details(tree))

        except Exception as e:
            logger.error(f"Ошибка при загрузке заявок: {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить заявки")

    def create_supplies_view(self):
        tree = ttk.Treeview(self.supplies_tab, columns=('ID', 'Товар', 'Количество', 'Дата поставки'), show='headings')
        tree.heading('ID', text='ID')
        tree.heading('Товар', text='Товар')
        tree.heading('Количество', text='Количество')
        tree.heading('Дата поставки', text='Дата поставки')
        tree.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.supplies_tab, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        try:
            response = requests.get(f'http://localhost:5000/supplies')
            response.raise_for_status()
            supplies = response.json()

            for supply in supplies:
                tree.insert('', 'end',
                            values=(supply['id'], supply['product_name'], supply['amount'], supply['supply_date']))

        except Exception as e:
            logger.error(f"Ошибка при загрузке поставок: {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить поставки")

    def create_user(self, username, password, role):
        try:
            if role == 'admin':
                logger.info(f"Создается администратор: {username}")
            elif role == 'manager':
                logger.info(f"Создается менеджер: {role}")

            messagebox.showinfo("Успех", f"Пользователь {username} с ролью {role} успешно создан!")

        except Exception as e:
            logger.error(f"Ошибка при создании пользователя: {e}")
            messagebox.showerror("Ошибка", f"Ошибка при создании пользователя: {str(e)}")


    def create_user_view(self):
        frame = ttk.Frame(self.users_tab)
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Поле для ввода имени пользователя
        tk.Label(frame, text="Имя пользователя").grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        # Поле для ввода пароля
        tk.Label(frame, text="Пароль").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        # Выбор роли (admin или manager)
        tk.Label(frame, text="Роль").grid(row=2, column=0, padx=5, pady=5)
        self.role_var = tk.StringVar(value="manager")
        tk.Radiobutton(frame, text="Admin", variable=self.role_var, value="admin").grid(row=2, column=1, sticky='w',
                                                                                        padx=5, pady=5)
        tk.Radiobutton(frame, text="Manager", variable=self.role_var, value="manager").grid(row=2, column=1, sticky='e',
                                                                                            padx=5, pady=5)

        # Кнопка для создания пользователя
        tk.Button(frame, text="Создать пользователя", command=self.on_create_user).grid(row=3, column=1, pady=10)


    def create_users_view(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()

        if not username or not password:
            messagebox.showwarning("Ошибка", "Имя пользователя и пароль обязательны для заполнения")
            return

        self.create_user(username, password, role)


    # Отображение деталей выбранной заявки
    def show_order_details(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите заявку для просмотра")
            return

        # Получение данных о выбранной строке
        item = tree.item(selected_item[0])
        order_id = item['values'][0]

        try:
            # Запрос данных по конкретной заявке
            response = requests.get(f'{Config.Orders_url}/{order_id}')
            response.raise_for_status()
            order = response.json()

            # Создание окна с деталями заявки
            details_window = tk.Toplevel(self.root)
            details_window.title(f"Детали заявки #{order_id}")
            details_window.geometry("400x400")

            # Отображение данных
            details = [
                f"ID Заявки: {order['id']}",
                f"Магазин: {order['store_id']}",
                f"Сумма: {order['total_sum']}",
                f"Статус: {order['status']}",
                f"Дата: {order['order_date']}",
                "Товары:"
            ]
            for detail in details:
                tk.Label(details_window, text=detail).pack(pady=5)

            # Отображение товаров в заявке
            for item in order['items']:
                product_info = f"Товар: {item['product_name']}, Количество: {item['amount']}, Цена: {item['price']}"
                tk.Label(details_window, text=product_info).pack(pady=5)

        except Exception as e:
            logger.error(f"Ошибка при получении данных заявки {order_id}: {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить данные заявки")

        # Отображение поставок
        def create_supplies_view(self):
            # Создание таблицы (Treeview)
            tree = ttk.Treeview(self.supplies_tab, columns=('ID', 'Товар', 'Количество', 'Дата поставки'),
                                show='headings')
            tree.heading('ID', text='ID')
            tree.heading('Товар', text='Товар')
            tree.heading('Количество', text='Количество')
            tree.heading('Дата поставки', text='Дата поставки')
            tree.pack(fill=tk.BOTH, expand=True)

            # Добавление полосы прокрутки для таблицы
            scrollbar = ttk.Scrollbar(self.supplies_tab, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side='right', fill='y')

            try:
                # Получение данных с сервера
                response = requests.get(Config.Vendor_url)
                response.raise_for_status()
                supplies = response.json()

                # Логирование успешной загрузки данных
                logger.info(f"Загружено {len(supplies)} поставок")

                # Вставка данных в таблицу
                for supply in supplies:
                    tree.insert('', 'end',
                                values=(supply['id'], supply['product_name'], supply['amount'], supply['supply_date']))

                # Добавление возможности выбора и отображения деталей поставки
                tree.bind("<Double-1>", lambda event: self.show_supply_details(tree))

            except Exception as e:
                logger.error(f"Ошибка при загрузке поставок: {e}")
                messagebox.showerror("Ошибка", "Не удалось загрузить поставки")


        # Отображение деталей выбранной поставки
        def show_supply_details(self, tree):
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showerror("Ошибка", "Выберите поставку для просмотра")
                return

            # Получение данных о выбранной строке
            item = tree.item(selected_item[0])
            supply_id = item['values'][0]

            try:
                # Запрос данных по конкретной поставке
                response = requests.get(f'{Config.Vendor_url}/{supply_id}')
                response.raise_for_status()
                supply = response.json()

                # Создание окна с деталями поставки
                details_window = tk.Toplevel(self.root)
                details_window.title(f"Детали поставки #{supply_id}")
                details_window.geometry("400x300")

                # Отображение данных
                details = [
                    f"ID Поставки: {supply['id']}",
                    f"Товар: {supply['product_name']}",
                    f"Количество: {supply['amount']}",
                    f"Дата поставки: {supply['supply_date']}"
                ]
                for detail in details:
                    tk.Label(details_window, text=detail).pack(pady=5)

            except Exception as e:
                logger.error(f"Ошибка при получении данных поставки {supply_id}: {e}")
                messagebox.showerror("Ошибка", "Не удалось загрузить данные поставки")