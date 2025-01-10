from aiogram import types, Router, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from queries import add_user, get_buy_coffee, get_user_by_phone, add_coffee
from filters import RegistrationFilter, IsadminFilter, IsSuperUserFilter
from middleware import RegistrationMiddleware
import keyboards as kb


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
        await add_user(msg.chat.id, formatted_number)
        await msg.answer(
            f"<b>Sakura Michi приветствует Вас, {msg.from_user.first_name}&#129303;\n\nМы очень стараемся для, Вас, постоянно совершенствуя рецепты, согласно Японским традициям.\nЧтобы ваши вкусовые сосочки сказали нам СПАСИБО!\n\nВ данный момент у нас проходит АКЦИЯ&#9749;\nКупи 5 больших стаканов любого кофе и получи 6-ой В ПОДАРОК &#127873;</b>",
            reply_markup=kb.menu_user,
        )

    else:
        await msg.answer("Это не ваш контакт! Пожалуйста, введите СВОЙ номер телефона.")


# Хендлер для зарегистрированных пользователей на кнопку профиля


@router.message(F.text == "Мой профиль")
async def my_profile(msg: types.Message):
    tg_id = msg.from_user.id
    buy_coffee = await get_buy_coffee(tg_id)
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


class AddCoffeeState(StatesGroup):
    waiting_for_phone = State()
    waiting_for_buy_coffe = State()


@router.message(
    F.text == "Добавить Кофе",
    RegistrationFilter(),
    IsadminFilter(),
)
async def start_add_coffee(message: types.Message, state: FSMContext):
    await message.answer(
        "Введите номер телефона пользователя начиная с 8:\nПример: 89012345678"
    )
    await state.set_state(AddCoffeeState.waiting_for_phone)


@router.message(AddCoffeeState.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()

    if not phone.startswith("8") or len(phone) != 11 or not phone.isdigit():
        await message.answer(
            "Введите корректный номер телефона, начинающийся с 8 и длиной 11 цифр.\nПример: 89012345678"
        )
        return

    normalized_phone = phone[1:]

    user = await get_user_by_phone(normalized_phone)
    if not user:
        await message.answer(
            f"Пользователь с номером {phone} не найден.\nПроверьте правильность введенного номера и повторите попытку!"
        )
        return

    await state.update_data(phone=normalized_phone)

    await message.answer("Введите количество купленных кофе:")
    await state.set_state(AddCoffeeState.waiting_for_buy_coffe)


@router.message(AddCoffeeState.waiting_for_buy_coffe)
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

    success = await add_coffee(phone, buy_coffe)

    if success:
        await message.answer(
            f"Добавлено {buy_coffe} кофе для пользователя с номером {phone}."
        )
    else:
        await message.answer(
            f"Произошла ошибка при добавлении кофе для пользователя с номером {phone}."
        )
    await state.clear()


# Ответ ботом на любое из сообщений кроме кнопок


@router.message()
async def non_command(msg: types.Message):
    await msg.answer(
        "<b>Уважаемый Клиент!\nЯ не понимаю сообщения подобного характера, воспользуйся кнопкой&#129325;</b>"
    )
