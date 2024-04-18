from sqlalchemy import (
    Boolean,
    Column,
    String,
    ForeignKey,
    UniqueConstraint,
    DateTime,
    or_,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_utils import EmailType

from core.config import settings
from db.postgres import Base
from models.parents import IdMixin, TimestampMixin


class Role(Base, IdMixin, TimestampMixin):
    __tablename__ = "role"

    title = Column(
        String(settings.max_role_title_length), unique=True, nullable=False
    )
    description = Column(String(settings.max_role_description_length))


class User(Base, IdMixin, TimestampMixin):
    __tablename__ = "users"

    username = Column(
        String(settings.max_username_length), unique=True, nullable=False
    )
    email = Column(
        EmailType(settings.max_email_length), unique=True, nullable=False
    )
    hashed_password = Column(
        String(settings.max_password_length), nullable=False
    )
    first_name = Column(String(settings.max_first_name_length))
    last_name = Column(String(settings.max_last_name_length))
    is_active = Column(Boolean, default=True, nullable=False)

    roles = relationship("UserRoleModel", back_populates="user", uselist=True)
    social_accounts = relationship(
        "SocialAccount", back_populates="user", lazy=True
    )

    def __repr__(self) -> str:
        return f"{self.username}_{self.email}, is_active: {self.is_active})"

    @classmethod
    def get_user_by_universal_login(
        cls, login: str | None = None, email: str | None = None
    ):
        return cls.query.filter(
            or_(cls.username == login, cls.email == email)
        ).first()


class UserRoleModel(Base, IdMixin, TimestampMixin):
    __tablename__ = "user_role"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(User.id, ondelete="CASCADE"),
        nullable=False,
    )

    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey(Role.id, ondelete="CASCADE"),
        nullable=False,
    )
    expire_at = Column(DateTime)
    is_active = Column(Boolean, default=True, nullable=False)

    user = relationship(
        "User", back_populates="roles", foreign_keys="UserRoleModel.user_id"
    )
    role = relationship("Role", foreign_keys="UserRoleModel.role_id")

    UniqueConstraint(user_id, role_id, name="unique_role_for_user")


class UserActivityHistory(Base, IdMixin, TimestampMixin):
    __tablename__ = "user_activity_history"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    user_agent = Column(String(255), nullable=False, default="Unknown")
    activity = Column(String(255), nullable=False, default="Login")


class SocialAccount(Base, IdMixin):
    __tablename__ = "social_account"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    user = relationship("User", back_populates="social_accounts", lazy=True)

    social_id = Column(String, nullable=False)
    social_name = Column(String, nullable=False)

    UniqueConstraint("social_id", "social_name", name="social_pk")

    def __repr__(self) -> str:
        return f"<SocialAccount {self.social_name}:{self.user_id}>"
