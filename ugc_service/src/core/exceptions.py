"""Модели кастомных исключений."""
from fastapi import HTTPException, status


class ObjectDoesNotExistExeption(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail='Object does not exist',
        )


class DuplicateObjectExeption(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail='Duplicate Object',
        )
