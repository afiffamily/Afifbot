from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from locales.texts import TEXTS

def get_contact_kb(lang):
    ADMIN_USERNAME = "@sotuvmenejeri_afif"
    INSTAGRAM_LINK = "https://www.instagram.com/afif_shirinliklari?igsh=Z2V4ZjFmMmh2djBh" 

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=TEXTS["btn_call"][lang], callback_data="contact_action_phone"),
                InlineKeyboardButton(text=TEXTS["btn_location"][lang], callback_data="contact_action_location"),
            ],
            [
                InlineKeyboardButton(text=TEXTS["btn_telegram"][lang], url=f"https://t.me/{ADMIN_USERNAME}"),
                InlineKeyboardButton(text=TEXTS["btn_instagram"][lang], url=INSTAGRAM_LINK)
            ],
            [
                InlineKeyboardButton(text=TEXTS["btn_main_menu"][lang], callback_data="back_to_main")
            ]
        ]
    )