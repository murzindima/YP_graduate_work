from uuid import UUID

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


@router.get("/{user_id}", summary="Получение списка рекоммендаций.")
async def get_recommendations(
    user_id: UUID,
    recommendations_service: RecommendationsService = Depends(
        get_recommendations_service
    ),
) -> list[FilmShort]:
    recommendations = await recommendations_service.get_recommendations(
        str(user_id)
    )
    return recommendations
