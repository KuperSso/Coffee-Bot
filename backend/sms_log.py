from aiogram import Bot

superuser = [6038243662]


async def send_log(bot: Bot, message: str):
    """
    Отправляет лог администратору(-ам).
    """
    if isinstance(superuser, list):
        for admin_id in superuser:
            try:
                await bot.send_message(admin_id, message)
            except Exception as e:
                print(f"Не удалось отправить сообщение администратору {admin_id}: {e}")
    else:
        try:
            await bot.send_message(superuser, message)
        except Exception as e:
            print(f"Не удалось отправить сообщение администратору {superuser}: {e}")
