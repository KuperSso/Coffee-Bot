from typing import Optional
from database import async_session
from models import User
from sqlalchemy import select


async def add_user(tg_id: int, phone: str) -> None:
    async with async_session() as session:
        user = User(tg_id=tg_id, phone=phone)
        session.add(user)
        await session.commit()


async def get_user(tg_id: int) -> User | None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        return user


async def get_buy_coffee(tg_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        return user.buy_coffe


async def get_user_by_phone(phone: str) -> User | None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.phone == phone))
        return user


async def add_coffee(phone: str, coffee_count: int) -> bool:
    try:
        async with async_session() as session:
            user_phone = select(User).filter(User.phone == phone)
            result = await session.execute(user_phone)
            user = result.scalar_one_or_none()

            if not user:
                return False

            user.buy_coffe += coffee_count
            await session.commit()
            return True
    except Exception as e:
        print(f"Ошибка при добавлении кофе: {e}")
        return False


async def used_free_coffe(phone: str) -> bool:
    try:
        async with async_session() as session:
            user_phone = select(User).filter(User.phone == phone)
            result = await session.execute(user_phone)
            user = result.scalar_one_or_none()

            if not user:
                return False

            user.buy_coffe -= 5
            await session.commit()
            return True
    except Exception as e:
        print(f"Ошибка при списании кофе: {e}")
        return False


async def add_admin(phone: str) -> Optional[User]:
    async with async_session() as session:
        user_phone = select(User).filter(User.phone == phone)
        result = await session.execute(user_phone)
        user = result.scalar_one_or_none()

        if not user:
            return None

        user.is_admin = True
        await session.commit()
        session.expunge(user)
        return user


async def remove_admin(phone: str) -> Optional[User]:
    async with async_session() as session:
        user_phone = select(User).filter(User.phone == phone)
        result = await session.execute(user_phone)
        user = result.scalar_one_or_none()

        if not user:
            return None

        user.is_admin = False
        await session.commit()
        session.expunge(user)
        return user
