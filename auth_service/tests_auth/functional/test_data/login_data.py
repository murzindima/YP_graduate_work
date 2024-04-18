from http import HTTPStatus


correct_login = (
    {
        "username": "string",
        "password": "string",
        "grant_type": "",
        "scope": "",
        "client_id": "",
        "client_secret": "",
    },
    HTTPStatus.OK,
)
