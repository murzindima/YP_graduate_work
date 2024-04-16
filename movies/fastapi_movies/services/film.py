from functools import lru_cache

from fastapi import Depends

from core.enum import IndexName
from core.service import CommonService
from models.film import Film
from services.cache import get_cache_service
from services.storage import get_storage_service


@lru_cache()
def get_film_service(
    cache=Depends(get_cache_service),
    elastic=Depends(get_storage_service),
) -> CommonService:
    return CommonService(
        cache=cache, elastic=elastic, model=Film, index=IndexName.movies
    )