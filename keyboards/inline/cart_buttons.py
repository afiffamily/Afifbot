from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from locales.texts import TEXTS

# 1. SAVAT TUGMALARI
def cart_markup(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=TEXTS["btn_order"][lang], callback_data="order_start")],
        [InlineKeyboardButton(text=TEXTS["btn_clear"][lang], callback_data="cart_clear")],
        [InlineKeyboardButton(text=TEXTS["btn_main_menu"][lang], callback_data="back_to_main")]
    ])

# 2. YETKAZIB BERISH TURI
def delivery_type_markup(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=TEXTS["btn_delivery"][lang], callback_data="dlv_delivery")],
        [InlineKeyboardButton(text=TEXTS["btn_pickup"][lang], callback_data="dlv_pickup")],
        [InlineKeyboardButton(text=TEXTS["back"][lang], callback_data="back_to_cart")]
    ])

# 3. LOKATSIYA SO'RASH (REPLY)
def location_markup(lang):
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=TEXTS["btn_location"][lang], request_location=True)]
    ], resize_keyboard=True, one_time_keyboard=True)

# 4. TELEFON SO'RASH (REPLY)
def phone_markup(lang):
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=TEXTS["btn_contact"][lang], request_contact=True)]
    ], resize_keyboard=True, one_time_keyboard=True)

# 5. TO'LOV TURI
def payment_type_markup(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=TEXTS["btn_cash"][lang], callback_data="pay_cash")],
        [InlineKeyboardButton(text=TEXTS["btn_card"][lang], callback_data="pay_card")],
    ])

# 6. TASDIQLASH
def confirm_order_markup(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=TEXTS["btn_confirm"][lang], callback_data="order_confirm")],
        [InlineKeyboardButton(text=TEXTS["btn_cancel"][lang], callback_data="order_cancel")]
    ])

def saved_address_markup(lang, address):
    short_addr = address[:25] + "..." if len(address) > 25 else address
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"📍 {short_addr}", callback_data="use_saved_addr")],
        [InlineKeyboardButton(text=TEXTS["btn_new_address"][lang], callback_data="use_new_addr")],
        [InlineKeyboardButton(text=TEXTS["back"][lang], callback_data="back_to_cart")]
    ])