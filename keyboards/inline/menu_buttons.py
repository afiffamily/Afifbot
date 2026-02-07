from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from locales.texts import TEXTS

def products_markup(lang, products):
    keyboard = []
    row = []
    for product in products:
        prod_name = product['name_uz'] if lang == 'uz' else product['name_ru']
        prod_id = product['id']
        
        row.append(InlineKeyboardButton(text=prod_name, callback_data=f"product:{prod_id}"))
        
        if len(row) == 2:
            keyboard.append(row)
            row = []
            
    if row:
        keyboard.append(row)
        
    keyboard.append([InlineKeyboardButton(text=TEXTS["btn_main_menu"][lang], callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def product_detail_markup(lang, product_id, quantity=1):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➖", callback_data=f"count:minus:{product_id}:{quantity}"),
                InlineKeyboardButton(text=f"{quantity}", callback_data="ignore"),
                InlineKeyboardButton(text="➕", callback_data=f"count:plus:{product_id}:{quantity}"),
            ],
            [
                InlineKeyboardButton(text=TEXTS["btn_add_to_cart"][lang], callback_data=f"cart:add:{product_id}:{quantity}")
            ],
            [
                InlineKeyboardButton(text=TEXTS["back"][lang], callback_data="back_to_products")
            ]
        ]
    )