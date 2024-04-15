from datetime import timedelta, datetime

token_data = {
    "username": "user_1",
    "user_id": "cf4f87f8-d6a2-4fb9-a9f9-f3ad47d0d9b8",
    "roles": ["admin", "user"],
    "email": "mail@mail.com",
    "first_name": "first_name",
    "last_name": "last_name",
    "exp": datetime.utcnow() + timedelta(minutes=60),
}
