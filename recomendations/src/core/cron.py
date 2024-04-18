import requests
import argparse

from src.core.config import settings


def arg():
    parser = argparse.ArgumentParser(description='Формирование данных по рекомендациям')
    parser.add_argument('type',
                        type=str,
                        help='Вид рекомендации (новинки, лучшие, подбор рекомендаций от пользователей)',
                        choices=['new', 'best', 'similar'])

    args = parser.parse_args()
    return args


def get_data(endpoint):
    """Выполнение эндпоинтов"""
    try:
        response = requests.get(endpoint)
        response.raise_for_status()  # Бросит исключение для статусов 4xx и 5xx

    except requests.RequestException as e:
        print(f"Ошибка при запросе к API: {e}")


if __name__ == '__main__':
    args = arg()
    type = args.type
    if type == 'new':
        url = settings.new_recommendation_endpoint
    elif type == 'best':
        url = settings.best_recommendation_endpoint
    elif type == 'similar':
        url = settings.similar_recommendation_endpoint
    else:
        url = ''

    get_data(url)
