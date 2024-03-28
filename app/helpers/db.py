import datetime
import re
import uuid
from asyncio import current_task

import sqlalchemy
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from app.settings import APP_SETTINGS


def to_snake_case(name):
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub("__([A-Z])", r"_\1", name)
    name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.lower()


class DbHelper:
    _ENGINES = {}

    def __init__(self, urls: [str], echo: bool = False):
        for i, url in enumerate(urls):
            _engine = create_async_engine(
                url=url, echo=echo, pool_size=5, max_overflow=10, future=True
            )
            if i == 0:
                self._ENGINES.update({'primary': _engine})
            else:
                self._ENGINES.update({'replica': _engine})

    def get_scoped_session(self, db_name: str = 'primary'):
        if db_name not in self._ENGINES:
            raise Exception(f"{db_name} db not found")
        _session = async_scoped_session(
            session_factory=self._ENGINES[db_name],
            scopefunc=current_task,
        )
        return _session

    async def session_dependency(self, db_name: str = 'primary'):
        async def _wrapper() -> AsyncSession:
            if db_name not in self._ENGINES:
                raise Exception(f"{db_name} db not found")
            _engine = self._ENGINES[db_name]
            _async_session = async_sessionmaker(
                bind=_engine,
                autoflush=False,
                autocommit=False,
                expire_on_commit=False,
            )
            async with _async_session() as session:
                yield session
                await session.close()

        return _wrapper()

    async def scoped_session_dependency(self, db_name: str = 'primary'):
        async def _wrapper() -> AsyncSession:
            _session = self.get_scoped_session(db_name=db_name)
            async with _session() as session:
                print(session.bind.pool.status())
                yield session
                await session.close()

        return _wrapper()


class BaseModel(DeclarativeBase):
    __abstract__ = True
    uuid = sqlalchemy.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime.datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )

    @declared_attr.directive
    def __tablename__(cls):
        return to_snake_case(cls.__name__)


DB_HELPER = DbHelper(urls=[APP_SETTINGS.DATABASE.POSTGRES_PRIMARY_DSN, APP_SETTINGS.DATABASE.POSTGRES_REPLICATION_DSN])
