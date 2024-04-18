from fastapi import APIRouter, Depends

from core.models import FilmShort
from services.recommendations import (
    RecommendationsService,
    get_recommendations_service,
)

router = APIRouter()


@router.get("/create_matrices", summary="Создание и обновление матриц.")
async def create_matrices(
    recommendations_service: RecommendationsService = Depends(
        get_recommendations_service
    ),
) -> None:
    await recommendations_service.refresh_matrices()


@router.get("/update_new", summary="Актуализация новинок фильмов.")
async def update_new(
        recommendations_service: RecommendationsService = Depends(
            get_recommendations_service
        ),
) -> None:
    await recommendations_service.refresh_new()


@router.get("/update_best", summary="Актуализация лучших фильмов.")
async def update_best(
        recommendations_service: RecommendationsService = Depends(
            get_recommendations_service
        ),
) -> None:

    await recommendations_service.refresh_best()


@router.get("/{user_id}", summary="Получение списка рекоммендаций.")
async def get_recommendations(
    user_id: str,
    recommendations_service: RecommendationsService = Depends(
        get_recommendations_service
    ),
) -> list[FilmShort]:
    recommendations = await recommendations_service.get_recommendations(
        user_id
    )
    return recommendations
