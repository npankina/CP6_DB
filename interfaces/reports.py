import tkinter as tk
from tkinter import ttk, messagebox
import requests
from logger import logger
from functions import center_window, Config


class Reports_Interface:
    def __init__(self, parent):
        """Инициализация класса отчетов"""
        self.parent = parent  # Ссылка на основной интерфейс
        self.report_tree = ttk.Treeview(self.parent.reports_tab, show='headings')  # Используем существующую вкладку
        self.report_tree.pack(fill=tk.BOTH, expand=True)

    def generate_report_1(self):
        """Отчет #1: Объемы заказов по каждому из товаров за указанный месяц"""
        try:
            month = int(self.month_entry.get().strip() )

            if month is None:
                raise ValueError("Месяц не может быть пустым. Пожалуйста, введите значение от 1 до 12.")

            if month < 1 or month > 12:
                raise ValueError("Месяц должен быть числом от 1 до 12")

            # Отправка запроса с месяцем
            response = requests.get(f"{Config.Reports_url}1", params={'month': month})
            response.raise_for_status()
            data = response.json()

            self.display_report_1(data)

        except ValueError as ve:
            logger.error(f"Ошибка ввода данных: {ve}")
            messagebox.showerror("Ошибка", str(ve))

        except Exception as e:
            logger.error(f"Ошибка при генерации отчета #1: {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить отчет #1")


    def generate_report_2(self):
        """Отчет #2: Товары, отгруженные по магазинам"""
        try:
            response = requests.get(f"{Config.Reports_url}2")
            response.raise_for_status()
            data = response.json()

            self.display_report_2(data)

        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP ошибка при запросе отчета #2: {http_err}")
            messagebox.showerror("Ошибка", f"Ошибка HTTP: {http_err}")

        except Exception as e:
            logger.error(f"Ошибка при генерации отчета #2: {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить отчет #2")


    def generate_report_3(self, report_type):
        """Отчет #3: Остатки на складе и магазины, заказывавшие товары"""
        try:
            # В зависимости от типа запроса выбираем, что запрашивать
            if report_type == 'stock':
                is_stock = True
            elif report_type == 'stores':
                is_stock = False

            response = requests.get(f"{Config.Reports_url}3", params={'is_stock': is_stock})
            response.raise_for_status()
            data = response.json()

            self.display_report_3(data, report_type)

        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP ошибка при запросе отчета #3 ({report_type}): {http_err}")
            messagebox.showerror("Ошибка", f"Ошибка HTTP: {http_err}")

        except Exception as e:
            logger.error(f"Ошибка при генерации отчета #3 ({report_type}): {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить отчет #3")


    def generate_report_4(self):
        """Отчет #4: Полная информация о магазинах, заказывавших определенный товар"""
        try:
            product_name = self.product_entry.get().strip()

            if not product_name:
                raise ValueError("Поле не может быть пустым. Пожалуйста, введите название товара")

            response = requests.get(f"{Config.Reports_url}4", params={'product_name': product_name})
            response.raise_for_status()
            data = response.json()

            logger.info(f"Данные для отчета #4: {data}")
            self.display_report_4(data)

        except Exception as e:
            logger.error(f"Ошибка при генерации отчета #4: {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить отчет #4")


    def generate_report_5(self):
        """Отчет #5: Товары, которые нужно срочно завезти на склад"""
        try:
            response = requests.get(f"{Config.Reports_url}5")
            response.raise_for_status()
            data = response.json()

            self.display_report_5(data)
            logger.info(f"Данные для отчета #5: {data}")

        except Exception as e:
            logger.error(f"Ошибка при генерации отчета #5: {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить отчет #5")


    def generate_report_6(self):
        """Отчет #6: Товары, отпущенные по конкретной накладной"""
        try:
            invoice_id = self.invoice_entry.get().strip()

            if not invoice_id:
                raise ValueError("Поле не может быть пустым. Пожалуйста, введите ID накладной")

            response = requests.get(f"{Config.Reports_url}6", params={'invoice_id': invoice_id})
            response.raise_for_status()
            data = response.json()

            logger.info(f"Данные для отчета #6: {data}")
            self.display_report_6(data)

        except Exception as e:
            logger.error(f"Ошибка при генерации отчета #6: {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить отчет #6")


    def generate_report_7(self):
        """Отчет #7: Товары, входящие в определенный заказ"""
        try:
            response = requests.get(f"{Config.Reports_url}7")
            response.raise_for_status()
            data = response.json()

            self.display_report_7(data)
        except Exception as e:
            logger.error(f"Ошибка при генерации отчета #7: {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить отчет #7")


    def generate_report_8(self):
        """Отчет #8: Заказы, сделанные определенным магазином, и товары, не пользующиеся спросом"""
        try:
            response = requests.get(f"{Config.Reports_url}8")
            response.raise_for_status()
            data = response.json()

            self.display_report_8(data)
        except Exception as e:
            logger.error(f"Ошибка при генерации отчета #8: {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить отчет #8")


    def display_report_1(self, data):
        """Отображение данных отчета #1"""
        # Логируем начало отображения отчета
        logger.info("Начато отображение отчета в Treeview")

        # Очищаем таблицу
        logger.info("Очищаем текущие данные таблицы")
        self.report_tree.delete(*self.report_tree.get_children())

        if data:
            # Логируем количество полученных строк данных
            logger.info(f"Количество строк данных для отображения: {len(data)}")

            # Устанавливаем заголовки столбцов
            columns = ['Название', 'Количество']
            self.report_tree["columns"] = columns

            for col in columns:
                self.report_tree.heading(col, text=col)
                logger.info(f"Добавлен заголовок столбца: {col}")

            # Вставляем строки данных в таблицу
            for row in data:
                values = (row['product_name'], row['total_quantity'])
                self.report_tree.insert("", "end", values=values)

        else:
            logger.info("Данные отсутствуют, показываем сообщение пользователю")
            messagebox.showinfo("Информация", "Нет данных для отображения")

        logger.info("Отображение отчета завершено")


    def display_report_2(self, data):
        """Отображение отчета #2"""
        # Очищаем таблицу
        self.report_tree.delete(*self.report_tree.get_children())

        if data:
            # Устанавливаем правильные заголовки столбцов
            columns = ['Магазин', 'Товар', 'Количество']
            self.report_tree["columns"] = columns

            for col in columns:
                self.report_tree.heading(col, text=col)
                self.report_tree.column(col, width=200)

            # Вставляем строки данных в таблицу
            for row in data:
                values = (row['store_name'], row['product_name'], row['total_quantity'])
                self.report_tree.insert("", "end", values=values)
        else:
            messagebox.showinfo("Информация", "Нет данных для отображения")


    def display_report_3(self, data, is_stock):
        """Отображение отчета #3"""
        # Очищаем таблицу
        self.report_tree.delete(*self.report_tree.get_children())

        if data:
            if is_stock == 'stock':
                # Устанавливаем заголовки для остатков товаров
                columns = ['Товар', 'Количество на складе']
                self.report_tree["columns"] = columns

                for col in columns:
                    self.report_tree.heading(col, text=col)
                    self.report_tree.column(col, width=200)

                # Вставляем данные в таблицу
                for row in data:
                    values = (row['product_name'], row['quantity_in_stock'])
                    self.report_tree.insert("", "end", values=values)

            elif is_stock == 'stores':
                # Устанавливаем заголовки для магазинов, заказавших товары
                columns = ['Товар', 'Магазин', 'Количество заказов']
                self.report_tree["columns"] = columns

                for col in columns:
                    self.report_tree.heading(col, text=col)
                    self.report_tree.column(col, width=200)

                # Вставляем данные в таблицу
                for row in data:
                    values = (row['product_name'], row['store_name'], row['quantity_ordered'])
                    self.report_tree.insert("", "end", values=values)
        else:
            messagebox.showinfo("Информация", "Нет данных для отображения")


    def display_report_4(self, data):
        """Отображение отчета #4"""
        # Очищаем таблицу
        self.report_tree.delete(*self.report_tree.get_children())

        if data:
            # Устанавливаем заголовки столбцов
            columns = ['Магазин', 'Адрес', 'Номер документа', 'Дата документа', 'Количество', 'Контактное лицо',
                       'Email']
            self.report_tree["columns"] = columns

            for col in columns:
                self.report_tree.heading(col, text=col)
                self.report_tree.column(col, width=200)

            # Вставляем строки данных в таблицу
            for row in data:
                values = (
                    row['store_name'],
                    row['full_address'],
                    row['document_number'],
                    row['order_date'],
                    row['amount'],
                    row['contact'],
                    row['email']
                )
                self.report_tree.insert("", "end", values=values)
        else:
            messagebox.showinfo("Информация", "Нет данных для отображения")


    def display_report_5(self, data):
        """Отображение отчета #5: """
        # Очищаем таблицу
        self.report_tree.delete(*self.report_tree.get_children())

        if data:
            # Устанавливаем заголовки столбцов
            columns = ['Наименование', 'Количество на складе', 'Минимальный остаток']
            self.report_tree["columns"] = columns

            for col in columns:
                self.report_tree.heading(col, text=col)
                self.report_tree.column(col, width=200)

            # Вставляем строки данных в таблицу
            for row in data:
                values = (
                    row['product_name'],
                    row['amount'],
                    row['min_amount']
                )
                self.report_tree.insert("", "end", values=values)
        else:
            messagebox.showinfo("Информация", "Нет данных для отображения")


    def display_report_6(self, data):
        """Отображение отчета #6"""
        # Очищаем таблицу
        self.report_tree.delete(*self.report_tree.get_children())

        if data:
            # Устанавливаем заголовки столбцов
            columns = ['Наименование', 'Количество']
            self.report_tree["columns"] = columns

            for col in columns:
                self.report_tree.heading(col, text=col)
                self.report_tree.column(col, width=200)

            # Вставляем строки данных в таблицу
            for row in data:
                values = (
                    row['product_name'],
                    row['quantity']
                )
                self.report_tree.insert("", "end", values=values)
        else:
            messagebox.showinfo("Информация", "Нет данных для отображения")


    def display_report_7(self, data):
        """Отображение отчета #7"""
        # Очищаем таблицу
        self.report_tree.delete(*self.report_tree.get_children())

        if data:
            # Устанавливаем заголовки столбцов
            columns = ['Наименование', 'Количество']
            self.report_tree["columns"] = columns

            for col in columns:
                self.report_tree.heading(col, text=col)
                self.report_tree.column(col, width=200)

            # Вставляем строки данных в таблицу
            for row in data:
                values = (
                    row['product_name'],
                    row['quantity']
                )
                self.report_tree.insert("", "end", values=values)
        else:
            messagebox.showinfo("Информация", "Нет данных для отображения")


    def display_report_8(self, data):
        """Отображение отчета #8"""
        # Очищаем таблицу
        self.report_tree.delete(*self.report_tree.get_children())

        if data:
            # Устанавливаем заголовки столбцов
            columns = ['Наименование', 'Количество']
            self.report_tree["columns"] = columns

            for col in columns:
                self.report_tree.heading(col, text=col)
                self.report_tree.column(col, width=200)

            # Вставляем строки данных в таблицу
            for row in data:
                values = (
                    row['product_name'],
                    row['quantity']
                )
                self.report_tree.insert("", "end", values=values)
        else:
            messagebox.showinfo("Информация", "Нет данных для отображения")


    def create_reports_view(self):
        """Создание интерфейса для отчетов"""
        report_buttons_frame = tk.Frame(self.parent.reports_tab)  # Используем вкладку из родителя
        report_buttons_frame.pack(fill=tk.X, padx=10, pady=5)

        button_width = 30  # Задаем фиксированную ширину кнопок

        # Фрейм для отчета #1 и поля ввода месяца
        report_1_frame = tk.Frame(report_buttons_frame)
        report_1_frame.pack(fill=tk.X, pady=5)

        # Поле для ввода месяца для отчета #1
        tk.Label(report_1_frame, text="Введите месяц (1-12):").pack(side=tk.LEFT, padx=5)
        self.month_entry = tk.Entry(report_1_frame, width=5)
        self.month_entry.pack(side=tk.LEFT, padx=5)

        # Кнопка для отчета #1
        tk.Button(report_1_frame, text="Отчет #1: Объемы заказов по товарам",
                  command=self.generate_report_1).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Кнопка для отчета #2
        tk.Button(report_buttons_frame, text="Отчет #2: Товары, отгруженные по магазинам",
                  command=self.generate_report_2, width=button_width).pack(fill=tk.X)

        # Кнопка для отчета #3
        # Фрейм для кнопок отчета #3, разделенный на два столбца
        report_3_frame = tk.Frame(report_buttons_frame)
        report_3_frame.pack(fill=tk.X, padx=10, pady=5)

        # Кнопка для остатков товаров на складе (левая часть)
        self.stock_button = tk.Button(report_3_frame, text="Сколько остатков товаров на складе?",
                                      command=lambda: self.generate_report_3('stock'))
        self.stock_button.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)

        # Кнопка для магазинов, заказавших товары (правая часть)
        self.stores_button = tk.Button(report_3_frame, text="Какие магазины заказывали имеющиеся товары?",
                                       command=lambda: self.generate_report_3('stores'))
        self.stores_button.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)

        # Фрейм для отчета #4 (поле ввода названия товара + кнопка)
        report_4_frame = tk.Frame(report_buttons_frame)
        report_4_frame.pack(fill=tk.X, pady=5)

        # Поле для ввода названия товара для отчета #4
        tk.Label(report_4_frame, text="Введите название товара:").pack(side=tk.LEFT, padx=5)
        self.product_entry = tk.Entry(report_4_frame, width=20)  # Поле для ввода названия товара
        self.product_entry.pack(side=tk.LEFT, padx=5)

        # Кнопка для генерации отчета #4
        tk.Button(report_4_frame, text="Отчет #4: Информация о магазинах по товару",
                  command=self.generate_report_4).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Кнопка для отчета #5
        tk.Button(report_buttons_frame, text="Отчет #5: Товары, необходимые для завоза",
                  command=self.generate_report_5, width=button_width).pack(fill=tk.X)

        # Кнопка для отчета #6
        report_6_frame = tk.Frame(report_buttons_frame)
        report_6_frame.pack(fill=tk.X, pady=5)

        tk.Label(report_6_frame, text="Введите ID накладной:").pack(side=tk.LEFT, padx=5)
        self.invoice_entry = tk.Entry(report_6_frame, width=20)  # Поле для ввода ID накладной
        self.invoice_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(report_6_frame, text="Отчет #6: Товары по накладной", command=self.generate_report_6).pack(
            side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        tk.Button(report_buttons_frame, text="Отчет #7: Товары в заказе", command=self.generate_report_7,
                  width=button_width).pack(fill=tk.X)
        tk.Button(report_buttons_frame, text="Отчет #8: Заказы магазинов и не пользующиеся спросом товары",
                  command=self.generate_report_8, width=button_width).pack(fill=tk.X)