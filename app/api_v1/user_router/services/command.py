import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.user_router.handlers.command import UserCommandHandler
from app.api_v1.user_router.repository.models import User
from app.api_v1.user_router.schemas.write_schema import UserCreate
from app.helpers.rabbitmq import publish_event


class UserCommandService:
    @staticmethod
    @publish_event(event_name='user_created')
    async def create_user(db: AsyncSession, user: UserCreate) -> User:
        _user_for_create = User(
            name=user.name,
            email=user.email,
            phone=user.phone,
            uuid=uuid.uuid4()
        )
        _user = await UserCommandHandler.create_user(db, _user_for_create)
        return _user
