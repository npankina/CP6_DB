import tkinter as tk
from tkinter import ttk, messagebox
import requests
from logger import logger
from functions import center_window, Config


class Supplier_Interface:
    def __init__(self, root):
        self.root = root
        self.root.title("Интерфейс поставщика")
        center_window(self.root, Config.Width, Config.Height)

        # Создание вкладок
        tab_control = ttk.Notebook(self.root)
        self.supplies_tab = ttk.Frame(tab_control)
        self.new_supply_tab = ttk.Frame(tab_control)

        tab_control.add(self.supplies_tab, text="Мои поставки")
        tab_control.add(self.new_supply_tab, text="Добавить поставку")
        tab_control.pack(expand=1, fill='both')

        # Отображение данных по поставкам и создание новой поставки
        self.create_supplies_view()
        self.create_new_supply_view()

    # Отображение поставок поставщика
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

            if not supplies:  # Проверка, есть ли данные
                messagebox.showinfo("Информация", "Данных о поставках нет.")
                return

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


    # Создание новой поставки
    def create_new_supply_view(self):
        # Поля для добавления новой поставки
        tk.Label(self.new_supply_tab, text="ID Товара").grid(row=0, column=0, padx=10, pady=10)
        tk.Label(self.new_supply_tab, text="Количество").grid(row=1, column=0, padx=10, pady=10)

        product_id_entry = tk.Entry(self.new_supply_tab)
        amount_entry = tk.Entry(self.new_supply_tab)

        product_id_entry.grid(row=0, column=1, padx=10, pady=10)
        amount_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Button(self.new_supply_tab, text="Добавить поставку", command=lambda: self.save_supply(
            product_id_entry.get(), amount_entry.get())).grid(row=2, column=1, padx=10, pady=10)

    # Сохранение новой поставки
    def save_supply(self, product_id, amount):
        data = {
            'product_id': product_id,
            'amount': amount
        }
        try:
            response = requests.post(f'{Config.Vendor_url}', json=data)
            response.raise_for_status()

            messagebox.showinfo("Успех", "Поставка добавлена")
            logger.info(f"Добавлена новая поставка для товара ID {product_id}")
            self.create_supplies_view()  # Обновление списка поставок
        except Exception as e:
            logger.error(f"Ошибка при добавлении поставки: {e}")
            messagebox.showerror("Ошибка", "Не удалось добавить поставку")
