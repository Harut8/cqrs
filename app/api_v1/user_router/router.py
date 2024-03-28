from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.user_router.schemas.body_schema import UserGet
from app.api_v1.user_router.schemas.read_schema import UserRead
from app.api_v1.user_router.schemas.write_schema import UserCreate
from app.api_v1.user_router.services.command import UserCommandService
from app.api_v1.user_router.services.query import UserQueryService
from app.helpers.db import DB_HELPER

user_router = APIRouter(
    prefix="/user",
    tags=["User"],
)


@user_router.get("/user", response_model=UserRead)
async def get_user(request: UserGet,
                   db: AsyncSession = Depends(DB_HELPER.scoped_session_dependency(db_name="replica"))):
    _user = await UserQueryService.get_user(db, user_uuid=request.user_id)
    return _user


@user_router.post("/user")
async def create_user(user: UserCreate,
                      db: AsyncSession = Depends(DB_HELPER.scoped_session_dependency(db_name="primary"))):
    _user = await UserCommandService.create_user(db, user)

