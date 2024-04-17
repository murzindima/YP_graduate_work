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
)


class RecommendationsService:
    def __init__(
        self,
        user_movie_collection: MongoStorage,
        similarity_collection: MongoStorage,
    ) -> None:
        self.user_movie_collection = user_movie_collection
        self.similarity_collection = similarity_collection

    async def refresh_matrices(self) -> None:
        """Создание/обновление существующих матриц."""
        raw_data = await self._fetch_movies_data()
        df_likes = self._process_data(raw_data)

        # Создание матрицы "пользователь-фильм"
        user_movie_matrix = df_likes.pivot_table(
            index="user_id", columns="movie_id", values="rating", fill_value=0
        )

        # Вычисление косинусного сходства между пользователями
        similarity_matrix = pd.DataFrame(
            cosine_similarity(user_movie_matrix),
            index=user_movie_matrix.index,
            columns=user_movie_matrix.index,
        )

        # Сохранение user_movie_matrix
        user_movie_data = user_movie_matrix.reset_index().melt(
            id_vars="user_id", var_name="movie_id", value_name="rating"
        )
        user_movie_records = user_movie_data.to_dict("records")
        await self.user_movie_collection.delete_all()
        await self.user_movie_collection.insert_many(user_movie_records)

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
        similarity_records = similarity_data.to_dict("records")
        await self.similarity_collection.delete_all()
        await self.similarity_collection.insert_many(similarity_records)

    async def get_recommendations(self, user_id: str) -> list[str]:
        """Получение списка рекомендаций."""
        try:
            # получение матриц
            user_movie_matrix, similarity_matrix = await self._fetch_matrices()
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
            # Возвращаем топ N рекомендаций
            return [
                movie
                for movie, _ in recommended_movies_sorted[
                    : settings.num_recommendations
                ]
            ]
        except KeyError:
            raise UserNotFoundtExeption

    async def _fetch_movies_data(self):
        """Получение данных из UGC"""
        try:
            response = requests.get(settings.ugc_movies_endpoint)
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
        # Извлечение user_movie_matrix
        user_movie_data = await self.user_movie_collection.get_list()
        user_movie_df = pd.DataFrame(user_movie_data)
        user_movie_matrix = user_movie_df.pivot(
            index="user_id", columns="movie_id", values="rating"
        )
        # Извлечение similarity_matrix
        similarity_data = await self.similarity_collection.get_list()
        similarity_df = pd.DataFrame(similarity_data)
        similarity_matrix = similarity_df.pivot(
            index="user_id", columns="other_user", values="similarity"
        )
        return user_movie_matrix, similarity_matrix


def get_recommendations_service(
    user_movie_collection: MongoStorage = Depends(get_user_movie_storage),
    similarity_collection: MongoStorage = Depends(get_similarity_storage),
) -> RecommendationsService:
    return RecommendationsService(
        user_movie_collection=user_movie_collection,
        similarity_collection=similarity_collection,
    )
