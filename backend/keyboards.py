from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

not_registered = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="Регистрация",
                request_contact=True,
                # input_field_placeholder="Тапни на кнопку ниже!",
            )
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Поделись скорей контактом, чтобы зарегистрироваться!",
)

menu_user = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="Мой профиль",
            )
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Тапни на кнопку для получения информации о своем счетчике!",
)

menu_admin = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить Кофе")],
        [KeyboardButton(text="Выдать Бесплатный Кофе")],
    ],
    resize_keyboard=True,
)

menu_superuser = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Добавить Баристу"),
            KeyboardButton(text="Удалить Баристу"),
        ],
        [
            KeyboardButton(text="Добавить Кофе"),
            KeyboardButton(text="Выдать Бесплатный Кофе"),
        ],
    ],
    resize_keyboard=True,
)
