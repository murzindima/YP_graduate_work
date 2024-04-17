from functional.settings import test_settings

roles = (
    {"title": "role1", "description": "description1"},
    {"title": "role2", "description": "description2"},
)

admin = {
    "username": test_settings.superuser_name,
    "password": test_settings.superuser_password,
    "grant_type": "",
    "scope": "",
    "client_id": "",
    "client_secret": "",
    "id": "b96a5e2d-327d-4e10-a8ad-f3db78fd4170",
    "first_name": test_settings.superuser_first_name,
    "last_name": test_settings.superuser_last_name,
}

role_to_user = (
    {"username": "roles_user", "title": "role1"},
    {"username": "roles_user", "title": "role2"},
)

role_to_admin = (
    {"username": "admin", "title": "role1"},
    {"username": "admin", "title": "role2"},
)

unauthorized = {"detail": "Not authenticated"}


user = {
    "username": "roles_user",
    "password": "string",
    "email": "user_role@example.com",
    "grant_type": "",
    "scope": "",
    "client_id": "",
    "client_secret": "",
}


forbidden = {"detail": "Недостаточно прав."}

no_user = {"detail": "Пользователь не найден"}

no_roles = {"detail": "Роль не существует."}

no_title = {"detail": "Ошибки по полям: ['title: Field required']."}

user_add_new_role_answer = {
    "detail": "Роль role1 добавлена пользователю roles_user."
}

user_add_second_role_answer = {
    "detail": "Роль role2 добавлена пользователю roles_user."
}

user_override_role_answer = {
    "detail": "Роль уже была назначена пользователю ранее."
}

user_delete_role_answer = {
    "detail": "Роль role1 у пользователя roles_user удалена."
}

user_without_role_answer = {
    "detail": "Роль не назначалась пользователю ранее."
}

check_user_roles_in_db_sql = """select * from user_role;"""
