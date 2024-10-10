import tkinter as tk
from tkinter import ttk, messagebox
import requests
from logger import logger
from functions import center_window, Config

class Reports_Interface:
    def __init__(self, root):
        self.root = root


    def create_reports_view(self, tab_control):
        """Создание вкладки для отчетов"""
        report_tab = ttk.Frame(tab_control)
        tab_control.add(report_tab, text="Отчеты")

        frame = ttk.Frame(report_tab)
        frame.pack(fill=tk.BOTH, expand=True)

        # Добавляем кнопки для отчетов
        btn_orders_volume = tk.Button(frame, text="Объёмы заказов по товарам", command=self.show_orders_volume)
        btn_orders_volume.grid(row=0, column=0, padx=5, pady=5)

        btn_shipped_items = tk.Button(frame, text="Отгруженные товары по магазинам", command=self.show_shipped_items)
        btn_shipped_items.grid(row=1, column=0, padx=5, pady=5)

        btn_stock_remain = tk.Button(frame, text="Остатки товаров на складе", command=self.show_stock_remain)
        btn_stock_remain.grid(row=2, column=0, padx=5, pady=5)

        btn_store_orders = tk.Button(frame, text="Заказы магазинов", command=self.show_store_orders)
        btn_store_orders.grid(row=3, column=0, padx=5, pady=5)

        btn_urgent_supply = tk.Button(frame, text="Товары, требующие срочной доставки", command=self.show_urgent_supply)
        btn_urgent_supply.grid(row=4, column=0, padx=5, pady=5)

        btn_invoice_details = tk.Button(frame, text="Товары по накладной", command=self.show_invoice_details)
        btn_invoice_details.grid(row=5, column=0, padx=5, pady=5)

        btn_store_report = tk.Button(frame, text="Все заказы магазина", command=self.show_store_report)
        btn_store_report.grid(row=6, column=0, padx=5, pady=5)

        btn_unpopular_items = tk.Button(frame, text="Непопулярные товары", command=self.show_unpopular_items)
        btn_unpopular_items.grid(row=7, column=0, padx=5, pady=5)


    def show_orders_volume(self):
        """Показать объёмы заказов по товарам"""
        self.fetch_and_display_report(Config.Report_orders_volume_url, "Объёмы заказов по товарам")


    def show_shipped_items(self):
        """Показать отгруженные товары по магазинам"""
        self.fetch_and_display_report(Config.Report_shipped_items_url, "Отгруженные товары по магазинам")

    # Остальные методы отчетов...

    def fetch_and_display_report(self, url, title):
        """Запрос данных с сервера и отображение отчета"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            self.display_report(data, title)
        except Exception as e:
            logger.error(f"Ошибка при загрузке отчета: {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить отчет")


    def display_report(self, data, title):
        """Отображение данных отчета в отдельном окне"""
        report_window = tk.Toplevel(self.root)
        report_window.title(title)
        report_tree = ttk.Treeview(report_window, show='headings')
        report_tree.pack(fill=tk.BOTH, expand=True)

        if data:
            columns = list(data[0].keys())
            report_tree["columns"] = columns
            for col in columns:
                report_tree.heading(col, text=col)

            for row in data:
                report_tree.insert("", "end", values=tuple(row.values()))

        report_window.geometry("800x400")