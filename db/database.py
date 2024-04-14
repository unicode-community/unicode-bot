import os
from datetime import datetime
from typing import Optional

from pytz import timezone
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
        """Создаем таблицы в базе данных"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


    async def get_user(self, user_id) -> Optional[ScalarResult]:
        stmt = (
            select(User).
            where(User.tg_id == user_id)
        )

        try:
            async with self.async_session.begin() as session:
                data = await session.execute(stmt)
                return data.scalars().one()
        except NoResultFound:
            return None

    async def get_user_by_username(self, tg_username: str) -> Optional[ScalarResult]:
        stmt = (
            select(User).
            where(User.tg_username == tg_username)
        )

        try:
            async with self.async_session.begin() as session:
                data = await session.execute(stmt)
                return data.scalars().one()
        except NoResultFound:
            return None


    async def get_mentor(self, tg_id: int) -> Optional[ScalarResult]:
        stmt = (
            select(Mentor).
            where(
                Mentor.tg_id == tg_id,
            )
        )
        try:
            async with self.async_session.begin() as session:
                data = await session.execute(stmt)
                return data.scalars().one()
        except NoResultFound:
            return None


    async def user_update(self, user_id: int, **kwargs) -> None:
        stmt = (
            update(User).
            where(User.tg_id == user_id).
            values(**kwargs)
        )

        async with self.async_session.begin() as session:
            await session.execute(stmt)


    async def mentor_update(self, tg_id: int, **kwargs) -> None:
        stmt = (
            update(Mentor).
            where(Mentor.tg_id == tg_id).
            values(**kwargs)
        )

        async with self.async_session.begin() as session:
            await session.execute(stmt)


    async def is_new_user(self, tg_id: int) -> bool:
        stmt = (
            select(User).
            where(User.tg_id == tg_id)
        )
        try:
            async with self.async_session.begin() as session:
                data = await session.execute(stmt)
                data.scalars().one()
                return False
        except NoResultFound:
            return True


    async def new_user(self, **kwargs) -> None:
        async with self.async_session.begin() as session:
            session.add(User(**kwargs))

    async def new_mentor(self, **kwargs) -> None:
        async with self.async_session.begin() as session:
            session.add(Mentor(**kwargs))

    async def delete_mentor(self, tg_id: int) -> None:
        stmt = (
            delete(Mentor).
            where(Mentor.tg_id == tg_id)
        )
        async with self.async_session.begin() as session:
            await session.execute(stmt)


    async def get_all_users(self):
        stmt = select(User)
        try:
            async with self.async_session.begin() as session:
                data = await session.execute(stmt)
                return data.scalars().all()
        except NoResultFound:
            return []


    async def get_all_mentors(self):
        stmt = (select(Mentor).where(Mentor.airtable_record_id.isnot(None)))
        try:
            async with self.async_session.begin() as session:
                data = await session.execute(stmt)
                return data.scalars().all()
        except NoResultFound:
            return []


    async def get_all_unsubscribers(self):
        stmt = (
            select(User)
            .where(
                User.is_subscriber.is_(None),
            )
        )

        try:
            async with self.async_session.begin() as session:
                data = await session.execute(stmt)
                return data.scalars().all()
        except NoResultFound:
            return []


    async def get_all_subscribers(self):
        stmt = (
            select(User)
            .where(
                User.is_subscriber.is_(True),
                User.subscription_start <= datetime.now(tz=timezone("Europe/Moscow")),
                User.subscription_end >= datetime.now(tz=timezone("Europe/Moscow"))
            )
        )

        try:
            async with self.async_session.begin() as session:
                data = await session.execute(stmt)
                return data.scalars().all()
        except NoResultFound:
            return []


async def get_db():
    db = Database()
    yield db
