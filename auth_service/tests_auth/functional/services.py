import bcrypt


def create_hashed_password(password: str) -> str:
    hashed_password_b: bytes = bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt()
    )
    hashed_password: str = hashed_password_b.decode("utf-8")
    return hashed_password


def check_password(password: str, hashed_password: str) -> bool:
    result = bool(
        bcrypt.checkpw(
            password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    )
    return result
