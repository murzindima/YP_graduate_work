import requests
import backoff

from core.logger import logger
from core.config import settings


@backoff.on_exception(backoff.expo,
                      requests.RequestException,
                      max_time=86400,
                      logger=logger)
def get_data(endpoint):
    """Выполнение эндпоинтов"""

    response = requests.get(endpoint, timeout=5)
    response.raise_for_status()  # Бросит исключение для статусов 4xx и 5xx


if __name__ == '__main__':
    logger.info('START')
    url = f'http://{settings.recommendations_host}:{settings.recommendations_port}{settings.recommendations_endpoint}'
    get_data(url)
    logger.info('FINISH')
