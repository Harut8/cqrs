import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.user_router.handlers.query import UserQueryHandler
from app.api_v1.user_router.repository.models import User


class UserQueryService:
    @staticmethod
    async def get_user(db: AsyncSession, user_uuid: uuid.UUID) -> User:
        _user = await UserQueryHandler.get_user(db, user_uuid)
        return _user
