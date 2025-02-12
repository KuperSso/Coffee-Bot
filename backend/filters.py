from aiogram.filters import BaseFilter
from aiogram.types import Message
from queries import get_user


class RegistrationFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user_id = message.from_user.id
        user = await get_user(user_id)
        return {"is_registered": bool(user), "user": user}


class IsadminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user_id = message.from_user.id
        user = await get_user(user_id)
        return bool(user) and user.is_admin


class IsSuperUserFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user_id = message.from_user.id
        user = await get_user(user_id)
        return bool(user) and user.is_superuser
