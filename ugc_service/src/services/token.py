import http
import time

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt

from core.config import settings
from models.user import User


def decode_token(token: str) -> dict | None:
    try:
        decoded_token = jwt.decode(
            token,
            settings.access_token_secret_key,
            algorithms=[settings.token_jwt_algorithm],
        )
        return decoded_token if decoded_token["exp"] >= time.time() else None
    except Exception:
        return None


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: (
            HTTPAuthorizationCredentials | None
        ) = await super().__call__(request)
        if not credentials:
            raise HTTPException(
                status_code=http.HTTPStatus.FORBIDDEN,
                detail="Invalid authorization code.",
            )
        if not credentials.scheme == "Bearer":
            raise HTTPException(
                status_code=http.HTTPStatus.UNAUTHORIZED,
                detail="Only Bearer token might be accepted",
            )
        decoded_token = self.parse_token(credentials.credentials)
        if not decoded_token:
            raise HTTPException(
                status_code=http.HTTPStatus.FORBIDDEN,
                detail="Invalid or expired token.",
            )
        return decoded_token

    @staticmethod
    def parse_token(jwt_token: str) -> dict | None:
        return decode_token(jwt_token)


security_jwt = JWTBearer()


def get_user():
    async def check_user(
        token_data: dict = Depends(security_jwt),
    ) -> User | None:
        user = User(**token_data)
        return user

    return check_user
