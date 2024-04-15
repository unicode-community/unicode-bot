from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, Text
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    tg_username: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_subscriber: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    subscription_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    subscription_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_subscribed_to_payments: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    payment_method_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    send_warning_1d: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    send_warning_7d: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

class Mentor(Base):
    __tablename__ = "mentors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(Text, nullable=True)
    descr: Mapped[str] = mapped_column(Text, nullable=True)
    price: Mapped[str] = mapped_column(Text, nullable=True)
    contact: Mapped[str] = mapped_column(Text, nullable=True)
    direction: Mapped[str] = mapped_column(Text, nullable=True)
    airtable_record_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
