import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api_v1.user_router.repository.models import User


class UserRepository:

    @staticmethod
    async def _insert_instance(instance, db: AsyncSession):
        db.add(instance)
        await db.commit()
        await db.refresh(instance)
        return instance

    @staticmethod
    async def create_user(db: AsyncSession, user: User) -> User:
        _user = await UserRepository._insert_instance(user, db)
        return _user

    @staticmethod
    async def get_user(db: AsyncSession, user_uuid: uuid.uuid4()) -> User:
        _stmt = select(User).where(User.uuid == user_uuid)  # type: ignore
        _user = await db.scalar(_stmt)
        return _user
