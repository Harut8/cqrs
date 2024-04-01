from app.api_v1.user_router.repository.crud import UserRepository
from app.api_v1.user_router.repository.models import User
from app.helpers.rabbitmq import event


class UserCommandHandler:
    @staticmethod
    async def create_user(db, user: User):
        _user = await UserRepository.create_user(db, user)
        return _user

    @staticmethod
    @event.on('user_created')
    async def _sync_user_with_replica(db, user: User):
        _user = await UserCommandHandler.create_user(db, user)
        return _user
