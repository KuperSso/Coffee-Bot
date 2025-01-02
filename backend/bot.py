import os
from dotenv import load_dotenv

import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

load_dotenv()

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv('bot_token'))
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")

async def main():
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    asyncio.run(main())