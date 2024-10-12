from datetime import datetime
from sqlalchemy import DateTime, BigInteger, String, func, Integer, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())


class User(Base):
    __tablename__ = 'User'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)  # Измените на BigInteger
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)


class Cinema_by_code(Base):
    __tablename__ = 'cinema_by_code'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cinema_code: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    cinema_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

