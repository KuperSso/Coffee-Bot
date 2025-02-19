from aiogram.filters import BaseFilter
from aiogram.types import Message
from database.queries import get_user
from database.db import async_session


class RegistrationFilter(BaseFilter):
    async def __call__(self, message: Message) -> dict:
        tg_id = message.from_user.id
        async with async_session() as session:
            user = await get_user(tg_id=tg_id, session=session)
        return {"is_registered": bool(user), "user": user}


class IsadminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        tg_id = message.from_user.id
        async with async_session() as session:
            user = await get_user(tg_id=tg_id, session=session)
        return bool(user) and user.is_admin


class IsSuperUserFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        tg_id = message.from_user.id
        async with async_session() as session:
            user = await get_user(tg_id=tg_id, session=session)
        return bool(user) and user.is_superuser
