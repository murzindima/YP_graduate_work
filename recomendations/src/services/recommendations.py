import json
import random
from collections import defaultdict

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from fastapi import Depends
from aiohttp import ClientSession

from core.config import settings
from core.exceptions import UserNotFoundtExeption
from services.mongo_storage import (
    MongoStorage,
    get_user_movie_storage,
    get_similarity_storage,
    get_new_movies_storage,
)
from core.models import FilmShort
from core.logger import logger


class RecommendationsService:
    def __init__(
        self,
        user_movie_collection: MongoStorage,
        similarity_collection: MongoStorage,
        new_movies_collection: MongoStorage,
    ) -> None:
        self.user_movie_collection = user_movie_collection
        self.similarity_collection = similarity_collection
        self.new_movies_collection = new_movies_collection

    async def refresh_matrices(self) -> None:
        """Создание/обновление существующих матриц."""
        raw_data = await self._fetch_movies_data(settings.ugc_movies_endpoint)
        df_likes = self._process_data(raw_data)

        # Создание матрицы "пользователь-фильм"
        user_movie_matrix = df_likes.pivot_table(
            index="user_id", columns="movie_id", values="rating", fill_value=0
        )
        # Преобразование в нужный формат и сохранение в коллекцию
        user_movie_records = []
        for user_id, row in user_movie_matrix.iterrows():
            user_movie_data = {
                "_id": user_id,  # Устанавливаем user_id как _id
                "movies": [],  # Список фильмов и рейтингов
            }
            for movie_id, rating in row.items():
                user_movie_data["movies"].append(
                    {"movie_id": movie_id, "rating": rating}
                )
            user_movie_records.append(user_movie_data)
        await self.user_movie_collection.delete_all()
        await self.user_movie_collection.insert_many(user_movie_records)

        # Вычисление косинусного сходства между пользователями
        similarity_matrix = pd.DataFrame(
            cosine_similarity(user_movie_matrix),
            index=user_movie_matrix.index,
            columns=user_movie_matrix.index,
        )
        # Преобразование в нужный формат и сохранение в коллекцию user_similarity
        similarity_records = []
        for user_id, row in similarity_matrix.iterrows():
            similarity_data = {
                "_id": user_id,  # Устанавливаем user_id как _id
                "similar_users": [],  # Список схожих пользователей и их similarity
            }
            for other_user_id, similarity in row.items():
                similarity_data["similar_users"].append(
                    {"user_id": other_user_id, "similarity": similarity}
                )
            similarity_records.append(similarity_data)
        await self.similarity_collection.delete_all()
        await self.similarity_collection.insert_many(similarity_records)
        # Получаем список новых фильмов и сохраняем в коллекцию
        new_movies_list = await self._get_new_movies_list(user_movie_matrix)
        new_movies_records = []
        for uuid in new_movies_list:
            record = {"_id": uuid}
            new_movies_records.append(record)
        await self.new_movies_collection.delete_all()
        if new_movies_records:
            await self.new_movies_collection.insert_many(new_movies_records)

    async def get_recommendations(self, user_id: str) -> list[FilmShort]:
        """Получение списка рекомендаций с учетом лучших фильмов."""
        try:
            # получение матриц
            user_movie_matrix, similarity_matrix = await self._fetch_matrices()
            # Получаем список movies_uuid по популярности:
            best_movies_list = self._get_average_ratings(user_movie_matrix)
            # получаем список новых фильмов
            new_movies_list = await self.new_movies_collection.distinct("_id")
            # Находим схожих пользователей
            similar_users = similarity_matrix[user_id].sort_values(
                ascending=False
            )[1 : (settings.num_similar_users + 1)]  # исключая самого себя
            # Собираем рекомендации от схожих пользователей
            recommended_movies = defaultdict(float)
            for other_user, similarity in similar_users.items():
                for movie, rating in user_movie_matrix.loc[other_user].items():
                    if (
                        rating > 0
                        and user_movie_matrix.at[user_id, movie] == 0
                    ):  # фильм понравился другому и не смотрел целевой
                        recommended_movies[movie] += similarity * rating
            # Сортировка рекомендаций
            recommended_movies_sorted = sorted(
                recommended_movies.items(), key=lambda x: x[1], reverse=True
            )
            # Возвращаем топ рекомендаций
            recommended_movies_list = [
                movie for movie, _ in recommended_movies_sorted
            ]
            movies_uuid = self._get_uuid_list(
                recommended_movies_list, best_movies_list, new_movies_list
            )
            # получаем данные по фильмам из movies
            movies_data = await self._fetch_movies_data_by_uuid(
                movies_uuid[: settings.num_recommendations]
            )
            # сортируем результат
            recommendations = self._sort_movies(movies_uuid, movies_data)
            return recommendations
        except KeyError as exc:
            raise UserNotFoundtExeption from exc

    async def _get_all_movies_uuid(self) -> list[str]:
        """Получение всех UUID фильмоы из movies."""
        async with ClientSession() as session:
            try:
                async with session.get(settings.movies_uuid_endpoint) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data
            except Exception as e:
                logger.error(f"Ошибка при запросе к API: {e}")
                return []

    async def _get_new_movies_list(self, user_movie_matrix) -> list[str]:
        """Получение списка киноновинок."""
        # получаем список всех фильмов в movies
        all_movies = await self._get_all_movies_uuid()
        # получаем список всех фильмов, на которые есть отзывы
        movie_ids = user_movie_matrix.columns.tolist()
        # Преобразование списка UUID фильмов из all_movies в множество
        all_movies_set = set(all_movies)
        # Преобразование списка movie_ids в множество
        movie_ids_set = set(movie_ids)
        # Получение списка фильмов, которые есть в all_movies, но отсутствуют в movie_ids
        new_movies_list = list(all_movies_set - movie_ids_set)
        return new_movies_list

    def _get_uuid_list(
        self, recommended_movies_list, best_movies_list, new_movies_list
    ) -> set[str]:
        """Получение списка UUID фильмов для рекомендаций."""
        min_recommendations = (
            settings.num_recommendations
            - settings.min_best_movies_in_recommendations
            - settings.min_new_movies_in_recommendations
        )
        movies_uuid = set()
        # Добавляем фильмы из recommended_movies_list
        movies_uuid.update(recommended_movies_list[:min_recommendations])
        # Добавляем фильмы из best_movies_list
        movies_uuid.update(
            best_movies_list[: settings.min_best_movies_in_recommendations]
        )
        # Добавляем фильмы из new_movies_list
        movies_uuid.update(
            new_movies_list[: settings.min_new_movies_in_recommendations]
        )

        # Если какой-то из списков пуст или содержит меньше требуемого количества,
        # добавляем фильмы из других списков
        total_movies = len(movies_uuid)
        if total_movies < settings.num_recommendations:
            need_to_add = settings.num_recommendations - total_movies
            if (
                need_to_add
                <= len(recommended_movies_list) - min_recommendations
            ):
                movies_uuid.update(
                    recommended_movies_list[
                        min_recommendations : min_recommendations + need_to_add
                    ]
                )
                need_to_add = 0
            else:
                movies_uuid.update(
                    recommended_movies_list[min_recommendations:]
                )
                need_to_add -= (
                    len(recommended_movies_list) - min_recommendations
                )

            if need_to_add > 0 and best_movies_list:
                movies_uuid.update(best_movies_list[:need_to_add])
                need_to_add = max(0, need_to_add - len(best_movies_list))

            if need_to_add > 0 and new_movies_list:
                movies_uuid.update(new_movies_list[:need_to_add])
                need_to_add = 0

        return movies_uuid

    def _get_average_ratings(self, user_movie_matrix) -> list[str]:
        """Получение списка UUID фильмов отсортированных по рейтингу."""
        # Вычисление среднего рейтинга для каждого фильма
        average_ratings = user_movie_matrix.mean()
        # Преобразование результатов в словарь
        average_ratings_dict = average_ratings.to_dict()
        # Сортировка фильмов по среднему рейтингу в порядке убывания
        sorted_movies = sorted(
            average_ratings_dict.items(), key=lambda x: x[1], reverse=True
        )
        # Возвращаем список UUID фильмов в порядке убывания среднего рейтинга
        sorted_movie_uuids = [movie_id for movie_id, _ in sorted_movies]
        return sorted_movie_uuids

    def _sort_movies(
        self, movies_uuid: list[str], movies_data: list[FilmShort]
    ) -> list[FilmShort]:
        """Сотрировка фильмов в порядке, как предоставленно рекомендациями."""
        # Создаем словарь для быстрого доступа к данным фильма по его UUID
        movies_data_dict = {
            movie_data["uuid"]: movie_data for movie_data in movies_data
        }
        # проверяем что все фильмы для рекомендаций присутствуют в movies
        absent_films = set(movies_uuid) - set(movies_data_dict.keys())
        if not absent_films:
            other_films = [
                random.sample(list(set(movies_data_dict.keys()) - set(movies_uuid)), len(absent_films))
            ]

        # Создаем список рекомендаций из данных фильмов в нужном порядке
        recommendations = []
        for movie_uuid in movies_uuid:
            try:
                recommendations.append(movies_data_dict[movie_uuid])
            except KeyError:
                recommendations.append(movies_data_dict[other_films.pop()])
                logger.error(f"Не нашлось в коллекции фильма с uuid={movie_uuid}")

        return recommendations

    async def _fetch_movies_data(self, endpoint):
        """Получение данных из UGC"""
        async with ClientSession() as session:
            try:
                async with session.get(endpoint) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data
            except Exception as e:
                logger.error(f"Ошибка при запросе к API: {e}")
                return []

    async def _fetch_movies_data_by_uuid(
        self, movies_uuid: list
    ) -> list[FilmShort]:
        """Получение данных по фильмам из Movies"""
        async with ClientSession() as session:
            try:
                data = json.dumps(movies_uuid)
                async with session.post(
                    settings.movies_endpoint, data=data
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data
            except Exception as e:
                logger.error(f"Ошибка при запросе к API: {e}")
                return []

    def _process_data(self, raw_data):
        """Преобразование данных в DataFrame."""
        users = []
        movies = []
        ratings = []

        for movie in raw_data:
            movie_id = movie["_id"]
            if "likes" in movie:
                for like in movie["likes"]:
                    users.append(like["user_id"])
                    movies.append(movie_id)
                    ratings.append(like["rating"])

        df = pd.DataFrame(
            {"user_id": users, "movie_id": movies, "rating": ratings}
        )
        return df

    async def _fetch_matrices(self):
        """Получение матриц из хранилища."""
        # Извлечение user_movie_matrix
        user_movie_data = await self.user_movie_collection.get_list()
        # Создаем список словарей
        data_list = []
        for user in user_movie_data:
            for movie in user["movies"]:
                data_list.append(
                    {
                        "user_id": user["_id"],
                        "movie_id": movie["movie_id"],
                        "rating": movie["rating"],
                    }
                )
        # Создаем DataFrame из списка словарей
        user_movie_df = pd.DataFrame(data_list)
        user_movie_matrix = user_movie_df.pivot(
            index="user_id", columns="movie_id", values="rating"
        )
        # Извлечение similarity_matrix
        similarity_data = await self.similarity_collection.get_list()
        # Создаем список словарей
        data_list = []
        for user in similarity_data:
            for similar_user in user["similar_users"]:
                data_list.append(
                    {
                        "user_id": user["_id"],
                        "other_user": similar_user["user_id"],
                        "similarity": similar_user["similarity"],
                    }
                )
        similarity_df = pd.DataFrame(data_list)
        similarity_matrix = similarity_df.pivot(
            index="user_id", columns="other_user", values="similarity"
        )
        return user_movie_matrix, similarity_matrix


def get_recommendations_service(
    user_movie_collection: MongoStorage = Depends(get_user_movie_storage),
    similarity_collection: MongoStorage = Depends(get_similarity_storage),
    new_movies_collection: MongoStorage = Depends(get_new_movies_storage),
) -> RecommendationsService:
    return RecommendationsService(
        user_movie_collection=user_movie_collection,
        similarity_collection=similarity_collection,
        new_movies_collection=new_movies_collection,
    )
