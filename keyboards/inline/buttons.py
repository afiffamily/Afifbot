from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from locales.texts import TEXTS

# =========================================================
# 1. ASOSIY MENYU (Userlar uchun)
# =========================================================
def main_user_menu(lang):
    kb = InlineKeyboardBuilder()
    kb.button(text=TEXTS["btn_menu"][lang], callback_data="menu_food")
    kb.button(text=TEXTS["btn_promo"][lang], callback_data="menu_promo")
    kb.button(text=TEXTS["btn_orders"][lang], callback_data="menu_orders")
    kb.button(text=TEXTS["btn_about"][lang], callback_data="menu_about")
    kb.button(text=TEXTS["btn_contact"][lang], callback_data="menu_contact")
    kb.button(text=TEXTS["btn_settings"][lang], callback_data="menu_settings")
    kb.adjust(1, 1, 2, 2)
    return kb.as_markup()


# =========================================================
# 2. SOZLAMALAR TUGMALARI
# =========================================================
def get_settings_kb(lang):
    kb = InlineKeyboardBuilder()
    kb.button(text=TEXTS["btn_edit_lang"][lang], callback_data="set_edit_lang")
    kb.button(text=TEXTS["btn_edit_phone"][lang], callback_data="set_edit_phone")
    kb.button(text=TEXTS["btn_edit_name"][lang], callback_data="set_edit_name")
    kb.button(text=TEXTS["back"][lang], callback_data="back_to_main")
    kb.adjust(1)
    return kb.as_markup()

def get_lang_kb(lang):
    kb = InlineKeyboardBuilder()
    kb.button(text="🇺🇿 O'zbekcha", callback_data="lang_set_uz")
    kb.button(text="🇷🇺 Русский", callback_data="lang_set_ru")
    kb.button(text=TEXTS["back"][lang], callback_data="back_to_settings")
    kb.adjust(1)
    return kb.as_markup()

def back_to_settings_kb(lang):
    kb = InlineKeyboardBuilder()
    kb.button(text=TEXTS["back"][lang], callback_data="back_to_settings")
    return kb.as_markup()


# =========================================================
# 3. AKSIYA TUGMALARI (+ / - / SAVAT) 
# =========================================================
def get_promo_kb(lang, promo_id, quantity=1):
    kb = InlineKeyboardBuilder()
    
    kb.button(text="➖", callback_data=f"promo_minus_{promo_id}_{quantity}")
    kb.button(text=f"{quantity}", callback_data="none")
    kb.button(text="➕", callback_data=f"promo_plus_{promo_id}_{quantity}")
    kb.button(text=TEXTS["btn_add_cart"][lang], callback_data=f"promo_add_{promo_id}_{quantity}")
    kb.button(text=TEXTS["back"][lang], callback_data="back_to_main")
    kb.adjust(3, 1, 1)
    return kb.as_markup()


# =========================================================
# 4. UNIVERSAL ORTGA TUGMASI
# =========================================================
def get_back_kb(lang):
    kb = InlineKeyboardBuilder()
    kb.button(text=TEXTS["back"][lang], callback_data="back_to_main")
    return kb.as_markup()
