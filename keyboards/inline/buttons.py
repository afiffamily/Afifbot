from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from locales.texts import TEXTS

# =========================================================
# 1. ASOSIY MENYU (Userlar uchun)
# =========================================================
def main_user_menu(lang):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=TEXTS["btn_menu"][lang], callback_data="menu_food"),
                InlineKeyboardButton(text=TEXTS["btn_promo"][lang], callback_data="menu_promo"),
            ],
            [
                InlineKeyboardButton(text=TEXTS["btn_cart"][lang], callback_data="menu_cart"),
                InlineKeyboardButton(text=TEXTS["btn_orders"][lang], callback_data="menu_orders"),
            ],
            [
                InlineKeyboardButton(text=TEXTS["btn_about"][lang], callback_data="menu_about"),
                InlineKeyboardButton(text=TEXTS["btn_contact"][lang], callback_data="menu_contact"),
            ],
            [
                InlineKeyboardButton(text=TEXTS["btn_settings"][lang], callback_data="menu_settings")
            ]
        ]
    )


# =========================================================
# 2. SOZLAMALAR TUGMALARI
# =========================================================
def get_settings_kb(lang):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=TEXTS["btn_edit_lang"][lang], callback_data="set_edit_lang")],
            [InlineKeyboardButton(text=TEXTS["btn_edit_phone"][lang], callback_data="set_edit_phone")],
            [InlineKeyboardButton(text=TEXTS["btn_edit_name"][lang], callback_data="set_edit_name")],
            [InlineKeyboardButton(text=TEXTS["btn_main_menu"][lang], callback_data="back_to_main")]
        ]
    )

def get_lang_kb(lang):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_set_uz"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_set_ru")
            ],
            [InlineKeyboardButton(text=TEXTS["back"][lang], callback_data="back_to_settings")]
        ]
    )

def back_to_settings_kb(lang):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=TEXTS["back"][lang], callback_data="back_to_settings")]
        ]
    )


# =========================================================
# 3. AKSIYA TUGMALARI (+ / - / SAVAT) 
# =========================================================
def get_promo_kb(lang, promo_id, quantity=1):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➖", callback_data=f"promo_minus_{promo_id}_{quantity}"),
                InlineKeyboardButton(text=f"{quantity}", callback_data="none"), 
                InlineKeyboardButton(text="➕", callback_data=f"promo_plus_{promo_id}_{quantity}"),
            ],
            [
                InlineKeyboardButton(text=TEXTS["btn_add_cart"][lang], callback_data=f"promo_add_{promo_id}_{quantity}")
            ],
            [
                InlineKeyboardButton(text=TEXTS["btn_main_menu"][lang], callback_data="back_to_main")
            ]
        ]
    )


# =========================================================
# 4. UNIVERSAL ORTGA TUGMASI
# =========================================================
def get_back_kb(lang):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=TEXTS["back"][lang], callback_data="back_to_main")]
        ]
    )