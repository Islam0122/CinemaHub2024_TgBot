from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from .model import User, Cinema_by_code
from sqlalchemy import or_


async def orm_get_users(session: AsyncSession):
    async with session as s:
        result = await s.execute(select(User))
        return result.scalars().all()


async def orm_get_user(session: AsyncSession, user_id: int):
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def orm_get_user_by_telegram_id(session: AsyncSession, user_telegram_id: int):
    query = select(User).where(User.telegram_id == user_telegram_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def orm_add_user(session: AsyncSession, telegram_id: str, full_name: str, username: str):
    new_user = User(
        telegram_id=telegram_id,
        full_name=full_name,
        username=username,
    )
    async with session as s:
        s.add(new_user)
        await s.commit()
        return new_user


async def orm_add_cinema_by_code(session: AsyncSession, cinema_code: str, cinema_name: str):
    new_code = Cinema_by_code(
        cinema_code=cinema_code,
        cinema_name=cinema_name,
    )
    session.add(new_code)
    try:
        await session.commit()
        await session.refresh(new_code)
        return new_code
    except IntegrityError:
        await session.rollback()
        return None


async def orm_get_cinema_by_code(session: AsyncSession, cinema_code: str):
    query = select(Cinema_by_code).where(Cinema_by_code.cinema_code == cinema_code)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def orm_get_all_cinemas(session: AsyncSession):
    result = await session.execute(select(Cinema_by_code))
    return result.scalars().all()


async def orm_delete_cinema_by_code(session: AsyncSession, cinema_code: str):
    stmt = delete(Cinema_by_code).where(Cinema_by_code.cinema_code == cinema_code)
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount

