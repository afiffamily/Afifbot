from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

super_admin_panel = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Kengaytirilgan Statistika")],
        [
            KeyboardButton(text="🔥 Aksiyalar"),
            KeyboardButton(text="🍴 Menyu va Mahsulotlar")
        ],
        [
            KeyboardButton(text="📢 Smart Marketing"),
            KeyboardButton(text="👥 HR (Xodimlar)"),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Afifbot Boshqaruv Markazi"
)

admin_panel = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Kunlik hisobot")],
        [
            KeyboardButton(text="🔥 Aksiyalar"),
            KeyboardButton(text="🍴 Menyu va Mahsulotlar")
        ],
        [
            KeyboardButton(text="📢 Smart Marketing"),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Ishchi Panel"
)

back_button = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔙 Ortga")]],
    resize_keyboard=True
)