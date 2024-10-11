import tkinter as tk
from tkinter import ttk, messagebox

import requests

from interfaces.reports import Reports_Interface
from logger import logger
from functions import center_window, Config
from db_connection import connect_to_db


class Base_Interface:
    def __init__(self, root):
        self.root = root
        self.root.title("Интерфейс системы")
        center_window(self.root, Config.Width, Config.Height)


        # Создание вкладок
        self.tab_control = ttk.Notebook(self.root)
        self.products_tab = ttk.Frame(self.tab_control)
        self.orders_tab = ttk.Frame(self.tab_control)
        self.supplies_tab = ttk.Frame(self.tab_control)
        self.reports_tab = ttk.Frame(self.tab_control)  # Вкладка для отчетов


        self.tab_control.add(self.products_tab, text="Товары")
        self.tab_control.add(self.orders_tab, text="Заявки")
        self.tab_control.add(self.supplies_tab, text="Поставки")
        self.tab_control.add(self.reports_tab, text="Отчеты")  # Добавляем вкладку для отчетов

        self.tab_control.pack(expand=1, fill='both')

        # Создаем объект для отчетов
        self.reports = Reports_Interface(self)

        # Отображение данных на вкладках
        self.create_products_view()
        self.create_orders_view()
        self.create_supplies_view()
        self.create_reports_view()  # Создаем интерфейс для отчетов


    def create_reports_view(self):
        """Создание интерфейса для отчетов"""
        self.reports.create_reports_view()


    def create_products_view(self):
        """Создание интерфейса для просмотра и поиска товаров"""
        # Фрейм для строки поиска
        search_frame = tk.Frame(self.products_tab)
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(search_frame, text="Поиск товаров:").pack(side=tk.LEFT, padx=5)
        # Создайте отдельные атрибуты для строки поиска в каждой вкладке
        self.products_search_entry = tk.Entry(search_frame)  # Для вкладки "Товары"
        self.products_search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        search_button = tk.Button(search_frame, text="Найти", command=self.search_products)
        search_button.pack(side=tk.LEFT, padx=5)

        # Таблица товаров
        self.products_tree = ttk.Treeview(self.products_tab, columns=('ID', 'Название', 'Количество', 'Мин. запас'),
                                 show='headings')
        self.products_tree.heading('ID', text='ID')
        self.products_tree.heading('Название', text='Название')
        self.products_tree.heading('Количество', text='Количество')
        self.products_tree.heading('Мин. запас', text='Мин. запас')
        self.products_tree.pack(fill=tk.BOTH, expand=True)

        # Загрузка всех товаров
        self.load_products()


    def load_products(self):
        """Загрузка и отображение всех товаров"""
        try:
            # Запрос к серверу для получения товаров
            response = requests.get(Config.Products_url)
            response.raise_for_status()

            # Сохраняем товары в self.products
            self.products = response.json()

            logger.info(f"Загружено {len(self.products)} товаров")

            # Отображаем товары
            self.display_products(self.products)
        except Exception as e:
            logger.error(f"Ошибка при загрузке товаров: {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить товары")


    def display_products(self, products):
        """Функция для отображения товаров в таблице"""
        print(f"Отображаем {len(products)} товаров")  # Для отладки
        logger.info(f"Отображаем {len(products)} товаров")

        # Очищаем текущие данные в таблице
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)

        # Заполняем таблицу новыми данными
        for product in products:
            self.products_tree.insert('', 'end', values=(
                product['id'], product['name'], product['amount'], product['min_amount']
            ))

        logger.info("Товары успешно отображены.")


    def search_products(self):
        """Функция для поиска товаров по строке"""
        print("Поиск начат")  # Для отладки
        logger.info("Поиск начат")

        search_text = self.products_search_entry.get().strip().lower()  # Используем строку поиска для товаров
        print(f"Поисковый запрос: {search_text}")  # Для отладки
        logger.info(f"Поисковый запрос: {search_text}")

        if search_text:  # Проверяем, что строка поиска не пуста
            # Фильтруем товары по названию
            filtered_products = [product for product in self.products if search_text in product['name'].lower()]
            logger.info(f"Найдено {len(filtered_products)} товаров, соответствующих запросу: {search_text}")

            # Отображаем отфильтрованные товары
            self.display_products(filtered_products)
        else:
            logger.info("Поле поиска пустое. Отображаем все товары.")
            self.display_products(self.products)



    def create_orders_view(self):
        """Создание интерфейса для отображения списка заявок"""
        search_frame = tk.Frame(self.orders_tab)
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(search_frame, text="Поиск заказов по Магазину:").pack(side=tk.LEFT, padx=5)
        self.orders_search_entry = tk.Entry(search_frame)  # Для вкладки "Заявки"
        self.orders_search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        search_button = tk.Button(search_frame, text="Найти", command=self.search_orders_by_store)
        search_button.pack(side=tk.LEFT, padx=5)

        self.orders_tree = ttk.Treeview(self.orders_tab, columns=('ID', 'Магазин', 'Сумма', 'Статус', 'Дата'), show='headings')
        self.orders_tree.heading('ID', text='ID')
        self.orders_tree.heading('Магазин', text='Магазин')
        self.orders_tree.heading('Сумма', text='Сумма')
        self.orders_tree.heading('Статус', text='Статус')
        self.orders_tree.heading('Дата', text='Дата')
        self.orders_tree.pack(fill=tk.BOTH, expand=True)

        self.load_orders()

        try:
            response = requests.get(Config.Orders_url)
            response.raise_for_status()
            orders = response.json()
            logger.info(f"Загружено {len(orders)} заявок")

            for order in orders:
                self.orders_tree.insert('', 'end', values=(
                order['id'], order['store_name'], order['total_sum'], order['status'], order['order_date']))

        except Exception as e:
            logger.error(f"Ошибка при загрузке заявок: {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить заявки")


    def search_orders_by_store(self):
        """Функция для поиска заявок по названию магазина"""
        search_term = self.orders_search_entry.get().strip().lower()  # Получаем данные из строки поиска

        # Отладка: проверяем содержимое строки поиска
        print(f"Текущее содержимое строки поиска: '{search_term}'")
        logger.info(f"Текущее содержимое строки поиска: '{search_term}'")

        if search_term:  # Если строка не пуста
            logger.info(f"Начат поиск заявок по магазину: {search_term}")
            try:
                # Выполняем поиск по названию магазина
                filtered_orders = [order for order in self.orders if search_term in order['store_name'].lower()]
                logger.info(f"Найдено {len(filtered_orders)} заявок для магазина с названием: {search_term}")
                self.display_orders(filtered_orders)
            except Exception as e:
                logger.error(f"Ошибка при фильтрации заказов: {e}")
                messagebox.showerror("Ошибка", f"Ошибка при поиске: {str(e)}")
        else:
            logger.info("Поле поиска пустое. Отображаем все заказы.")
            self.display_orders(self.orders)

    def load_orders(self):
        """Загрузка данных о заявках через серверное API"""
        try:
            # Отправляем запрос на сервер за заказами
            response = requests.get(Config.Orders_url)
            response.raise_for_status()

            # Сохраняем заказы в self.orders
            self.orders = response.json()

            # Логируем количество загруженных заказов
            logger.info(f"Загружено {len(self.orders)} заказов")

            # Отображаем все заказы по умолчанию
            self.display_orders(self.orders)

        except Exception as e:
            logger.error(f"Ошибка при загрузке заказов: {e}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить заказы: {str(e)}")

    def display_orders(self, orders):
        """Функция для отображения заказов в таблице"""
        logger.info(f"Отображаем {len(orders)} заказов")

        try:
            # Очищаем текущие данные в таблице заявок
            for item in self.orders_tree.get_children():
                self.orders_tree.delete(item)

            # Заполняем таблицу новыми данными
            for order in orders:
                self.orders_tree.insert('', 'end', values=(
                    order['id'], order['store_name'], order['total_sum'], order['status'], order['order_date']
                ))

            logger.info("Заказы успешно отображены.")
        except Exception as e:
            logger.error(f"Ошибка при отображении заказов: {e}")
            messagebox.showerror("Ошибка", f"Ошибка при отображении заказов: {str(e)}")


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
            response = requests.get(Config.Vendor_url)
            response.raise_for_status()
            supplies = response.json()
            for supply in supplies:
                tree.insert('', 'end', values=(supply['id'], supply['product_name'], supply['amount'], supply['supply_date']))
        except Exception as e:
            logger.error(f"Ошибка при загрузке поставок: {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить поставки")