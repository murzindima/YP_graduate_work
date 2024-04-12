from abc import ABC, abstractmethod

from fastapi import Request


class AuthAbstractService[M](ABC):
    """Abstract base class defining authentication service methods."""

    @abstractmethod
    async def login(self, login: str, password: str, request: Request) -> M | None:
        """Authenticate a user."""

    @abstractmethod
    async def logout(self, request: Request) -> None:
        """Log out the user."""
