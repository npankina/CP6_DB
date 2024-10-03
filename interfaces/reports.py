import tkinter as tk
from tkinter import ttk, messagebox
import requests
from logger import logger
from functions import center_window, Config

class Reports_Interface:
    def __init__(self, root):
        self.root = root
        self.root.title("Интерфейс Отчетов")
        center_window(self.root, Config.Width, Config.Height)

        tab_control = ttk.Notebook(self.root)
        self.products_tab = ttk.Frame(tab_control)
        self.orders_tab = ttk.Frame(tab_control)
        self.supplies_tab = ttk.Frame(tab_control)

        # tab_control.add(self.products_tab, text="Товары")
        # tab_control.add(self.orders_tab, text="Заявки")
        # tab_control.add(self.supplies_tab, text="Поставки")

        # tab_control.pack(expand=1, fill='both')

        # self.create_reports_view()
