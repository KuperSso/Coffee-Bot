import os
from aiogram import Bot
from dotenv import load_dotenv

load_dotenv(".env")
superuser_env = os.getenv("TG_ID_SUPERUSER")

superuser = [int(superuser_env)]


async def send_log(bot: Bot, message: str):
    """
    Отправляет лог администратору(-ам).
    """
    for admin_id in superuser:
        try:
            await bot.send_message(admin_id, message)
        except Exception as e:
            print(f"Не удалось отправить сообщение администратору {admin_id}: {e}")
