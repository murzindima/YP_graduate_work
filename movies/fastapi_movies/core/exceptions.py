"""Модели кастомных исключений."""
from fastapi import HTTPException, status


class ElasticsearchError(Exception):
    pass


class RulesException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав.",
        )
