import tkinter as tk
from tkinter import ttk, messagebox
import requests

from interfaces.base import Base_Interface


class Manager_Interface(Base_Interface):
    def __init__(self, root):
        super().__init__(root)
        self.create_new_order_view()

    def create_new_order_view(self):
        # Поля для создания новой заявки
        tk.Label(self.orders_tab, text="ID Магазина").grid(row=0, column=0, padx=10, pady=10)
        tk.Label(self.orders_tab, text="Сумма").grid(row=1, column=0, padx=10, pady=10)
        tk.Label(self.orders_tab, text="Статус").grid(row=2, column=0, padx=10, pady=10)

        store_id_entry = tk.Entry(self.orders_tab)
        total_sum_entry = tk.Entry(self.orders_tab)
        status_entry = tk.Entry(self.orders_tab)

        store_id_entry.grid(row=0, column=1, padx=10, pady=10)
        total_sum_entry.grid(row=1, column=1, padx=10, pady=10)
        status_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Button(self.orders_tab, text="Создать заявку", command=lambda: self.save_order(
            store_id_entry.get(), total_sum_entry.get(), status_entry.get())).grid(row=3, column=1, padx=10, pady=10)

