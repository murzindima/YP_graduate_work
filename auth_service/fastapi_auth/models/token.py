from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID

from db.postgres import Base
from models.parents import IdMixin, TimestampMixin
from models.common import User


class UserRefreshToken(Base, IdMixin, TimestampMixin):
    __tablename__ = "refresh_tokens"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey(User.id, ondelete="CASCADE")
    )
    token = Column(String(1000), nullable=False, unique=True)
    expire_at = Column(DateTime)
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return (
            f"{self.user_id}_{self.token[-6:]}, is_active: {self.is_active})"
        )
