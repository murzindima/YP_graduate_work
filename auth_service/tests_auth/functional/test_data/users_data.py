from http import HTTPStatus

correct_user = (
    {
        "username": "string",
        "email": "user@example.com",
        "first_name": "string",
        "last_name": "string",
        "password": "string",
    },
    {
        "username": "string",
        "email": "user@example.com",
        "first_name": "string",
        "last_name": "string",
    },
)

same_email_user = (
    {
        "username": "Joe",
        "email": "user@example.com",
        "first_name": "Joe",
        "last_name": "Dohn",
        "password": "qwerty",
    },
    HTTPStatus.BAD_REQUEST,
)

same_username_user = (
    {
        "username": "string",
        "email": "newemail@example.com",
        "first_name": "Joe",
        "last_name": "Dohn",
        "password": "qwerty",
    },
    HTTPStatus.BAD_REQUEST,
)

incorrect_username = (
    {
        "username": "\\//",
        "email": "user@example.com",
        "first_name": "string",
        "last_name": "string",
        "password": "string",
    },
    HTTPStatus.BAD_REQUEST,
)

incorrect_email = (
    {
        "username": "string",
        "email": "test.validation`",
        "first_name": "string",
        "last_name": "string",
        "password": "string",
    },
    HTTPStatus.UNPROCESSABLE_ENTITY,
)

empty_username = (
    {
        "username": "",
        "email": "user@example.com",
        "first_name": "string",
        "last_name": "string",
        "password": "string",
    },
    HTTPStatus.BAD_REQUEST,
)

empty_email = (
    {
        "username": "username",
        "email": "",
        "first_name": "string",
        "last_name": "string",
        "password": "string",
    },
    HTTPStatus.UNPROCESSABLE_ENTITY,
)

empty_password = (
    {
        "username": "",
        "email": "user@example.com",
        "first_name": "Name",
        "last_name": "Last name",
        "password": "",
    },
    HTTPStatus.UNPROCESSABLE_ENTITY,
)

empty_dict = ({}, HTTPStatus.UNPROCESSABLE_ENTITY)  # type: ignore[var-annotated]

all_incorrect_users = [
    incorrect_username,
    incorrect_email,
    empty_username,
    empty_email,
    empty_password,
    empty_dict,
]

check_user_in_db_sql = (
    """select * from users where email='user@example.com';"""
)

user_1 = {
    "id": "11111111-1111-1111-1111-111111111111",
    "username": "user_1",
    "email": "user_1@example.com",
    "first_name": "Darth",
    "last_name": "Vader",
    "password": "Password123!",
    "is_active": "true",
}

user_updated = {
    "id": "11111111-1111-1111-1111-111111111111",
    "username": "New_username",
    "email": "user_1@example.com",
    "first_name": "Darth",
    "last_name": "Vader",
    "password": "New_Password123!",
    "is_active": "true",
}


user_2 = {
    "id": "22222222-2222-2222-2222-222222222222",
    "username": "user_2",
    "email": "user_2@example.com",
    "first_name": "Luke",
    "last_name": "Skywalker",
    "password": "Password1234!",
    "is_active": "true",
}
