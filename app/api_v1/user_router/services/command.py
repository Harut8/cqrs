import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.user_router.repository.crud import UserRepository
from app.api_v1.user_router.repository.models import User
from app.api_v1.user_router.schemas.write_schema import UserCreate


class UserCommandService:
    @staticmethod
    async def create_user(db: AsyncSession, user: UserCreate) -> User:
        _user_for_create = User(
            name=user.name,
            email=user.email,
            phone=user.phone,
            uuid=uuid.uuid4()
        )
        _user = await UserRepository.create_user(db, _user_for_create)
        return _user
