import json
import time
from collections import defaultdict

import pandas as pd
import requests
from sklearn.metrics.pairwise import cosine_similarity
from fastapi import Depends

from core.config import settings
from core.exceptions import UserNotFoundtExeption
from services.mongo_storage import (
    MongoStorage,
    get_user_movie_storage,
    get_similarity_storage,
    get_new_movies_storage,
    get_best_movies_storage,
)
from core.models import FilmShort


class RecommendationsService:
    def __init__(
        self,
        user_movie_collection: MongoStorage,
        similarity_collection: MongoStorage,
        new_movies_collection: MongoStorage,
        best_movies_collection: MongoStorage,
    ) -> None:
        self.user_movie_collection = user_movie_collection
        self.similarity_collection = similarity_collection
        self.new_movies_collection = new_movies_collection
        self.best_movies_collection = best_movies_collection

    async def refresh_new(self) -> None:
        """Создание/обновление данных по новинкам."""
        raw_data = await self._fetch_movies_data(settings.new_movies_endpoint)

        await self.new_movies_collection.delete_all()
        await self.new_movies_collection.insert_many(raw_data)

    async def refresh_best(self) -> None:
        """Создание/обновление данных по лучшим фильмам."""
        raw_data = await self._fetch_movies_data(settings.best_ugc_endpoint)

        await self.best_movies_collection.delete_all()
        await self.best_movies_collection.insert_many(raw_data)

    async def refresh_matrices(self) -> None:
        """Создание/обновление существующих матриц."""
        start_time = time.time()
        raw_data = await self._fetch_movies_data(settings.ugc_movies_endpoint)
        raw_data_time = time.time() - start_time
        df_likes = self._process_data(raw_data)
        df_likes_time = time.time() - start_time

        # Создание матрицы "пользователь-фильм"
        user_movie_matrix = df_likes.pivot_table(
            index="user_id", columns="movie_id", values="rating", fill_value=0
        )
        user_movie_matrix_time = time.time() - start_time
        # Вычисление косинусного сходства между пользователями
        similarity_matrix = pd.DataFrame(
            cosine_similarity(user_movie_matrix),
            index=user_movie_matrix.index,
            columns=user_movie_matrix.index,
        )
        similarity_matrix_time = time.time() - start_time
        # Сохранение user_movie_matrix
        user_movie_data = user_movie_matrix.reset_index().melt(
            id_vars="user_id", var_name="movie_id", value_name="rating"
        )
        user_movie_data_time = time.time() - start_time
        user_movie_records = user_movie_data.to_dict("records")
        user_movie_records_time = time.time() - start_time
        await self.user_movie_collection.delete_all()
        user_movie_delete_time = time.time() - start_time
        await self.user_movie_collection.insert_many(user_movie_records)
        user_movie_insert_time = time.time() - start_time

        # Сохранение similarity_matrix
        similarity_data = (
            similarity_matrix.reset_index()
            .rename(columns={"index": "user_id"})
            .melt(
                id_vars="user_id",
                var_name="other_user",
                value_name="similarity",
            )
        )
        similarity_data_time = time.time() - start_time
        similarity_records = similarity_data.to_dict("records")
        similarity_records_time = time.time() - start_time
        await self.similarity_collection.delete_all()
        similarity_delete_time = time.time() - start_time
        await self.similarity_collection.insert_many(similarity_records)
        similarity_insert_time = time.time() - start_time
        print(
            f"Работа refresh_matrices: raw_data_time = {raw_data_time}, df_likes_time = {df_likes_time}, user_movie_matrix_time = {user_movie_matrix_time}, similarity_matrix_time = {similarity_matrix_time}, "
            f"user_movie_data_time = {user_movie_data_time}, user_movie_records_time = {user_movie_records_time}, user_movie_delete_time = {user_movie_delete_time}, user_movie_insert_time = {user_movie_insert_time}, "
            f"similarity_data_time = {similarity_data_time}, similarity_records_time = {similarity_records_time}, similarity_delete_time = {similarity_delete_time}, "
            f"similarity_insert_time = {similarity_insert_time}"
        )

    async def get_recommendations(self, user_id: str) -> list[FilmShort]:
        """Получение списка рекомендаций."""
        try:
            start_time = time.time()
            # получение матриц
            user_movie_matrix, similarity_matrix = await self._fetch_matrices()
            # Находим схожих пользователей
            get_matrix_time = time.time() - start_time
            similar_users = similarity_matrix[user_id].sort_values(
                ascending=False
            )[1 : (settings.num_similar_users + 1)]  # исключая самого себя
            similar_users_time = time.time() - start_time
            # Собираем рекомендации от схожих пользователей
            recommended_movies = defaultdict(float)
            for other_user, similarity in similar_users.items():
                for movie, rating in user_movie_matrix.loc[other_user].items():
                    if (
                        rating > 0
                        and user_movie_matrix.at[user_id, movie] == 0
                    ):  # фильм понравился другому и не смотрел целевой
                        recommended_movies[movie] += similarity * rating
            recommended_movies_time = time.time() - start_time
            # Сортировка рекомендаций
            recommended_movies_sorted = sorted(
                recommended_movies.items(), key=lambda x: x[1], reverse=True
            )
            recommended_movies_sorted_time = time.time() - start_time
            # Возвращаем топ N рекомендаций
            movies_uuid = [
                movie
                for movie, _ in recommended_movies_sorted[
                    : settings.num_recommendations
                ]
            ]
            movies_uuid_time = time.time() - start_time
            # Возвращаем пустой список, если рекомендаций нет
            if movies_uuid == []:
                return movies_uuid
            movies_data = await self._fetch_movies_data_by_uuid(movies_uuid)
            movies_data_time = time.time() - start_time
            recommendations = self._sort_movies(movies_uuid, movies_data)
            recommendations_time = time.time() - start_time
            print(
                f"Работа get_recommendations: get_matrix_time = {get_matrix_time}, similar_users_time = {similar_users_time}, recommended_movies_time = {recommended_movies_time}, recommended_movies_sorted_time = {recommended_movies_sorted_time}, "
                f"movies_uuid_time = {movies_uuid_time}, movies_data_time = {movies_data_time}, recommendations_time = {recommendations_time}"
            )
            return recommendations
        except KeyError as exc:
            raise UserNotFoundtExeption from exc

    def _sort_movies(
        self, movies_uuid: list[str], movies_data: list[FilmShort]
    ) -> list[FilmShort]:
        """Сотрировка фильмов в порядке, как предоставленно рекомендациями."""
        # Создаем словарь для быстрого доступа к данным фильма по его UUID
        movies_data_dict = {
            movie_data["uuid"]: movie_data for movie_data in movies_data
        }
        # Создаем список рекомендаций из данных фильмов в нужном порядке
        recommendations = [
            movies_data_dict[movie_uuid] for movie_uuid in movies_uuid
        ]
        return recommendations

    async def _fetch_movies_data(self, endpoint):
        """Получение данных из UGC"""
        try:
            response = requests.get(endpoint)
            response.raise_for_status()  # Бросит исключение для статусов 4xx и 5xx
            data = response.json()
            return data
        except requests.RequestException as e:
            print(f"Ошибка при запросе к API: {e}")
            return []  # Возвращаем пустой список, если есть ошибка

    async def _fetch_movies_data_by_uuid(
        self, movies_uuid: list
    ) -> list[FilmShort]:
        """Получение данных по фильмам из Movies"""
        try:
            data = json.dumps(movies_uuid)
            response = requests.post(settings.movies_endpoint, data=data)
            response.raise_for_status()  # Бросит исключение для статусов 4xx и 5xx
            data = response.json()
            return data
        except requests.RequestException as e:
            print(f"Ошибка при запросе к API: {e}")
            return []  # Возвращаем пустой список, если есть ошибка

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
        start_time = time.time()
        # Извлечение user_movie_matrix
        user_movie_data = await self.user_movie_collection.get_list()
        user_movie_data_time = time.time() - start_time
        user_movie_df = pd.DataFrame(user_movie_data)
        user_movie_df_time = time.time() - start_time
        user_movie_matrix = user_movie_df.pivot(
            index="user_id", columns="movie_id", values="rating"
        )
        user_movie_matrix_time = time.time() - start_time
        # Извлечение similarity_matrix
        similarity_data = await self.similarity_collection.get_list()
        similarity_data_time = time.time() - start_time
        similarity_df = pd.DataFrame(similarity_data)
        similarity_df_time = time.time() - start_time
        similarity_matrix = similarity_df.pivot(
            index="user_id", columns="other_user", values="similarity"
        )
        similarity_matrix_time = time.time() - start_time
        print(
            f"Работа _fetch_matrices: user_movie_data_time = {user_movie_data_time}, user_movie_df_time = {user_movie_df_time}, user_movie_matrix_time = {user_movie_matrix_time}, similarity_data_time = {similarity_data_time}, "
            f"similarity_df_time = {similarity_df_time}, similarity_matrix_time = {similarity_matrix_time}"
        )
        return user_movie_matrix, similarity_matrix

    async def _fetch_new_movies(self):
        """Получение новинок из хранилища."""
        movies_data = await self.new_movies_collection.get_list()
        return movies_data

    async def _fetch_best_movies(self):
        """Получение лучших фильмов из хранилища."""
        movies_data = await self.best_movies_collection.get_list()
        return movies_data


def get_recommendations_service(
    user_movie_collection: MongoStorage = Depends(get_user_movie_storage),
    similarity_collection: MongoStorage = Depends(get_similarity_storage),
    new_movies_collection: MongoStorage = Depends(get_new_movies_storage),
    best_movies_collection: MongoStorage = Depends(get_best_movies_storage),
) -> RecommendationsService:
    return RecommendationsService(
        user_movie_collection=user_movie_collection,
        similarity_collection=similarity_collection,
        new_movies_collection=new_movies_collection,
        best_movies_collection=best_movies_collection,
    )
