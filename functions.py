# Метод для центрирования окна
def center_window(window, width=300, height=200):
    # Получаем размеры экрана
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Вычисляем координаты для центра экрана
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    # Устанавливаем размеры окна и его позицию по центру
    window.geometry(f'{width}x{height}+{x}+{y}')


class Config:
    Width = 1000
    Height = 600

    Vendor_url = 'http://localhost:5000/supplies/'
    Orders_url = 'http://localhost:5000/orders'
    Products_url = 'http://localhost:5000/products'
