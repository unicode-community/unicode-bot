import os
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy import ScalarResult, delete, select, update
from sqlalchemy.engine import URL
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .models import Base, Mentor, User

load_dotenv()
postgres_url = URL.create(
    drivername="postgresql+asyncpg",
    username=os.getenv("POSTGRES_USER"),
    host=os.getenv("POSTGRES_HOST"),
    password=os.getenv("POSTGRES_PASSWORD"),
    database=os.getenv("POSTGRES_NAME"),
    port=os.getenv("POSTGRES_PORT")
)


class Database:
    def __init__(self) -> None:
        self.engine: AsyncEngine = create_async_engine(url=postgres_url)
        self.async_session: AsyncSession = async_sessionmaker(
            self.engine,
            expire_on_commit=False
        )

    async def create(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def new_subscriber(self, **kwargs) -> None:
        async with self.async_session.begin() as session:
            session.add(User(**kwargs))

    async def new_mentor(self, **kwargs) -> None:
        async with self.async_session.begin() as session:
            session.add(Mentor(**kwargs))

    async def unsubscribe_user(self, tg_id: int):
        stmt = (
            delete(User).
            where(
                User.tg_id == tg_id
            )
        )
        async with self.async_session.begin() as session:
            await session.execute(stmt)
            await session.commit()

    async def delete_mentor(self, tg_id: int):
        stmt = (
            delete(Mentor).
            where(
                Mentor.tg_id == tg_id
            )
        )
        async with self.async_session.begin() as session:
            await session.execute(stmt)
            await session.commit()

    async def get_subscriber(self, user_id: Optional[int]=None, all_data: bool=False) -> Optional[ScalarResult]:
        stmt = (
            select(User).
            where(User.tg_id == user_id)
        ) if user_id is not None else select(User)

        try:
            async with self.async_session.begin() as session:
                data = await session.execute(stmt)
                return data.scalars().one() if not all_data else data.scalars().all()
        except NoResultFound:
            return None

    async def get_mentor(self, tg_id: int) -> Optional[ScalarResult]:
        stmt = (
            select(Mentor).
            where(Mentor.tg_id == tg_id)
        )
        try:
            async with self.async_session.begin() as session:
                data = await session.execute(stmt)
                return data.scalars().one()
        except NoResultFound:
            return None

    async def mentor_update(self, user_id: int, **kwargs) -> None:
        stmt = (
            update(Mentor).
            where(Mentor.tg_id == user_id).
            values(**kwargs)
        )

        async with self.async_session.begin() as session:
            await session.execute(stmt)

    async def subscriber_update(self, user_id: int, **kwargs) -> None:
        stmt = (
            update(User).
            where(User.tg_id == user_id).
            values(**kwargs)
        )

        async with self.async_session.begin() as session:
            await session.execute(stmt)

    async def get_db():
        db = Database()
        yield db
