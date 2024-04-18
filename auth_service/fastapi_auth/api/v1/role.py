from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings, RightsName
from db.postgres import get_session
from schemas.role_schema import RoleInDB, RoleBase, RoleTitle, RoleUpdate
from schemas.user_schema import UserInDBFull
from services.token_service import check_rights
from services.role_service import RoleService, get_role_service

router = APIRouter()


@router.post(
    "/",
    response_model=RoleInDB,
    description="Создать роль",
    status_code=HTTPStatus.CREATED,
)
async def create_role(
    db: Annotated[AsyncSession, Depends(get_session)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
    role: RoleBase = Body(description="название и описание роли"),
    admin_user: UserInDBFull = Depends(check_rights(RightsName.admin)),
) -> RoleInDB:
    """
    Создать роль
    """
    result = await role_service.create(db=db, role=role)
    return result


@router.get(
    "/{role_title}",
    response_model=RoleInDB,
    description="Получение информации о роли",
    status_code=HTTPStatus.OK,
)
async def get_role(
    db: Annotated[AsyncSession, Depends(get_session)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
    role_title: str = Path(description="title роли"),
    admin_user: UserInDBFull = Depends(check_rights(RightsName.admin)),
) -> RoleInDB:
    """
    Получить данные по роли по id
    """
    role = RoleTitle(title=role_title)
    result = await role_service.get(db=db, role=role)
    return result


@router.patch(
    "/{role_title}",
    response_model=RoleInDB,
    description="Обновить роль",
    status_code=HTTPStatus.OK,
)
async def update_role(
    db: Annotated[AsyncSession, Depends(get_session)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
    role_title: str = Path(description="title роли"),
    updated_role_data: RoleUpdate = Body(description="поля для изменения"),
    admin_user: UserInDBFull = Depends(check_rights(RightsName.admin)),
) -> RoleInDB:
    """
    Обновить данные в роли
    """
    role = RoleTitle(title=role_title)
    result = await role_service.update(
        db=db, role=role, updated_role_data=updated_role_data
    )
    return result


@router.delete(
    "/{role_title}",
    description="Удалить роль",
    status_code=HTTPStatus.OK,
)
async def delete_role(
    db: Annotated[AsyncSession, Depends(get_session)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
    role_title: str = Path(description="title роли"),
    admin_user: UserInDBFull = Depends(check_rights(RightsName.admin)),
) -> dict[str, str]:
    """
    Удалить роль по title
    """
    role = RoleTitle(title=role_title)
    await role_service.delete(db=db, role=role)
    return {"detail": f"Роль {role_title} удалена."}


@router.get(
    "/",
    response_model=list[RoleInDB],
    description="Получить все роли.",
    status_code=HTTPStatus.CREATED,
)
async def get_role_list(
    db: Annotated[AsyncSession, Depends(get_session)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
    page_number: int = Query(1, description="Номер страницы", ge=1),
    page_size: int = Query(
        settings.standart_page_size, description="Элементов на странице", ge=1
    ),
    admin_user: UserInDBFull = Depends(check_rights(RightsName.admin)),
) -> list[RoleInDB]:
    """
    Вывод списка ролей админом.

    :param page_number: Номер страницы (начиная с 1).
    :param page_size: Количество элементов на странице.
    """
    role_list = await role_service.get_role_list(
        db=db,
        page_number=page_number,
        page_size=page_size,
    )
    return role_list
