from fastapi import HTTPException, status

from core.config import settings, RightsName


class UserInactiveException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive"
        )


class ValidationException(HTTPException):
    def __init__(self, refresh: bool = False) -> None:
        self.item = "token"
        if refresh:
            self.item = "refresh_token"
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {self.item}",
        )


class TokenExpiredException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Срок действия токена истек,"
            " войдите в аккаунт и получите новый токен",
        )


class TokenNonExistentException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Несуществующий токен,"
            " войдите в аккаунт и получите новый токен",
        )


class UserNotFoundException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )


class CredentialsException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


class OverrideRoleException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такая роль уже существует.",
        )


class RoleNotFoundException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Роль не существует.",
        )


class UserRoleNotFoundException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Роль не назначалась пользователю ранее.",
        )


class OverrideUserRoleException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Роль уже была назначена пользователю ранее.",
        )


class EmailAlreadyUsedException(HTTPException):
    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Пользователь с Email {self.email} уже зарегистрирован.",
        )


class UsernameAlreadyExistException(HTTPException):
    def __init__(self, username: str) -> None:
        self.username = username
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Пользователь с username {self.username} "
                f"уже зарегистрирован."
            ),
        )


class PasswordComplexityException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Пароль должен быть от {settings.min_password_input_length} "
                f"до {settings.max_password_input_length} символов."
            ),
        )


class UsernameNotMeException(HTTPException):
    def __init__(self, username: str) -> None:
        self.username = username
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username не может быть '{self.username}'.",
        )


class NotAllowedUsernameException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Username должен быть от {settings.min_username_length} до "
                f"{settings.max_username_length} символов на латинице, без "
                f"пробелов и специальных знаков."
            ),
        )


class ProcessErrorException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Ошибка обработки",
        )


class LoginException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректное имя пользователя или пароль",
        )


class RulesException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав.",
        )


class TooManyRequestsException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Превышен лимит запросов",
        )


class USserAlreadyBoundedToSocialNetworkException(HTTPException):
    def __init__(self, social_name: str) -> None:
        self.social_name = social_name
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Ваш аккаунт уже привязан к {self.social_name} с другой "
                f"учетной записи."
            ),
        )


class UserHaveNotBoundedException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ваш аккаунт не был привязан раеее к соцсетям.",
        )


class AdminRoleDeleteException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Нельзя удалить роль {RightsName.admin}.",
        )


class AdminRoleNameChangeException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Нельзя изменить title роли {RightsName.admin}.",
        )


class BoundedToUserRoleException(HTTPException):
    def __init__(self, role_title: str) -> None:
        self.role_title = role_title
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Невозможно удалить роль {self.role_title} т.к. она привязана "
                f"к пользователю."
            ),
        )


class SelfDeleteAdminUserRoleException(HTTPException):
    def __init__(self, role_title: str) -> None:
        self.role_title = role_title
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(f"Невозможно удалить роль {self.role_title} у себя."),
        )


class NotDefinedSocialNetwork(HTTPException):
    def __init__(self, social_network: str) -> None:
        self.social_network = social_network
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Не реализована возможность регистрации и авторизации через "
                f"{self.social_network}."
            ),
        )
