import os
from dotenv import load_dotenv

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from handlers import admin_router, superuser_router, client_router

load_dotenv()


async def main():
    bot = Bot(
        token=os.getenv("bot_token"),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(superuser_router)
    dp.include_router(admin_router)
    dp.include_router(client_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
