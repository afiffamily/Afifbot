from aiogram import Router, F, types
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime
import pytz

from loader import db
from data.config import ADMINS
from locales.texts import TEXTS
from keyboards.inline.buttons import main_user_menu

router = Router()

# =========================================================
# YORDAMCHI: ISH VAQTINI TEKSHIRISH (09:00 - 21:00)
# =========================================================
def is_working_hours(user_id):
    if str(user_id) in ADMINS or user_id in [int(x) for x in ADMINS]:
        return True
    tz = pytz.timezone('Asia/Tashkent')
    now = datetime.now(tz)
    hour = now.hour 
    if 9 <= hour < 21:
        return True
    return False

async def send_closed_message(call: CallbackQuery, lang):
    msg = (
        "😴 <b>Biz hozir dam olyapmiz.</b>\n\n"
        "⏰ <b>Ish vaqti:</b> 09:00 — 21:00\n"
        "☀️ <i>Ertalab soat 09:00 da yana xizmatingizdamiz!</i>"
    ) if lang == 'uz' else (
        "😴 <b>Мы сейчас отдыхаем.</b>\n\n"
        "⏰ <b>Режим работы:</b> 09:00 — 21:00\n"
        "☀️ <i>Ждем вас завтра с 09:00 утра!</i>"
    )
    await call.answer(show_alert=True, text="😴 Zzz... 09:00 dan 21:00 gacha ishlaymiz!")
    await call.message.delete()
    await call.message.answer(msg, reply_markup=main_user_menu(lang))


# =========================================================
# YORDAMCHI: AKSIYA KLAVIATURASI 
# =========================================================
def get_promo_kb(lang, promo_id, quantity):
    kb = InlineKeyboardBuilder()
    
    kb.button(text="➖", callback_data=f"promo_minus_{promo_id}_{quantity}")
    kb.button(text=f"{quantity} dona", callback_data="ignore")
    kb.button(text="➕", callback_data=f"promo_plus_{promo_id}_{quantity}")
    add_text = TEXTS["btn_add_cart"][lang]
    kb.button(text=add_text, callback_data=f"promo_add_{promo_id}_{quantity}")
    kb.button(text=TEXTS["back"][lang], callback_data="back_to_main")
    kb.adjust(3, 1, 1)
    return kb.as_markup()


# =========================================================
# 1. AKSIYA TUGMASI 
# =========================================================
@router.callback_query(F.data == "menu_promo") 
async def show_aksiya_handler(call: CallbackQuery):
    user_id = call.from_user.id
    user = await db.get_user_info(user_id)
    lang = user['language'] if user else 'uz'
    if not is_working_hours(user_id):
        await send_closed_message(call, lang)
        return
    promos = await db.get_all_promotions()
    if not promos:
        await call.answer(TEXTS["promo_empty"][lang], show_alert=True)
        return
    promo = promos[0]
    promo_id = promo['id']
    image = promo['photo']
    if lang == 'uz':
        name = promo.get('name_uz', 'Aksiya')
        caption = promo.get('caption_uz', '')
        currency = "so'm"
    else:
        name = promo.get('name_ru', 'Акция')
        caption = promo.get('caption_ru', '')
        currency = "сум"

    price = promo.get('price', 0)
    price_fmt = "{:,.0f}".format(price).replace(",", " ")

    full_caption = (
        f"🔥 <b>{name}</b>\n\n"
        f"{caption}\n\n"
        f"💸 <b>{price_fmt} {currency}</b>"
    )

    await call.message.delete()
    
    await call.message.answer_photo(
        photo=image,
        caption=full_caption,
        reply_markup=get_promo_kb(lang, promo_id=promo_id, quantity=1)
    )


# =========================================================
# 2. AKSIYA BOSHQARUVI (+ / - / SAVAT)
# =========================================================
@router.callback_query(F.data.startswith("promo_"))
async def manage_aksiya_actions(call: CallbackQuery):
    parts = call.data.split("_")
    action = parts[1]       
    promo_id = int(parts[2])
    quantity = int(parts[3])

    user_id = call.from_user.id
    user = await db.get_user_info(user_id)
    lang = user['language'] if user else 'uz'
    if not is_working_hours(user_id):
        await send_closed_message(call, lang)
        return
    if action == "plus":
        quantity += 1
        try:
            await call.message.edit_reply_markup(
                reply_markup=get_promo_kb(lang, promo_id, quantity)
            )
        except:
            pass
    
    elif action == "minus":
        if quantity > 1:
            quantity -= 1
            try:
                await call.message.edit_reply_markup(
                    reply_markup=get_promo_kb(lang, promo_id, quantity)
                )
            except:
                pass
        else:
            await call.answer("Minimum 1")
    elif action == "add":
        promo = await db.get_promotion_by_id(promo_id)
        if promo:
            if lang == 'uz':
                prod_name = f"🔥 {promo['name_uz']}"
            else:
                prod_name = f"🔥 {promo['name_ru']}"
            price = promo['price']
            await db.add_to_cart(
                user_id=user_id,
                product_name=prod_name,
                quantity=quantity,
                price=price  
            )
            await call.answer(TEXTS["added_to_cart"][lang], show_alert=True)
            await call.message.delete()
            await call.message.answer(
                text=TEXTS["welcome"][lang],
                reply_markup=main_user_menu(lang)
            )
        else:
            await call.answer("Xatolik: Aksiya topilmadi", show_alert=True)


# =========================================================
# 3. ORTGA QAYTISH
# =========================================================
@router.callback_query(F.data == "back_to_main")
async def back_to_main_menu_handler(call: CallbackQuery):
    user_id = call.from_user.id
    user = await db.get_user_info(user_id)
    lang = user['language'] if user else 'uz'
    
    await call.message.delete()
    await call.message.answer(TEXTS["welcome"][lang], reply_markup=main_user_menu(lang))