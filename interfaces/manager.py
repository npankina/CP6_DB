import tkinter as tk
from tkinter import ttk, messagebox
import requests
from logger import logger
from functions import center_window, Config


class Manager_Interface:
    def __init__(self, root):
        self.root = root
        self.root.title("Интерфейс менеджера")
        center_window(self.root, Config.Width, Config.Height)

       # Создание вкладок
        tab_control = ttk.Notebook(self.root)
        self.orders_tab = ttk.Frame(tab_control)
        self.new_order_tab = ttk.Frame(tab_control)

        tab_control.add(self.orders_tab, text="Мои заявки")
        tab_control.add(self.new_order_tab, text="Создать заявку")
        tab_control.pack(expand=1, fill='both')

        # Отображение данных по заявкам и создание новой заявки
        self.create_orders_view()
        self.create_new_order_view()

    # Отображение заявок менеджера
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
            response = requests.get(f'{Config.Orders_url}')
            response.raise_for_status()
            orders = response.json()

            # Логирование успешной загрузки данных
            logger.info(f"Загружено {len(orders)} заявок")

            # Вставка данных в таблицу
            for order in orders:
                tree.insert('', 'end', values=(order['id'], order['store_id'], order['total_sum'], order['status'], order['order_date']))

            # Добавление возможности выбора и отображения деталей заявки
            tree.bind("<Double-1>", lambda event: self.show_order_details(tree))

        except Exception as e:
            logger.error(f"Ошибка при загрузке заявок: {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить заявки")

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

    # Создание новой заявки
    def create_new_order_view(self):
        # Поля для создания новой заявки
        tk.Label(self.new_order_tab, text="ID Магазина").grid(row=0, column=0, padx=10, pady=10)
        tk.Label(self.new_order_tab, text="Сумма").grid(row=1, column=0, padx=10, pady=10)
        tk.Label(self.new_order_tab, text="Статус").grid(row=2, column=0, padx=10, pady=10)

        store_id_entry = tk.Entry(self.new_order_tab)
        total_sum_entry = tk.Entry(self.new_order_tab)
        status_entry = tk.Entry(self.new_order_tab)

        store_id_entry.grid(row=0, column=1, padx=10, pady=10)
        total_sum_entry.grid(row=1, column=1, padx=10, pady=10)
        status_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Button(self.new_order_tab, text="Создать заявку", command=lambda: self.save_order(
            store_id_entry.get(), total_sum_entry.get(), status_entry.get())).grid(row=3, column=1, padx=10, pady=10)

    # Сохранение новой заявки
    def save_order(self, store_id, total_sum, status):
        data = {
            'store_id': store_id,
            'total_sum': total_sum,
            'status': status
        }
        try:
            response = requests.post(f'{Config.Orders_url}', json=data)
            response.raise_for_status()

            messagebox.showinfo("Успех", "Заявка создана")
            logger.info(f"Создана новая заявка с ID магазина {store_id}")
            self.create_orders_view()  # Обновление списка заявок
        except Exception as e:
            logger.error(f"Ошибка при создании заявки: {e}")
            messagebox.showerror("Ошибка", "Не удалось создать заявку")
