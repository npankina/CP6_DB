import logging
import os
# import tempfile

# Получаем текущую рабочую директорию
log_dir = os.path.dirname(os.path.abspath(__file__))

# Альтернатива: Используем временную системную директорию
# log_dir = tempfile.gettempdir()

log_file = os.path.join(log_dir, 'application.log')

# Настройка логгера для всего приложения
logger = logging.getLogger("ApplicationLogger")
logger.setLevel(logging.INFO)

# Создание обработчика для записи в файл
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_handler.setLevel(logging.INFO)

# Форматирование логов
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
file_handler.setFormatter(formatter)

# Добавляем обработчик к логгеру
logger.addHandler(file_handler)

# Настройка логирования
logging.basicConfig(
    filename=log_file,  # Используем файл в директории проекта или временной директории
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)