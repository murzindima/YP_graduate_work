"""Модели кастомных исключений."""

from fastapi import HTTPException, status


class UserNotFoundtExeption(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
