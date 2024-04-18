from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from core.logger import logger
from core.config import settings, RightsName
from services.utils import PageParams
from schemas.role_schema import RoleTitle
from schemas.user_role_schema import (
    UserRoleSchema,
    UserRoleChange,
    UserRoleAssign,
    UserRoleInDBSchema,
)
from schemas.user_schema import (
    BaseUser,
    UserAdminUpdate,
    UserCreate,
    UserSelfUpdate,
    UserInDBBase,
    UserInDBFull,
    UserHistory,
    UserSelfResponse,
)
from services.access_service import (
    AccessService,
    get_access_service,
)
from services.token_service import check_rights
from services.user_service import (
    UserService,
    get_user_service,
    UserHistoryService,
    get_user_history_service,
    UserSocialAccountService,
    get_user_social_account_service,
)


router = APIRouter()


@router.post(
    "/signup",
    response_model=BaseUser,
    status_code=HTTPStatus.CREATED,
    description="Создание пользователя",
)
async def create_user(
    user_service: Annotated[UserService, Depends(get_user_service)],
    db: Annotated[AsyncSession, Depends(get_session)],
    user: UserCreate,
) -> BaseUser:
    """Создание пользователя на основе полученных данных."""

    new_user = await user_service.create_user_in_db(db=db, user=user)
    logger.info(f"Пользователь {new_user.username} добавлен")
    return new_user


@router.get(
    "/me", response_model=UserSelfResponse, description="Информация о себе"
)
async def get_current_user_data(
    current_user: UserInDBFull = Depends(check_rights()),
) -> UserSelfResponse:
    """Получение данных текущего пользователя."""
    return current_user


@router.get(
    "/me/history",
    description="История активности пользователя",
    response_model=list[UserHistory],
)
async def user_history(
    user_history_service: Annotated[
        UserHistoryService, Depends(get_user_history_service)
    ],
    db: Annotated[AsyncSession, Depends(get_session)],
    page_params: Annotated[PageParams, Depends(PageParams)],
    current_user: UserInDBFull = Depends(check_rights()),
) -> list[UserHistory]:
    """История активности пользователя."""
    history = await user_history_service.get_user_history(
        db=db, current_user=current_user, page_params=page_params
    )

    return history


@router.patch(
    "/me",
    response_model=BaseUser,
    description="Изменение пользователя",
)
async def update_user_data(
    user_service: Annotated[UserService, Depends(get_user_service)],
    db: Annotated[AsyncSession, Depends(get_session)],
    new_user_data: UserSelfUpdate,
    current_user: UserInDBFull = Depends(check_rights()),
) -> BaseUser:
    """Изменение данных пользователя."""
    # Приводим new_user_data к UserAdminUpdate
    update_data = UserAdminUpdate(**new_user_data.model_dump())

    updated_user = await user_service.update_user_in_db(
        db=db, new_user_data=update_data, username=current_user.username
    )
    return updated_user


@router.delete("/me", description="Удаление пользователя")
async def delete_user_data(
    user_service: Annotated[UserService, Depends(get_user_service)],
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: UserInDBFull = Depends(check_rights()),
) -> dict[str, str]:
    """Удаление всех данных пользователя."""
    update_data = user_service.get_data_to_delete_user(user=current_user)
    await user_service.update_user_in_db(
        db=db, new_user_data=update_data, user=current_user
    )
    return {"detail": "Вас больше нет с нами."}


@router.delete(
    "/me/unbound", description="Удаление привязок пользователя к соцсетям."
)
async def delete_user_social_account_data(
    user_social_account_service: Annotated[
        UserSocialAccountService, Depends(get_user_social_account_service)
    ],
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: UserInDBFull = Depends(check_rights()),
) -> dict[str, str]:
    """Удаление всех привязок пользователя к соцсетям."""
    await user_social_account_service.unbound_user_from_social_account_in_db(
        db=db, user=current_user
    )
    return {"detail": "Вы были отвязаны от всех соцсетей."}


@router.get(
    "/{username}",
    response_model=UserInDBFull,
    description="Получение данных пользователя админом.",
)
async def get_user_by_admin(
    user_service: Annotated[UserService, Depends(get_user_service)],
    db: Annotated[AsyncSession, Depends(get_session)],
    username: str,
    admin_user: UserInDBFull = Depends(check_rights(RightsName.admin)),
) -> UserInDBFull:
    """Получение данных пользователя админом."""
    user = await user_service.get_user_or_404(
        db=db, username=username, is_admin_request=True
    )
    return user


@router.patch(
    "/{username}",
    response_model=UserInDBFull,
    description="Изменение пользователя админом.",
)
async def change_user_by_admin(
    user_service: Annotated[UserService, Depends(get_user_service)],
    db: Annotated[AsyncSession, Depends(get_session)],
    new_user_data: UserAdminUpdate,
    username: str,
    admin_user: UserInDBFull = Depends(check_rights(RightsName.admin)),
) -> UserInDBFull:
    """Изменение пользователя админом."""
    updated_user = await user_service.update_user_in_db(
        db=db, new_user_data=new_user_data, username=username
    )
    return updated_user


@router.delete(
    "/{username}",
    description="Удаление пользователя админом.",
)
async def delete_user_by_admin(
    user_service: Annotated[UserService, Depends(get_user_service)],
    db: Annotated[AsyncSession, Depends(get_session)],
    username: str,
    admin_user: UserInDBFull = Depends(check_rights(RightsName.admin)),
) -> dict[str, str]:
    """Изменение пользователя админом."""
    user = await user_service.get_user_or_404(db=db, username=username)
    update_data = user_service.get_data_to_delete_user(user=user)
    await user_service.update_user_in_db(
        db=db, new_user_data=update_data, username=user.username
    )
    return {"detail": "Он больше нас не побеспокоит."}


@router.post(
    "/{username}/roles",
    description="Добавление роли пользователю админом.",
)
async def add_user_roles_by_admin(
    access_service: Annotated[AccessService, Depends(get_access_service)],
    db: Annotated[AsyncSession, Depends(get_session)],
    role_data: UserRoleAssign,
    username: str,
    admin_user: UserInDBFull = Depends(check_rights(RightsName.admin)),
) -> dict[str, str]:
    """Добавление роли пользователя админом."""
    await access_service.assign_user_role(
        db=db, username=username, role_data=role_data
    )
    return {
        "detail": f"Роль {role_data.title} добавлена пользователю {username}."
    }


@router.get(
    "/{username}/roles",
    description="Получение списка ролей пользователя админом.",
)
async def get_user_roles_by_admin(
    access_service: Annotated[AccessService, Depends(get_access_service)],
    db: Annotated[AsyncSession, Depends(get_session)],
    username: str,
    page_number: int = Query(1, description="Номер страницы", ge=1),
    page_size: int = Query(
        settings.standart_page_size, description="Элементов на странице", ge=1
    ),
    admin_user: UserInDBFull = Depends(check_rights(RightsName.admin)),
) -> list[UserRoleInDBSchema]:
    """Получение списка ролей пользователя админом.

    :param page_number: Номер страницы (начиная с 1).
    :param page_size: Количество элементов на странице.
    """
    user_list = await access_service.get_user_role_list(
        db=db, username=username, page_number=page_number, page_size=page_size
    )
    return user_list


@router.patch(
    "/{username}/roles/{role_title}",
    description="Изменение роли пользователя админом.",
)
async def update_user_roles_by_admin(
    access_service: Annotated[AccessService, Depends(get_access_service)],
    db: Annotated[AsyncSession, Depends(get_session)],
    new_user_role_data: UserRoleChange,
    username: str,
    role_title: str,
    admin_user: UserInDBFull = Depends(check_rights(RightsName.admin)),
) -> UserRoleSchema:
    """Изменение ролей пользователя админом."""
    result = await access_service.update_user_role(
        db=db,
        username=username,
        role_title=role_title,
        new_user_role_data=new_user_role_data,
    )
    return result


@router.delete(
    "/{username}/roles",
    description="Удаление роли пользователя админом.",
)
async def delete_user_role_by_admin(
    access_service: Annotated[AccessService, Depends(get_access_service)],
    db: Annotated[AsyncSession, Depends(get_session)],
    role_title: RoleTitle,
    username: str,
    admin_user: UserInDBFull = Depends(check_rights(RightsName.admin)),
) -> dict[str, str]:
    """Удаление роли пользователя админом."""
    await access_service.remove_user_role(
        db=db,
        username=username,
        role_title=role_title.title,
        admin_user=admin_user,
    )
    return {
        "detail": f"Роль {role_title.title} у пользователя {username} удалена."
    }


@router.get(
    "/{username}/history",
    response_model=list[UserHistory],
    description="Получение истории активности пользователя админом.",
)
async def get_user_history_by_admin(
    user_history_service: Annotated[
        UserHistoryService, Depends(get_user_history_service)
    ],
    user_service: Annotated[UserService, Depends(get_user_service)],
    db: Annotated[AsyncSession, Depends(get_session)],
    username: str,
    page_params: Annotated[PageParams, Depends(PageParams)],
    admin_user: UserInDBFull = Depends(check_rights(RightsName.admin)),
) -> list[UserHistory]:
    """Получение истории активности пользователя админом."""
    user = await user_service.get_user_or_404(db=db, username=username)
    history = await user_history_service.get_user_history(
        db=db, current_user=user, page_params=page_params
    )
    return history


@router.get(
    "/",
    description="Показать пользователей (только суперюзер).",
)
async def show_users_list(
    user_service: Annotated[UserService, Depends(get_user_service)],
    db: Annotated[AsyncSession, Depends(get_session)],
    page_number: int = Query(1, description="Номер страницы", ge=1),
    page_size: int = Query(
        settings.standart_page_size, description="Элементов на странице", ge=1
    ),
    admin_user: UserInDBFull = Depends(check_rights(RightsName.admin)),
) -> list[UserInDBBase]:
    """
    Вывод списка пользователей суперюзером.

    :param page_number: Номер страницы (начиная с 1).
    :param page_size: Количество элементов на странице.
    """
    user_list = await user_service.get_users_list(
        db=db,
        page_number=page_number,
        page_size=page_size,
    )
    return user_list
