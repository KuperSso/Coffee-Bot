from aiogram import types, Router, F
from aiogram.filters.command import Command
from database.db import async_session

import database.queries as rq
import keyboards as kb

from filters import RegistrationFilter


client_router = Router()

tg_url = "https://t.me/Sakura_Michi_Coffe"
inst_url = "https://www.instagram.com/sakura_michi__coffee?igsh=MWJqYmoyZ2JiaTNrZA=="
# Приветствие клиенту


@client_router.message(Command("start"), RegistrationFilter())
async def cmd_start(message: types.Message, is_registered: bool):
    if is_registered:
        await message.answer(
            f"<b>Sakura Michi приветствует Вас, {message.from_user.first_name}&#129303;\n\n"
            "Мы очень стараемся, постоянно совершенствуя рецепты.\n"
            "Чтобы ваши вкусовые сосочки сказали нам СПАСИБО!\n\n"
            "В данный момент у нас проходит АКЦИЯ&#9749;\n"
            "Сделай 9 ЛЮБЫХ покупок и получи любой напиток на выбор В ПОДАРОК &#127873;\n\n"
            "Так же можете ознакомится с нашими каналами, чтоб больше узнать о нас &#129505;\n"
            f"<a href='{tg_url}'>Telegram</a>\n"
            f"<a href='{inst_url}'>Instagram</a></b>",
            reply_markup=kb.menu_user,
        )
    else:
        await message.answer(
            f"<b>Sakura Michi приветствует Вас, {message.from_user.first_name}!\n\nДля участия в акции требуется регистрация&#10071;</b>",
            reply_markup=kb.not_registered,
        )


# Ловля апдейта контакта для регистрации


@client_router.message(F.contact)
async def registration(msg: types.Message):
    if msg.chat.id == msg.contact.user_id:
        full_namber = msg.contact.phone_number
        formatted_number = full_namber[-10:]

        if not formatted_number.startswith("9"):
            await msg.answer(
                "Некорректный номер телефона. Попробуйте снова или обратитесь к Баристе."
            )
            return
        async with async_session() as session:
            await rq.add_user(msg.chat.id, formatted_number, session=session)

        await msg.answer(
            f"<b>Sakura Michi приветствует Вас, {msg.from_user.first_name}&#129303;\n\n"
            "Мы очень стараемся, постоянно совершенствуя рецепты.\n"
            "Чтобы ваши вкусовые сосочки сказали нам СПАСИБО!\n\n"
            "В данный момент у нас проходит АКЦИЯ&#9749;\n"
            "Сделай 9 ЛЮБЫХ покупок и получи любой напиток на выбор В ПОДАРОК &#127873;\n\n"
            "Так же можете ознакомится с нашими каналами, чтоб больше узнать о нас &#129505;\n"
            f"<a href='{tg_url}'>Telegram</a>\n"
            f"<a href='{inst_url}'>Instagram</a></b>",
            reply_markup=kb.menu_user,
        )

    else:
        await msg.answer("Это не ваш контакт! Пожалуйста, введите СВОЙ номер телефона.")


# Кнопка "Мой профиль" для зарегистрированных пользователей


@client_router.message(F.text == "Мой профиль")
async def my_profile(msg: types.Message):
    tg_id = msg.from_user.id
    async with async_session() as session:
        buy_coffee = await rq.get_buy_coffee(tg_id, session=session)
    if buy_coffee < 9:
        bonus_coffee = 9 - buy_coffee
        await msg.answer(
            f"<b>{msg.from_user.first_name}, вы совершили: {buy_coffee} покупок(-ки)&#128722;\n\n"
            f"До FREE DRINK осталось: {bonus_coffee} покупок(-ки) &#127873</b> "
        )
    else:
        await msg.answer(
            f"<b>{msg.from_user.first_name}, вы совершили: {buy_coffee} покупок(-ки)&#128722;\n\nПоздравляем, Вам доступен FREE DRINK &#127873</b> "
        )


# Ответ ботом на любое сообщение (кроме команд)


@client_router.message()
async def non_command(msg: types.Message):
    await msg.answer(
        "<b>Уважаемый Клиент!\nЯ не понимаю сообщения подобного характера, воспользуйтесь кнопкой&#129325;</b>"
    )
