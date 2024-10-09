import tkinter as tk
from tkinter import ttk, messagebox
import requests
from logger import logger
from functions import center_window, Config


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
        self.tab_control.add(self.reports_tab, text="Отчёты")  # Добавляем вкладку отчетов

        self.tab_control.pack(expand=1, fill='both')

        # Отображение данных на вкладках
        self.create_products_view()
        self.create_orders_view()
        self.create_supplies_view()
        self.create_reports_view()  # Вызываем метод создания интерфейса для отчетов


    def create_products_view(self):
        """Создание интерфейса для просмотра и поиска товаров"""
        # Фрейм для строки поиска
        search_frame = tk.Frame(self.products_tab)
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(search_frame, text="Поиск товаров:").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        search_button = tk.Button(search_frame, text="Найти", command=self.search_products)
        search_button.pack(side=tk.LEFT, padx=5)

        # Таблица товаров
        self.tree = ttk.Treeview(self.products_tab, columns=('ID', 'Название', 'Количество', 'Мин. запас'),
                                 show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Название', text='Название')
        self.tree.heading('Количество', text='Количество')
        self.tree.heading('Мин. запас', text='Мин. запас')
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Загрузка всех товаров
        self.load_products()


    def load_products(self):
        """Загрузка и отображение всех товаров"""
        try:
            response = requests.get(Config.Products_url)
            response.raise_for_status()
            self.products = response.json()
            logger.info(f"Загружено {len(self.products)} товаров")

            # Отображаем товары в таблице
            self.display_products(self.products)
        except Exception as e:
            logger.error(f"Ошибка при загрузке товаров: {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить товары")


    def display_products(self, products):
        """Отображение товаров в таблице"""
        # Очищаем текущую таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Добавляем отфильтрованные товары
        for product in products:
            self.tree.insert('', 'end',
                             values=(product['id'], product['name'], product['amount'], product['min_amount']))


    def search_products(self):
        """Функция для поиска товаров по строке"""
        search_text = self.search_entry.get().lower()
        filtered_products = [product for product in self.products if search_text in product['name'].lower()]

        # Если ничего не найдено
        if not filtered_products:
            messagebox.showinfo("Результаты поиска", "Товары не найдены.")

        # Отображаем отфильтрованные результаты
        self.display_products(filtered_products)


    def create_orders_view(self):
        tree = ttk.Treeview(self.orders_tab, columns=('ID', 'Магазин', 'Сумма', 'Статус', 'Дата'), show='headings')
        tree.heading('ID', text='ID')
        tree.heading('Магазин', text='Магазин')
        tree.heading('Сумма', text='Сумма')
        tree.heading('Статус', text='Статус')
        tree.heading('Дата', text='Дата')
        tree.pack(fill=tk.BOTH, expand=True)

        try:
            response = requests.get(Config.Orders_url)
            response.raise_for_status()
            orders = response.json()
            logger.info(f"Загружено {len(orders)} заявок")

            for order in orders:
                tree.insert('', 'end', values=(
                order['id'], order['store_id'], order['total_sum'], order['status'], order['order_date']))
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
                tree.insert('', 'end', values=(supply['id'], supply['product_name'], supply['amount'], supply['supply_date']))
        except Exception as e:
            logger.error(f"Ошибка при загрузке поставок: {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить поставки")


    def create_reports_view(self):
        """Создаем интерфейс для отчетов"""
        frame = tk.Frame(self.reports_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Кнопки для вызова отчетов
        btn_orders_volume = tk.Button(frame, text="Объёмы заказов по товарам за текущий месяц",
                                      command=self.show_orders_volume)
        btn_orders_volume.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        btn_shipped_items = tk.Button(frame, text="Отгруженные товары по магазинам", command=self.show_shipped_items)
        btn_shipped_items.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        btn_stock_remain = tk.Button(frame, text="Остатки товаров на складе", command=self.show_stock_remain)
        btn_stock_remain.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        btn_store_orders = tk.Button(frame, text="Заказы магазинов на товары", command=self.show_store_orders)
        btn_store_orders.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        btn_urgent_supply = tk.Button(frame, text="Товары, требующие срочной доставки", command=self.show_urgent_supply)
        btn_urgent_supply.grid(row=4, column=0, padx=5, pady=5, sticky="w")

        btn_invoice_details = tk.Button(frame, text="Товары по накладной", command=self.show_invoice_details)
        btn_invoice_details.grid(row=5, column=0, padx=5, pady=5, sticky="w")

        btn_order_items = tk.Button(frame, text="Товары в заказе", command=self.show_orders_volume)
        btn_order_items.grid(row=6, column=0, padx=5, pady=5, sticky="w")

        btn_store_report = tk.Button(frame, text="Все заказы магазина", command=self.show_store_report)
        btn_store_report.grid(row=7, column=0, padx=5, pady=5, sticky="w")

        btn_unpopular_items = tk.Button(frame, text="Товары, не заказанные в текущем месяце",
                                        command=self.show_unpopular_items)
        btn_unpopular_items.grid(row=8, column=0, padx=5, pady=5, sticky="w")

    def show_invoice_details(self):
        """Показать товары по накладной"""
        try:
            response = requests.get(f'{Config.Reports_url}/invoice_details')
            response.raise_for_status()
            data = response.json()

            # Отображаем данные в окне отчета
            self.display_report(data, "Товары по накладной")
        except Exception as e:
            logger.error(f"Ошибка при загрузке отчета: {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить отчет")


    # Методы для отчетов:
    def show_orders_volume(self):
        """Показать объёмы заказов по каждому из товаров на текущий месяц"""
        try:
            response = requests.get(f'{Config.Reports_url}/orders_volume')
            response.raise_for_status()
            data = response.json()
            self.display_report(data, "Объёмы заказов по товарам")
        except Exception as e:
            logger.error(f"Ошибка при загрузке отчета: {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить отчет")


    def show_shipped_items(self):
        """Показать отгруженные товары по каждому магазину"""
        try:
            response = requests.get(f'{Config.Reports_url}/shipped_items')
            response.raise_for_status()
            data = response.json()
            self.display_report(data, "Отгруженные товары")
        except Exception as e:
            logger.error(f"Ошибка при загрузке отчета: {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить отчет")


    def show_stock_remain(self):
        """Показать остатки товаров на складе"""
        try:
            response = requests.get(f'{Config.Reports_url}/stock_remain')
            response.raise_for_status()
            data = response.json()
            self.display_report(data, "Остатки товаров на складе")
        except Exception as e:
            logger.error(f"Ошибка при загрузке отчета: {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить отчет")


    def show_orders_volume(self):
        """Показать объёмы заказов по каждому из товаров на текущий месяц"""
        try:
            response = requests.get(f'{Config.Reports_url}/orders_volume')
            response.raise_for_status()
            data = response.json()
            self.display_report(data, "Объёмы заказов по товарам")
        except Exception as e:
            logger.error(f"Ошибка при загрузке отчета: {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить отчет")


    def show_shipped_items(self):
        """Показать отгруженные товары по каждому магазину"""
        try:
            response = requests.get(f'{Config.Reports_url}/shipped_items')
            response.raise_for_status()
            data = response.json()
            self.display_report(data, "Отгруженные товары по магазинам")

        except Exception as e:
            logger.error(f"Ошибка при загрузке отчета: {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить отчет")


    def show_urgent_supply(self):
        """Показать товары, требующие срочной доставки"""
        try:
            # Отправляем запрос на сервер для получения данных
            response = requests.get(f'{Config.Reports_url}/urgent_supply')
            response.raise_for_status()
            data = response.json()

            # Отображаем данные в окне отчета
            self.display_report(data, "Товары, требующие срочной доставки")
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
