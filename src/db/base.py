from decimal import Decimal
import contextlib
from typing import Annotated, AsyncIterator
import uuid

from sqlalchemy import Integer, MetaData, Numeric, String
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, mapped_column

from settings import DatabaseSettings, get_settings


meta = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    },
)

uuid_pk = Annotated[
    uuid.UUID,
    mapped_column(primary_key=True, default=uuid.uuid4),
]

int32_pk = Annotated[
    int,
    mapped_column(
        Integer,
        primary_key=True,
    ),
]
numeric_10_2 = Annotated[Decimal, mapped_column(Numeric(precision=10, scale=2))]
str_128 = Annotated[str, mapped_column(String(128))]
str_256 = Annotated[str, mapped_column(String(256))]


class Base(DeclarativeBase):
    metadata = meta


settings: DatabaseSettings = get_settings(DatabaseSettings)
engine: AsyncEngine = create_async_engine(settings.async_url)
async_session = async_sessionmaker(bind=engine, class_=AsyncSession)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session
