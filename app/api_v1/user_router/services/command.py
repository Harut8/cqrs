import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.user_router.handlers.command import UserCommandHandler
from app.api_v1.user_router.repository.models import User
from app.api_v1.user_router.schemas.write_schema import UserCreate
from app.helpers.db import DB_HELPER
from app.helpers.rabbitmq import publish_event, event


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

    @event.on('user_updated')
    async def up_to_date_users(db: AsyncSession, user_info: dict) -> User:
        ...

    @event.on('user_created')
    async def _sync_user_with_replica(user: dict,
                                      db: AsyncSession = DB_HELPER.scoped_session_dependency(
                                          db_name="replica")) -> User:
        _user_info = User(**user)
        _user = await UserCommandHandler.create_user(db, _user_info)
        return _user
