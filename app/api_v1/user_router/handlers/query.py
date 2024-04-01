import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.user_router.repository.crud import UserRepository
from app.api_v1.user_router.repository.models import User


class UserQueryHandler:
    @staticmethod
    async def get_user(db: AsyncSession, user_uuid: uuid.UUID) -> User:
        _user = await UserRepository.get_user(db, user_uuid)
        return _user
