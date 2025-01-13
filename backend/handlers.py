from aiogram import types, Router, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import queries as rq
import keyboards as kb

from filters import RegistrationFilter, IsadminFilter, IsSuperUserFilter
from middleware import RegistrationMiddleware


router = Router()
router.message.middleware(RegistrationMiddleware())


# Приветственные хендлеры для Суперпользователя(владельца), Админа(баристы)
# Авторизованных/неавторизованных пользователей


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


# Хендлер для ловли апдейта с контактом незарегистрированных пользователей


@router.message(F.contact)
async def registration(msg: types.Message):
    if msg.chat.id == msg.contact.user_id:
        full_namber = msg.contact.phone_number
        formatted_number = (
            full_namber[-10:] if full_namber.startswith("+") else full_namber[-10:]
        )

        if not formatted_number.startswith("9"):
            await msg.answer(
                "Некорректный номер телефона. Попробуйте снова или обратитесь к Баристе."
            )
            return
        await rq.add_user(msg.chat.id, formatted_number)
        await msg.answer(
            f"<b>Sakura Michi приветствует Вас, {msg.from_user.first_name}&#129303;\n\nМы очень стараемся для, Вас, постоянно совершенствуя рецепты, согласно Японским традициям.\nЧтобы ваши вкусовые сосочки сказали нам СПАСИБО!\n\nВ данный момент у нас проходит АКЦИЯ&#9749;\nКупи 5 больших стаканов любого кофе и получи 6-ой В ПОДАРОК &#127873;</b>",
            reply_markup=kb.menu_user,
        )

    else:
        await msg.answer("Это не ваш контакт! Пожалуйста, введите СВОЙ номер телефона.")


# Хендлер на кнопку профиля для зарегистрированных пользователей


@router.message(F.text == "Мой профиль")
async def my_profile(msg: types.Message):
    tg_id = msg.from_user.id
    buy_coffee = await rq.get_buy_coffee(tg_id)
    if buy_coffee < 5:
        bonus_coffee = 5 - buy_coffee
        await msg.answer(
            f"<b>{msg.from_user.first_name}, вы купили: {buy_coffee} стакана(ов) &#9749;\n\nДо FREE COFFEE осталось: {bonus_coffee} стакана(ов) &#127873</b> "
        )
    else:
        await msg.answer(
            f"<b>{msg.from_user.first_name}, вы купили: {buy_coffee} стакана(ов) &#9749;\n\nПоздравляем, Вам доступен FREE COFFEE &#127873</b> "
        )


# Добавление кофе пользователю


class CoffeeState(StatesGroup):
    waiting_for_phone = State()
    waiting_for_buy_coffe = State()


@router.message(
    F.text == "Добавить Кофе",
    RegistrationFilter(),
    IsadminFilter(),
)
async def start_add_coffee(message: types.Message, state: FSMContext):
    await message.answer(
        "Для ДОБАВЛЕНИЯ КОФЕ пользователю:\nВведите номер телефона пользователя начиная с 8!\n(Пример: 89012345678)"
    )
    await state.set_state(CoffeeState.waiting_for_phone)


@router.message(CoffeeState.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()

    if not phone.startswith("8") or len(phone) != 11 or not phone.isdigit():
        await message.answer(
            "Введите корректный номер телефона, начинающийся с 8 и длиной 11 цифр.\nПример: 89012345678"
        )
        return

    normalized_phone = phone[1:]

    user = await rq.get_user_by_phone(normalized_phone)
    if not user:
        await message.answer(
            f"Пользователь с номером {phone} не найден.\nПроверьте правильность введенного номера и повторите попытку!"
        )
        return

    await state.update_data(phone=normalized_phone)

    await message.answer("Введите количество купленных кофе:")
    await state.set_state(CoffeeState.waiting_for_buy_coffe)


@router.message(CoffeeState.waiting_for_buy_coffe)
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

    success = await rq.add_coffee(phone, buy_coffe)

    if success:
        await message.answer(
            f"Добавлено {buy_coffe} кофе для пользователя с номером {phone}."
        )
        user = await rq.get_user_by_phone(phone)
        if user and user.tg_id:
            try:
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


@router.message(
    F.text == "Выдать Бесплатный Кофе",
    RegistrationFilter(),
    IsadminFilter(),
)
async def start_used_coffee(message: types.Message, state: FSMContext):
    await message.answer(
        "Для выдачи БЕСПЛАТНОГО КОФЕ:\nВедите номер телефона пользователя начиная с 8!\n(Пример: 89012345678)"
    )
    await state.set_state(FreeCoffeeStates.waiting_for_phone)


@router.message(FreeCoffeeStates.waiting_for_phone)
async def process_phone_check(message: types.Message, state: FSMContext):
    phone = message.text.strip()

    if not phone.startswith("8") or len(phone) != 11 or not phone.isdigit():
        await message.answer(
            "Введите корректный номер телефона, начинающийся с 8 и длиной 11 цифр.\n(Пример: 89012345678)"
        )
        return

    normalized_phone = phone[1:]

    try:
        user = await rq.get_user_by_phone(normalized_phone)
    except Exception as e:
        await message.answer(f"Ошибка при запросе пользователя: {e}")
        return

    if not user:
        await message.answer(
            f"Пользователь с номером {phone} не найден.\nПроверьте правильность введенного номера и повторите попытку!"
        )
        return

    await state.update_data(phone=normalized_phone)
    await message.answer(
        f"Ты уверен, что хочешь выдать БЕСПЛАТНЫЙ КОФЕ пользователю: {phone}?\n\nОтправь любое слово - и я сразу выдам!\n\nЕсли ты ошибся нажми на кнопку выдачи и начни сначала!"
    )

    await state.set_state(FreeCoffeeStates.confirming_usage)


@router.message(FreeCoffeeStates.confirming_usage)
async def process_coffee_used(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    phone = user_data.get("phone")

    user = await rq.get_user_by_phone(phone)
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

    success = await rq.used_free_coffe(phone)

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


# Добавление Баристы(админа) Суперпользователем(владельцем)


class AddIsAdminState(StatesGroup):
    waiting_for_phone_admin = State()
    admin_flag = State()


@router.message(F.text == "Добавить Баристу", RegistrationFilter(), IsSuperUserFilter())
async def start_admin_add(message: types.Message, state: FSMContext):
    await message.answer(
        "Чтобы ДОБАВИТЬ БАРИСТУ:\nВведите номер телефона пользователя начиная с 8!\n(Пример: 89012345678)"
    )
    await state.set_state(AddIsAdminState.waiting_for_phone_admin)


@router.message(AddIsAdminState.waiting_for_phone_admin)
async def check_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()

    if not phone.startswith("8") or len(phone) != 11 or not phone.isdigit():
        await message.answer(
            "Введите корректный номер телефона, начинающийся с 8 и длиной 11 цифр.\n(Пример: 89012345678)"
        )
        return

    normalized_phone = phone[1:]

    try:
        user = await rq.get_user_by_phone(normalized_phone)
    except Exception as e:
        await message.answer(f"Ошибка при запросе пользователя: {e}")
        return

    if not user:
        await message.answer(
            f"Пользователь с номером {phone} не найден.\nПроверьте правильность введенного номера и повторите попытку!"
        )
        return

    await state.update_data(phone=normalized_phone)
    await message.answer(
        f"Ты уверен, что хочешь НАЗНАЧИТЬ на должность БАРИСТЫ пользователя: {phone}?\n\nОтправь любое слово - и я сразу назначу его!\n\nЕсли ты ошибся нажми на кнопку добавления и начни сначала!"
    )

    await state.set_state(AddIsAdminState.admin_flag)


@router.message(AddIsAdminState.admin_flag)
async def add_admin(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    phone = user_data.get("phone")

    user = await rq.get_user_by_phone(phone)
    if not user:
        await message.answer("Пользователь не найден.")
        await state.clear()
        return

    if user.is_admin:
        await message.answer("Этот пользователь уже бариста")
        await state.clear()
        return

    success = await rq.add_admin(phone)

    if success:
        await message.answer(
            f"Пользователь: {phone} успешно стал баристой, мои соболезнования ему..."
        )
        user = await rq.get_user_by_phone(phone)
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


@router.message(F.text == "Удалить Баристу", RegistrationFilter(), IsSuperUserFilter())
async def start_admin_remove(message: types.Message, state: FSMContext):
    await message.answer(
        "Чтобы УДАЛИТЬ БАРИСТУ:\nВведите номер телефона пользователя начиная с 8!\n(Пример: 89012345678)"
    )
    await state.set_state(RemoveIsAdminState.waiting_for_phone_admin)


@router.message(RemoveIsAdminState.waiting_for_phone_admin)
async def check_phone_admin(message: types.Message, state: FSMContext):
    phone = message.text.strip()

    if not phone.startswith("8") or len(phone) != 11 or not phone.isdigit():
        await message.answer(
            "Введите корректный номер телефона, начинающийся с 8 и длиной 11 цифр.\n(Пример: 89012345678)"
        )
        return

    normalized_phone = phone[1:]

    try:
        user = await rq.get_user_by_phone(normalized_phone)
    except Exception as e:
        await message.answer(f"Ошибка при запросе пользователя: {e}")
        return

    if not user:
        await message.answer(
            f"Пользователь с номером {phone} не найден.\nПроверьте правильность введенного номера и повторите попытку!"
        )
        return

    await state.update_data(phone=normalized_phone)
    await message.answer(
        f"Ты уверен, что хочешь Уволить пользователя: {phone}?\n\nОтправь любое слово - и я сразу уволю его!\n\nЕсли ты ошибся нажми на кнопку добавления и начни сначала!"
    )

    await state.set_state(RemoveIsAdminState.admin_flag)


@router.message(RemoveIsAdminState.admin_flag)
async def remove_admin(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    phone = user_data.get("phone")

    user = await rq.get_user_by_phone(phone)
    if not user:
        await message.answer("Пользователь не найден.")
        await state.clear()
        return

    if user.is_admin is False:
        await message.answer("Этот пользователь не бариста")
        await state.clear()
        return

    success = await rq.remove_admin(phone)

    if success:
        await message.answer(f"Пользователь: {phone}, успешно уволен!")
        user = await rq.get_user_by_phone(phone)
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


# Ответ ботом на любое сообщение (кроме команд)


@router.message()
async def non_command(msg: types.Message):
    await msg.answer(
        "<b>Уважаемый Клиент!\nЯ не понимаю сообщения подобного характера, воспользуйтесь кнопкой&#129325;</b>"
    )
