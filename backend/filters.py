from aiogram.filters import BaseFilter
from aiogram.types import Message
from requests_bot import get_user


class RegistrationFilter(BaseFilter):
    async def __call__(self, message: Message) -> dict | bool:
        user_id = message.from_user.id
        user = await get_user(user_id)

        return {"is_registered": user is not None, "user": user}
