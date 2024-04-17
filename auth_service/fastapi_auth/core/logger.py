import logging

from aiologger import Logger
from aiologger.handlers.files import AsyncFileHandler
from aiologger.handlers.streams import AsyncStreamHandler
from aiologger.levels import LogLevel

LOG_FILE_NAME = "logs/auth_service.log"

# Создание и настройка логгера
logger = Logger.with_default_handlers(name=__name__)

# Установка уровня логгирования
logger.level = LogLevel.INFO

# Создание обработчика для вывода в консоль
console_handler = AsyncStreamHandler()


# Создание текстового форматтера
class CustomFormatter(logging.Formatter):
    LOG_FORMAT = "{asctime} - {name} - {levelname} - {message}"

    def format(self, record):
        record.asctime = self.formatTime(record, self.datefmt)
        return self.LOG_FORMAT.format(**record.__dict__)


custom_formatter = CustomFormatter()
console_handler.formatter = custom_formatter
logger.add_handler(console_handler)

# Создание обработчика для записи в файл
file_handler = AsyncFileHandler(filename=LOG_FILE_NAME, mode="a")
file_handler.formatter = custom_formatter
logger.add_handler(file_handler)
