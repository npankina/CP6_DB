import tkinter as tk
from tkinter import ttk, messagebox
import requests

# Базовый URL сервера (измените его на ваш адрес)
BASE_URL = 'http://localhost:5000/api'

# Главное окно приложения
class AdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система управления складом")
        self.root.geometry("800x600")

        # Создание меню
        self.create_menu()

        # Создание контейнера для основных разделов
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

    # Функция создания меню
    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        # Раздел меню "Товары"
        product_menu = tk.Menu(menu_bar, tearoff=0)
        product_menu.add_command(label="Просмотр товаров", command=self.view_products)
        product_menu.add_command(label="Добавить товар", command=self.add_product)

        # Раздел меню "Заявки"
        orders_menu = tk.Menu(menu_bar, tearoff=0)
        orders_menu.add_command(label="Просмотр заявок", command=self.view_orders)
        orders_menu.add_command(label="Создать заявку", command=self.create_order)

        # Раздел меню "Поставки"
        supplies_menu = tk.Menu(menu_bar, tearoff=0)
        supplies_menu.add_command(label="Просмотр поставок", command=self.view_supplies)
        supplies_menu.add_command(label="Создать поставку", command=self.create_supply)

        # Добавление разделов меню в главное меню
        menu_bar.add_cascade(label="Товары", menu=product_menu)
        menu_bar.add_cascade(label="Заявки", menu=orders_menu)
        menu_bar.add_cascade(label="Поставки", menu=supplies_menu)

    # Функция отображения товаров (получение данных с сервера)
    def view_products(self):
        self.clear_frame()
        tree = ttk.Treeview(self.main_frame, columns=('ID', 'Название', 'Количество', 'Мин. Запас'), show='headings')
        tree.heading('ID', text='ID')
        tree.heading('Название', text='Название')
        tree.heading('Количество', text='Количество')
        tree.heading('Мин. Запас', text='Мин. Запас')
        tree.pack(fill=tk.BOTH, expand=True)

        response = requests.get(f'{BASE_URL}/products')
        if response.status_code == 200:
            products = response.json()
            for product in products:
                tree.insert('', 'end', values=product)
        else:
            messagebox.showerror("Ошибка", "Не удалось получить список товаров")

    # Функция добавления нового товара
    def add_product(self):
        self.clear_frame()

        tk.Label(self.main_frame, text="Название товара").grid(row=0, column=0)
        tk.Label(self.main_frame, text="Количество").grid(row=1, column=0)
        tk.Label(self.main_frame, text="Мин. запас").grid(row=2, column=0)

        name_entry = tk.Entry(self.main_frame)
        amount_entry = tk.Entry(self.main_frame)
        min_amount_entry = tk.Entry(self.main_frame)

        name_entry.grid(row=0, column=1)
        amount_entry.grid(row=1, column=1)
        min_amount_entry.grid(row=2, column=1)

        tk.Button(self.main_frame, text="Добавить товар", command=lambda: self.save_product(
            name_entry.get(), amount_entry.get(), min_amount_entry.get())).grid(row=3, column=1)

    # Функция сохранения нового товара
    def save_product(self, name, amount, min_amount):
        data = {
            'name': name,
            'amount': amount,
            'min_amount': min_amount
        }
        response = requests.post(f'{BASE_URL}/products', json=data)
        if response.status_code == 201:
            messagebox.showinfo("Успех", "Товар добавлен")
            self.view_products()
        else:
            messagebox.showerror("Ошибка", "Не удалось добавить товар")

    # Функция отображения заявок
    def view_orders(self):
        self.clear_frame()
        tree = ttk.Treeview(self.main_frame, columns=('ID', 'Магазин', 'Сумма', 'Статус', 'Дата'), show='headings')
        tree.heading('ID', text='ID')
        tree.heading('Магазин', text='Магазин')
        tree.heading('Сумма', text='Сумма')
        tree.heading('Статус', text='Статус')
        tree.heading('Дата', text='Дата')
        tree.pack(fill=tk.BOTH, expand=True)

        response = requests.get(f'{BASE_URL}/orders')
        if response.status_code == 200:
            orders = response.json()
            for order in orders:
                tree.insert('', 'end', values=order)
        else:
            messagebox.showerror("Ошибка", "Не удалось получить список заявок")

    # Функция создания новой заявки
    def create_order(self):
        self.clear_frame()

        tk.Label(self.main_frame, text="ID Магазина").grid(row=0, column=0)
        tk.Label(self.main_frame, text="Сумма").grid(row=1, column=0)
        tk.Label(self.main_frame, text="Статус").grid(row=2, column=0)

        store_id_entry = tk.Entry(self.main_frame)
        total_sum_entry = tk.Entry(self.main_frame)
        status_entry = tk.Entry(self.main_frame)

        store_id_entry.grid(row=0, column=1)
        total_sum_entry.grid(row=1, column=1)
        status_entry.grid(row=2, column=1)

        tk.Button(self.main_frame, text="Создать заявку", command=lambda: self.save_order(
            store_id_entry.get(), total_sum_entry.get(), status_entry.get())).grid(row=3, column=1)

    # Функция сохранения заявки
    def save_order(self, store_id, total_sum, status):
        data = {
            'store_id': store_id,
            'total_sum': total_sum,
            'status': status
        }
        response = requests.post(f'{BASE_URL}/orders', json=data)
        if response.status_code == 201:
            messagebox.showinfo("Успех", "Заявка создана")
            self.view_orders()
        else:
            messagebox.showerror("Ошибка", "Не удалось создать заявку")

    # Функция отображения поставок
    def view_supplies(self):
        self.clear_frame()
        tree = ttk.Treeview(self.main_frame, columns=('ID', 'Товар', 'Количество', 'Дата'), show='headings')
        tree.heading('ID', text='ID')
        tree.heading('Товар', text='Товар')
        tree.heading('Количество', text='Количество')
        tree.heading('Дата', text='Дата')
        tree.pack(fill=tk.BOTH, expand=True)

        response = requests.get(f'{BASE_URL}/supplies')
        if response.status_code == 200:
            supplies = response.json()
            for supply in supplies:
                tree.insert('', 'end', values=supply)
        else:
            messagebox.showerror("Ошибка", "Не удалось получить список поставок")

    # Функция создания новой поставки
    def create_supply(self):
        self.clear_frame()

        tk.Label(self.main_frame, text="ID Товара").grid(row=0, column=0)
        tk.Label(self.main_frame, text="Количество").grid(row=1, column=0)

        product_id_entry = tk.Entry(self.main_frame)
        amount_entry = tk.Entry(self.main_frame)

        product_id_entry.grid(row=0, column=1)
        amount_entry.grid(row=1, column=1)

        tk.Button(self.main_frame, text="Создать поставку", command=lambda: self.save_supply(
            product_id_entry.get(), amount_entry.get())).grid(row=2, column=1)

    # Функция сохранения поставки
    def save_supply(self, product_id, amount):
        data = {
            'product_id': product_id,
            'amount': amount
        }
        response = requests.post(f'{BASE_URL}/supplies', json=data)
        if response.status_code == 201:
            messagebox.showinfo("Успех", "Поставка создана")
            self.view_supplies()
        else:
            messagebox.showerror("Ошибка", "Не удалось создать поставку")

    # Очистка фрейма
    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = AdminApp(root)
    root.mainloop()
