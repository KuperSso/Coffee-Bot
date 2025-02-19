from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User
from sqlalchemy import select


async def add_user(tg_id: int, phone: str, session: AsyncSession) -> None:
    user = User(tg_id=tg_id, phone=phone)
    session.add(user)
    await session.commit()


async def get_user(tg_id: int, session: AsyncSession) -> User | None:
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    return user


async def get_buy_coffee(tg_id: int, session: AsyncSession) -> User | None:
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    return user.buy_coffe


async def get_user_by_phone(phone: str, session: AsyncSession) -> User | None:
    user = await session.scalar(select(User).where(User.phone == phone))
    return user


async def add_coffee(phone: str, coffee_count: int, session: AsyncSession) -> bool:
    try:
        result = await session.execute(select(User).filter(User.phone == phone))
        user = result.scalar_one_or_none()

        if not user:
            return False

        user.buy_coffe += coffee_count
        await session.commit()
        return True
    except Exception as e:
        print(f"Ошибка при добавлении кофе: {e}")
        return False


async def used_free_coffe(phone: str, session: AsyncSession) -> bool:
    try:
        result = await session.execute(select(User).filter(User.phone == phone))
        user = result.scalar_one_or_none()

        if not user:
            return False

        user.buy_coffe -= 5
        await session.commit()
        return True
    except Exception as e:
        print(f"Ошибка при списании кофе: {e}")
        return False


async def add_admin(phone: str, session: AsyncSession) -> Optional[User]:
    result = await session.execute(select(User).filter(User.phone == phone))
    user = result.scalar_one_or_none()

    if not user:
        return None

    user.is_admin = True
    await session.commit()
    session.expunge(user)
    return user


async def remove_admin(phone: str, session: AsyncSession) -> Optional[User]:
    result = await session.execute(select(User).filter(User.phone == phone))
    user = result.scalar_one_or_none()

    if not user:
        return None

    user.is_admin = False
    await session.commit()
    session.expunge(user)
    return user
