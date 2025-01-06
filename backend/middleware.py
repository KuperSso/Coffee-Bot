from aiogram.dispatcher.middlewares.base import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import Message, Update
from requests_bot import get_user


class RegistrationMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        if hasattr(event, "message") and isinstance(event.message, Message):
            user_id = event.message.from_user.id
            user = await get_user(user_id)

            data["is registered"] = user is not None
            data["user"] = user

        return await handler(event, data)
