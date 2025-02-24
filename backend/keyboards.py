from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

not_registered = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="Регистрация",
                request_contact=True,
            )
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Поделись скорей контактом!",
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
    input_field_placeholder="Тапни на кнопку ниже!",
)

menu_admin = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить Покупку")],
        [KeyboardButton(text="Выдать Бесплатный Напиток")],
        [KeyboardButton(text="Назад")],
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
            KeyboardButton(text="Добавить Покупку"),
            KeyboardButton(text="Выдать Бесплатный Напиток"),
        ],
        [KeyboardButton(text="Назад")],
    ],
    resize_keyboard=True,
)
