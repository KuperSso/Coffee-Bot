from aiogram import types, Router, F
from aiogram.filters.command import Command

from requests_bot import add_user, get_buy_coffee
from filters import RegistrationFilter, IsadminFilter, IsSuperUserFilter
from middleware import RegistrationMiddleware
import keyboards as kb


router = Router()
router.message.middleware(RegistrationMiddleware())


@router.message(Command("start"), RegistrationFilter(), IsSuperUserFilter())
async def is_superuser(message: types.Message, user: dict | None):
    if user.is_superuser:
        await message.answer(
            "<b>Привет, хозяин!\nВыбери следущее действие</b>&#128071;",
            reply_markup=kb.menu_superuser,
        )


@router.message(Command("start"), RegistrationFilter(), IsadminFilter())
async def is_admin(message: types.Message, user: dict | None):
    if user.is_admin:
        await message.answer(
            "<b>Привет, Бариста!\nВыбери следущее действие</b>&#128071;",
            reply_markup=kb.menu_admin,
        )


@router.message(Command("start"), RegistrationFilter())
async def cmd_start(message: types.Message, is_registered: bool):
    if is_registered:
        await message.answer(
            f"<b>Sakura Michi приветствует Вас, {message.from_user.first_name}&#129303;\n\nМы очень стараемся, постоянно совершенствуя рецепты, согласно Японским традициям.\nЧтобы ваши вкусовые сосочки сказали нам СПАСИБО!\n\nВ данный момент у нас проходит АКЦИЯ&#9749;\nКупи 5 больших стаканов любого кофе и получи 6-ой В ПОДАРОК &#127873;</b>",
            reply_markup=kb.menu_user,
        )
    else:
        await message.answer(
            f"<b>Sakura Michi приветствует Вас, {message.from_user.first_name}!\n\nДля дальнешего участия в акции требуется регистрация&#10071;</b>",
            reply_markup=kb.not_registered,
        )


@router.message(F.contact)
async def registration(msg: types.Message):
    if msg.chat.id == msg.contact.user_id:
        await add_user(msg.chat.id, msg.contact.phone_number)
        await msg.answer(
            f"<b>Sakura Michi приветствует Вас, {msg.from_user.first_name}&#129303;\n\nМы очень стараемся для, Вас, постоянно совершенствуя рецепты, согласно Японским традициям.\nЧтобы ваши вкусовые сосочки сказали нам СПАСИБО!\n\nВ данный момент у нас проходит АКЦИЯ&#9749;\nКупи 5 больших стаканов любого кофе и получи 6-ой В ПОДАРОК &#127873;</b>",
            # reply_markup=types.ReplyKeyboardRemove(),
            reply_markup=kb.menu_user,
        )
    else:
        await msg.answer("Это не Ваш контакт!Введите СВОЙ номер телефона!")


@router.message(F.text == "Мой профиль")
async def my_profile(msg: types.Message):
    tg_id = msg.from_user.id
    buy_coffee = await get_buy_coffee(tg_id)
    await msg.reply(f"{msg.from_user.first_name}, ваш балланс: {buy_coffee}")
