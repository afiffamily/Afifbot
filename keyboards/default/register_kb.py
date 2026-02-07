from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

lang_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🇺🇿 O'zbekcha"),
            KeyboardButton(text="🇷🇺 Русский")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

phone_kb_uz = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

phone_kb_ru = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📞 Отправить номер телефона", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)