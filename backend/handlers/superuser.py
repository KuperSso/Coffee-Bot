from aiogram import types, Router, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import async_session

import database.queries as rq
import keyboards as kb

from filters import IsSuperUserFilter

superuser_router = Router()


async def check_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()

    if not phone.startswith("8") or len(phone) != 11 or not phone.isdigit():
        await message.answer(
            "Введите корректный номер телефона, начинающийся с 8 и длиной 11 цифр.\nПример: 89012345678"
        )
        return None
    normalized_phone = phone[1:]

    async with async_session() as session:
        user = await rq.get_user_by_phone(normalized_phone, session=session)

    if not user:
        await message.answer(
            f"Пользователь с номером {phone} не найден.\nПроверьте правильность введенного номера и повторите попытку!"
        )
        return None

    await state.update_data(phone=normalized_phone)
    return normalized_phone


# Кнопка "Назад"


@superuser_router.message(F.text == "Назад", IsSuperUserFilter())
async def back_to_menu_superuser(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы вернулись в главное меню.", reply_markup=kb.menu_superuser)


# Приветствие Владельца


@superuser_router.message(Command("start"), IsSuperUserFilter())
async def is_superuser(message: types.Message):
    await message.answer(
        "<b>Привет, хозяин!\nВыбери следущее действие</b>&#128071;",
        reply_markup=kb.menu_superuser,
    )


# Добавление Баристы(админа) Суперпользователем(владельцем)


class AddIsAdminState(StatesGroup):
    waiting_for_phone_admin = State()
    admin_flag = State()


@superuser_router.message(F.text == "Добавить Баристу", IsSuperUserFilter())
async def start_admin_add(message: types.Message, state: FSMContext):
    await message.answer(
        "Чтобы ДОБАВИТЬ БАРИСТУ:\nВведите номер телефона пользователя начиная с 8!\n(Пример: 89012345678)"
    )
    await state.set_state(AddIsAdminState.waiting_for_phone_admin)


@superuser_router.message(AddIsAdminState.waiting_for_phone_admin)
async def validate_phone(message: types.Message, state: FSMContext):
    normalized_phone = await check_phone(message, state)
    if not normalized_phone:
        return

    await message.answer(
        f"Ты уверен, что хочешь НАЗНАЧИТЬ на должность БАРИСТЫ пользователя: {normalized_phone}?\n\nОтправь любое слово - и я сразу назначу его!\n\nЕсли ты ошибся нажми на кнопку добавления и начни сначала!"
    )
    await state.set_state(AddIsAdminState.admin_flag)


@superuser_router.message(AddIsAdminState.admin_flag)
async def add_admin(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    phone = user_data.get("phone")

    async with async_session() as session:
        user = await rq.get_user_by_phone(phone, session=session)

    if not user:
        await message.answer("Пользователь не найден.")
        await state.clear()
        return

    if user.is_admin:
        await message.answer("Этот пользователь уже бариста")
        await state.clear()
        return
    async with async_session() as session:
        success = await rq.add_admin(phone, session=session)

    if success:
        await message.answer(
            f"Пользователь: {phone} успешно стал баристой, мои соболезнования ему..."
        )
        chat = await message.bot.get_chat(user.tg_id)
        user_first_name = chat.first_name
        if user and user.tg_id:
            try:
                await message.bot.send_message(
                    user.tg_id,
                    f"Добро пожаловать в команду Sakura Michi, {user_first_name}\nПоздравляю тебя с должностью: Бариста!",
                )
            except Exception as e:
                await message.answer(f"Баристе не удалось отправить уведомление: {e}")
    else:
        await message.answer("Произошла ошибка при добавлении Баристы")

    await state.clear()


# Удаление Баристы(админа) Суперпользователем(владельцем)


class RemoveIsAdminState(StatesGroup):
    waiting_for_phone_admin = State()
    admin_flag = State()


@superuser_router.message(F.text == "Удалить Баристу", IsSuperUserFilter())
async def start_admin_remove(message: types.Message, state: FSMContext):
    await message.answer(
        "Чтобы УДАЛИТЬ БАРИСТУ:\nВведите номер телефона пользователя начиная с 8!\n(Пример: 89012345678)"
    )
    await state.set_state(RemoveIsAdminState.waiting_for_phone_admin)


@superuser_router.message(RemoveIsAdminState.waiting_for_phone_admin)
async def validate_phone_remove(message: types.Message, state: FSMContext):
    normalized_phone = await check_phone(message, state)
    if not normalized_phone:
        return

    await message.answer(
        f"Ты уверен, что хочешь Уволить пользователя: {normalized_phone}?\n\nОтправь любое слово - и я сразу уволю его!\n\nЕсли ты ошибся нажми на кнопку добавления и начни сначала!"
    )
    await state.set_state(RemoveIsAdminState.admin_flag)


@superuser_router.message(RemoveIsAdminState.admin_flag)
async def remove_admin(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    phone = user_data.get("phone")

    async with async_session() as session:
        user = await rq.get_user_by_phone(phone, session=session)
    if not user:
        await message.answer("Пользователь не найден.")
        await state.clear()
        return

    if user.is_admin is False:
        await message.answer("Этот пользователь не бариста")
        await state.clear()
        return
    async with async_session() as session:
        success = await rq.remove_admin(phone, session=session)

    if success:
        await message.answer(f"Пользователь: {phone}, успешно уволен!")
        chat = await message.bot.get_chat(user.tg_id)
        user_first_name = chat.first_name
        if user and user.tg_id:
            try:
                await message.bot.send_message(
                    user.tg_id,
                    f"Спасибо за время проведенное вместе, {user_first_name}. Мы желаем тебе успехов в дальнейшей карьере!\nC уважением команда Sakura Michi",
                )
            except Exception as e:
                await message.answer(f"Баристе не удалось отправить уведомление: {e}")
    else:
        await message.answer("Произошла ошибка при добавлении Баристы")

    await state.clear()
