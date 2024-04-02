from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.user_router.repository.crud import UserRepository
from app.api_v1.user_router.repository.models import User


class UserCommandHandler:
    @staticmethod
    async def create_user(db: AsyncSession, user: User):
        _user = await UserRepository.create_user(db, user)
        return _user
