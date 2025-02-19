from aiogram import types, Router, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database.queries as rq
from database.db import async_session
import keyboards as kb

from filters import IsadminFilter
from sms_log import send_log
from handlers.superuser import check_phone

admin_router = Router()


# Приветствие Баристы


@admin_router.message(Command("start"), IsadminFilter())
async def is_admin(message: types.Message):
    await message.answer(
        "<b>Привет, Бариста!\nВыбери следущее действие</b>&#128071;",
        reply_markup=kb.menu_admin,
    )


# Кнопка "Назад"


@admin_router.message(F.text == "Назад", IsadminFilter())
async def back_to_menu_admin(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы вернулись в главное меню.", reply_markup=kb.menu_admin)


# Добавление кофе пользователю


class CoffeeState(StatesGroup):
    waiting_for_phone = State()
    waiting_for_buy_coffe = State()


@admin_router.message(
    F.text == "Добавить Кофе",
    IsadminFilter(),
)
async def start_add_coffee(message: types.Message, state: FSMContext):
    await message.answer(
        "Для ДОБАВЛЕНИЯ КОФЕ пользователю:\nВведите номер телефона пользователя начиная с 8!\n(Пример: 89012345678)"
    )
    await state.set_state(CoffeeState.waiting_for_phone)


@admin_router.message(CoffeeState.waiting_for_phone)
async def validate_phone(message: types.Message, state: FSMContext):
    normalized_phone = await check_phone(message, state)
    if not normalized_phone:
        return

    await message.answer("Введите количество купленных кофе:")
    await state.set_state(CoffeeState.waiting_for_buy_coffe)


@admin_router.message(CoffeeState.waiting_for_buy_coffe)
async def process_coffee_count(message: types.Message, state: FSMContext):
    try:
        buy_coffe = int(message.text.strip())
        if buy_coffe <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Введите положительное число кофе.")
        return

    user_data = await state.get_data()
    phone = user_data.get("phone")

    async with async_session() as session:
        success = await rq.add_coffee(phone, buy_coffe, session=session)

    if success:
        await message.answer(
            f"Добавлено {buy_coffe} кофе для пользователя с номером {phone}."
        )
        async with async_session() as session:
            user = await rq.get_user_by_phone(phone, session=session)
        if user and user.tg_id:
            try:
                log_message = (
                    f"Пользователю с номером {phone} "
                    f"начислено {buy_coffe} кофе.\n"
                    f"Текущий баланс: {user.buy_coffe} стакан(а)."
                )
                await send_log(message.bot, log_message)
                await message.bot.send_message(
                    user.tg_id,
                    f"<b>Вам начислено {buy_coffe} стакан(а) кофе.\nВаш текущий баланс: {user.buy_coffe} стакан(а).</b>",
                )
            except Exception as e:
                await message.answer(f"Клиенту не удалось отправить уведомление: {e}")
    else:
        await message.answer(
            f"Произошла ошибка при добавлении кофе для пользователя с номером {phone}."
        )
    await state.clear()


# Выдать подарочный кофе(тем самым списываем 5 стаканов со счета клиента)


class FreeCoffeeStates(StatesGroup):
    waiting_for_phone = State()
    confirming_usage = State()


@admin_router.message(
    F.text == "Выдать Бесплатный Кофе",
    IsadminFilter(),
)
async def start_used_coffee(message: types.Message, state: FSMContext):
    await message.answer(
        "Для выдачи БЕСПЛАТНОГО КОФЕ:\nВедите номер телефона пользователя начиная с 8!\n(Пример: 89012345678)"
    )
    await state.set_state(FreeCoffeeStates.waiting_for_phone)


@admin_router.message(FreeCoffeeStates.waiting_for_phone)
async def process_phone_check(message: types.Message, state: FSMContext):
    normalized_phone = await check_phone(message, state)
    if not normalized_phone:
        return
    await message.answer(
        f"Ты уверен, что хочешь выдать БЕСПЛАТНОЕ КОФЕ пользователю: {message.text.strip()}?\n\n"
        f"Отправь любое слово - и я сразу выдам!\n\n"
        f"Если ты ошибся, нажми на кнопку выдачи и начни сначала!"
    )
    await state.set_state(FreeCoffeeStates.confirming_usage)


@admin_router.message(FreeCoffeeStates.confirming_usage)
async def process_coffee_used(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    phone = user_data.get("phone")

    async with async_session() as session:
        user = await rq.get_user_by_phone(phone, session=session)
    if not user:
        await message.answer("Пользователь не найден.")
        await state.clear()
        return

    if user.buy_coffe < 5:
        await message.answer(
            f"Недостаточно кофе для выдачи бесплатного стакана. "
            f"На счету пользователя: {user.buy_coffe} стаканов."
        )
        await state.clear()
        return
    async with async_session() as session:
        success = await rq.used_free_coffe(phone, session=session)

    if success:
        await message.answer("Выдаю бесплатный кофе...")
        await message.answer(
            f"Выдан бесплатный кофе для пользователя с номером {phone}. "
            f"Оставшееся количество: {user.buy_coffe - 5}"
        )
        try:
            await message.bot.send_message(
                user.tg_id,
                f"<b>Поздравляем, Вы получили БЕСПЛАТНЫЙ КОФЕ&#127873;\nВаш текущий баланс: {user.buy_coffe - 5} стакана(ов).</b>",
            )
        except Exception as e:
            await message.answer(f"Клиенту не удалось отправить уведомление: {e}")
    else:
        await message.answer(
            f"Произошла ошибка при выдаче кофе для пользователя с номером {phone}."
        )
    await state.clear()
