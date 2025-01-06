from aiogram import types, Router, F
from aiogram.filters.command import Command
from aiogram.utils.formatting import Text, Bold

from requests_bot import add_user
from filters import RegistrationFilter
from middleware import RegistrationMiddleware

router = Router()
router.message.middleware(RegistrationMiddleware())


@router.message(Command("start"), RegistrationFilter())
async def cmd_start(message: types.Message, is_registered: bool):
    if is_registered:
        kb = [
            [types.KeyboardButton(text="Что-то")],
            [types.KeyboardButton(text="Что-то")],
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
        content = Text(
            "C Возвращением, ",
            Bold(message.from_user.full_name),
            ".\n",
            "Для продолжения, воспользуйтесь пожалуйста меню...",
        )
        await message.answer(**content.as_kwargs(), reply_markup=keyboard)
    else:
        kb = [
            [types.KeyboardButton(text="Отправить номер", request_contact=True)],
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
        content = Text(
            "Приветствую, Дорогой, ",
            Bold(message.from_user.full_name),
            ".\n",
            "Для продолжения просим, Вас, зарегистрироваться!",
        )

    await message.answer(**content.as_kwargs(), reply_markup=keyboard)


@router.message(F.contact)
async def registration(msg: types.Message):
    if msg.chat.id == msg.contact.user_id:
        await add_user(msg.chat.id, msg.contact.phone_number)
        await msg.answer(
            f"Твой номер успешно получен: {msg.contact.phone_number}",
            reply_markup=types.ReplyKeyboardRemove(),
        )
    else:
        await msg.answer("Это не Ваш контакт!Введите СВОЙ номер телефона!")
