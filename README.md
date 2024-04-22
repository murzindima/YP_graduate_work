# Проектная работа: диплом

## Адрес репозитория

<https://github.com/murzindima/graduate_work>

## Описание проекта

Рекомендательная система для онлайн-кинотеатра. Система рекомендует фильмы пользователям на основе их предпочтений и предыдущих просмотров. Если пользователь не имеет истории просмотров, система предлагает ему популярные или новые фильмы.

## Инструкция по запуску

1. Клонировать репозиторий на локальную машину командой `git clone https://github.com/murzindima/graduate_work.git`
2. Перейти в директорию проекта командой `cd graduate_work`
3. Запустить docker-compose командой `docker-compose up --build`
4. Перейти на <http://localhost:90/api/openapi> для просмотра документации по API сервиса Recommendations

`*` При первом запуске необходимо дождаться инициализации базы данных и загрузки данных

`**` Для простоты проверки работоспособности по согласованию с наставником на некоторых ручках API была отключена авторизация и сервис авторизации не был подключен

`***` Для проверки работоспособности рекомендаций можно воспользоваться скриптом в директории `recommendations/sqlite2mongo` для переноса данных из SQLite в MongoDB. Файл SQLite базы данных взят из теории первых спринтов. Скрипт наполнит MongoDB случайными данными, но с реальными ID фильмов. Для конфигурации скрипта требуется две переменные окружения: `SQLITE_FILE` -- путь к файлу SQLite базы данных (по умолчанию файл ищется в каталоге откуда запускается скрипт) и `UGC_API_URL` -- URL API сервиса UGC (по умолчанию <http://localhost:60/api/v1/movies>). Cкрипт можно запустить командой `python3 main.py`

## Сервисы

**Сервисы проекта Movies:**

- PostgreSQL -- база данных для хранения информации о фильмах
- Elasticsearch -- поисковый движок для поиска фильмов
- Redis -- кэш для хранения информации о фильмах
- ETL -- сервис для загрузки данных о фильмах в базу данных из PostgreSQL в Elasticsearch
- API -- сервис для работы с фильмами на основе FastAPI
- NGINX -- прокси-сервер для обработки запросов к API

**Сервисы проекта UGC:**

- MongoDB -- база данных для хранения информации об UGC
- Mongo Express -- веб-интерфейс для работы с базой данных (креды admin:pass)
- API -- сервис для работы с UGC на основе FastAPI
- NGINX -- прокси-сервер для обработки запросов к API

**Сервисы проекта Recommendations:**

- MongoDB -- база данных для хранения информации о рекомендациях
- Mongo Express -- веб-интерфейс для работы с базой данных (креды admin:pass)
- API -- сервис для работы с рекоммендациями на основе FastAPI
- NGINX -- прокси-сервер для обработки запросов к API

## Внутреннние и внешние порты

### Внешие порты

- 8081 -- порт для доступа к Mongo Express сервиса UGC
- 8091 -- порт для доступа к Mongo Express сервиса Recommendations
- 60 -- порт для доступа к API сервиса UGC
- 70 -- порт для доступа к API сервиса Movies
- 90 -- порт для доступа к API сервиса Recommendations

### Внутренние порты

- 27017 -- порт для MongoDB
- 8081 -- порт для Mongo Express
- 9200 -- порт для Elasticsearch
- 6379 -- порт для Redis
- 5432 -- порт для PostgreSQL
- 80 -- порт для NGINX
- 8003 -- порт для API сервиса Movies
- 8005 -- порт для API сервиса UGC
- 7070 -- порт для API сервиса Recommendations

Можно изменить порты в файле `.env`

## Переменные окружения

Необходимо создать файл `.env` в корне проекта и изменить переменные окружения на свои значения по необходимости.

Пример файла `.env` можно найти в файле `.env.example`

## Структура репозитория

- .github -- директория для хранения файлов GitHub Actions
- movies -- директория для сервиса Movies
  - etl -- директория для сервиса ETL
  - fastapi_movies -- директория для сервиса API
  - nginx -- директория для конфигурации NGINX
  - postgres_movies -- директория в которой хранится DDL для базы данных PostgreSQL
  - sqlite_to_postgres -- директория для скрипта для переноса данных из SQLite в PostgreSQL
- ugc_service -- директория для сервиса UGC
  - src -- директория для исходного кода сервиса UGC
  - nginx -- директория для конфигурации NGINX
- recommendations -- директория для сервиса Recommendations
  - src -- директория для исходного кода сервиса Recommendations
  - nginx -- директория для конфигурации NGINX
  - sqlite2mongo -- директория для скрипта для переноса данных из SQLite в MongoDB
- docker-compose.yml -- файл для запуска всех сервисов
- .env.example -- пример файла с переменными окружения
- README.md -- файл с описанием проекта

## Используемые библиотеки

- fastapi -- фреймворк для создания API
- pydantic -- библиотека для валидации данных
- motor -- асинхронный драйвер для работы с MongoDB
- pandas -- библиотека для работы с данными
- scikit-learn -- библиотека для машинного обучения

## Локаьная разработка

Пререквизит -- poetry
Также убедитесь, что у вас установлены запущены сервисы MongoDB и UGC
Для локальной разработки необходимо:

1. Перейти в директорию сервиса
2. Запустить виртуальное окружение командой `poetry shell`
3. Установить зависимости командой `poetry install`

Запустить сервис можно командой `poetry run uvicorn src.main:app --reload`

Либо можно использовать docker-compose командой `docker-compose up --build` в корне проекта и при необходимости перезапустить сервис командой `docker-compose restart recommendations`
