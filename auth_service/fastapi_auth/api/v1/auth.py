from typing import Annotated

from fastapi import APIRouter, Depends, status, Header, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings, SocialNetworks, oauth
from core.exceptions import NotDefinedSocialNetwork
from db.postgres import get_session
from schemas.token_schema import Tokens, oauth2_scheme, RefreshToken
from services.cache import get_cache_service, RedisCacheService
from services.token_service import get_user_token_service, TokenService
from services.user_service import UserService, get_user_service


router = APIRouter()


@router.post(
    "/login",
    response_model=Tokens,
    description="Аутентификация пользователя с выдачей ему токенов",
    status_code=status.HTTP_200_OK,
)
async def login(
    db: Annotated[AsyncSession, Depends(get_session)],
    token_service: Annotated[TokenService, Depends(get_user_token_service)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_agent: Annotated[str | None, Header()] = None,
) -> Tokens:
    """
    Аутентификация пользователя и
    выдача ему acceess и refresh токенов.
    """
    tokens = await token_service.authenticate_user(
        db=db, form_data=form_data, user_agent=user_agent
    )
    return tokens


@router.post(
    "/logout", description="Выход из аккаунта", status_code=status.HTTP_200_OK
)
async def logout(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_session)],
    token_service: Annotated[TokenService, Depends(get_user_token_service)],
    cache: Annotated[RedisCacheService, Depends(get_cache_service)],
    refresh_token: RefreshToken,
    user_agent: Annotated[str | None, Header()] = None,
) -> dict[str, str]:
    """Выход из аккаунта."""

    await token_service.revoke_tokens(
        db=db,
        token=token,
        refresh_token=refresh_token.token,
        cache=cache,
        user_agent=user_agent,
    )
    return {"detail": "logged out"}


@router.post(
    "/refresh",
    response_model=Tokens,
    description="Получить новые токены по refresh токену",
    status_code=status.HTTP_200_OK,
)
async def refresh_token(
    db: Annotated[AsyncSession, Depends(get_session)],
    token_service: Annotated[TokenService, Depends(get_user_token_service)],
    refresh_token: RefreshToken,
    user_agent: Annotated[str | None, Header()] = None,
) -> Tokens:
    """Получить новые токены по действующему refresh токену."""

    tokens = await token_service.refresh_tokens(
        db=db, refresh_token=refresh_token.token, user_agent=user_agent
    )
    return tokens


@router.get("/login/token")
async def login_by_social_network(
    code: str,
    state: dict,
    db: Annotated[AsyncSession, Depends(get_session)],
    token_service: Annotated[TokenService, Depends(get_user_token_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    user_agent: Annotated[str | None, Header()] = None,
) -> Tokens:
    """
    Эндпоинт для запроса кода подтверждения социальной сети.
    Сюда происходит автоматический редирект от социальной сети.

    """
    # state для трассировки приходит социальной сети
    if state["social_network"] == SocialNetworks.yandex:
        reg_data = await user_service.get_user_data_from_yandex(code=code)
    user = await user_service.get_or_create_user_by_social_network_data(
        db=db, reg_data=reg_data
    )
    tokens = await token_service.get_tokens(
        db=db, user=user, user_agent=user_agent
    )
    return tokens


@router.get("/login/{social_network}")
async def get_yandex_access_code(request: Request, social_network: str):
    """Эндпоинт для запроса кода подтверждения социальных сетей"""

    if social_network == SocialNetworks.yandex:
        client = oauth.create_client(SocialNetworks.yandex)
        state = {
            "X-Request-Id": request.headers.get("X-Request-Id"),
            "social_network": social_network,
        }
        authorize_url = f"{settings.yandex_url}&client_id={settings.yandex_client_id}&state={state}"
        return await client.authorize_redirect(request, authorize_url)
    raise NotDefinedSocialNetwork
