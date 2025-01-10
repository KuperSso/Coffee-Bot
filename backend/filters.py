from aiogram.filters import BaseFilter
from aiogram.types import Message
from queries import get_user
from typing import Optional


class RegistrationFilter(BaseFilter):
    async def __call__(self, message: Message) -> dict | bool:
        user_id = message.from_user.id
        user = await get_user(user_id)
        return {"is_registered": user is not None, "user": user}


class IsadminFilter(BaseFilter):
    async def __call__(self, message: Message, user: Optional[dict]) -> bool:
        return user and getattr(user, "is_admin", False)


class IsSuperUserFilter(BaseFilter):
    async def __call__(self, message: Message, user: Optional[dict]) -> bool:
        return user and getattr(user, "is_superuser", False)
