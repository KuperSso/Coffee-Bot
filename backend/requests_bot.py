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
