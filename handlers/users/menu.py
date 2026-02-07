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
# YORDAMCHI FUNKSIYALAR (LOGIKA)
# =========================================================
def is_working_hours(user_id):
    """Foydalanuvchi ish vaqtida ekanligini tekshiradi."""
    # Adminlar uchun har doim ochiq
    if str(user_id) in ADMINS or user_id in [int(x) for x in ADMINS]:
        return True

    # Toshkent vaqti
    tz = pytz.timezone('Asia/Tashkent')
    now = datetime.now(tz)
    
    # Soat 09:00 dan 21:00 gacha (21:00 kirmaydi)
    if 9 <= now.hour < 21:
        return True
    return False

async def send_closed_message(call: CallbackQuery, lang):
    """Do'kon yopiq bo'lsa xabar yuboradi."""
    msg_uz = (
        "😴 <b>Biz hozir dam olyapmiz.</b>\n\n"
        "⏰ <b>Ish vaqti:</b> 09:00 — 21:00\n"
        "☀️ <i>Ertalab soat 09:00 da yana xizmatingizdamiz!</i>"
    )
    msg_ru = (
        "😴 <b>Мы сейчас отдыхаем.</b>\n\n"
        "⏰ <b>Режим работы:</b> 09:00 — 21:00\n"
        "☀️ <i>Ждем вас завтра с 09:00 утра!</i>"
    )
    
    text = msg_uz if lang == 'uz' else msg_ru
    alert_text = "😴 Zzz... 09:00 dan 21:00 gacha ishlaymiz!"
    
    await call.answer(alert_text, show_alert=True)
    await call.message.delete()
    await call.message.answer(text, reply_markup=main_user_menu(lang))


# =========================================================
# KLAVIATURA YASOVCHILAR
# =========================================================
def products_markup(lang, products):
    kb = InlineKeyboardBuilder()
    
    for prod in products:
        name = prod['name_uz'] if lang == 'uz' else prod['name_ru']
        kb.button(text=name, callback_data=f"product:{prod['id']}")
    
    # Orqaga -> Bosh menyuga (Start dagi salomlashishga boradi)
    kb.button(text=TEXTS["back"][lang], callback_data="main_menu_start")
    
    kb.adjust(2)
    return kb.as_markup()

def product_detail_markup(lang, prod_id, quantity=1):
    kb = InlineKeyboardBuilder()
    
    # 1-qator: - 1 +
    kb.button(text="➖", callback_data=f"count:minus:{prod_id}:{quantity}")
    kb.button(text=f"{quantity} dona", callback_data="ignore")
    kb.button(text="➕", callback_data=f"count:plus:{prod_id}:{quantity}")
    
    # 2-qator: Savatga qo'shish
    add_text = TEXTS["btn_add_cart"][lang]
    kb.button(text=add_text, callback_data=f"cart:add:{prod_id}:{quantity}")
    
    # 3-qator: Orqaga -> Mahsulotlar ro'yxatiga
    kb.button(text=TEXTS["back"][lang], callback_data="back_to_products")
    
    kb.adjust(3, 1, 1)
    return kb.as_markup()


# =========================================================
# 1. MAHSULOTLAR RO'YXATINI KO'RSATISH
# =========================================================
@router.callback_query(F.data.in_({"menu_products", "menu_food", "back_to_products"}))
async def show_all_products_handler(call: CallbackQuery):
    user_id = call.from_user.id
    lang = await db.get_user_lang(user_id)
    
    # Ish vaqtini tekshirish
    if not is_working_hours(user_id):
        await send_closed_message(call, lang)
        return

    products = await db.get_all_products()
    
    if not products:
        await call.answer(TEXTS["menu_empty"][lang], show_alert=True)
        return

    # Eski xabarni o'chirish va yangisini yuborish
    await call.message.delete()
    await call.message.answer(
        text=TEXTS["select_product"][lang],
        reply_markup=products_markup(lang, products)
    )


# =========================================================
# 2. MAHSULOT TAFSILOTLARINI KO'RSATISH
# =========================================================
@router.callback_query(F.data.startswith("product:"))
async def show_product_detail(call: CallbackQuery):
    user_id = call.from_user.id
    lang = await db.get_user_lang(user_id)
    
    if not is_working_hours(user_id):
        await send_closed_message(call, lang)
        return

    try:
        product_id = int(call.data.split(":")[1])
    except (ValueError, IndexError):
        await call.answer("Xatolik: ID topilmadi", show_alert=True)
        return

    product = await db.get_product_by_id(product_id)
    
    if not product:
        await call.answer("Mahsulot topilmadi", show_alert=True)
        return

    # Ma'lumotlarni tayyorlash
    name = product['name_uz'] if lang == 'uz' else product['name_ru']
    desc = product['desc_uz'] if lang == 'uz' else product['desc_ru']
    price = "{:,.0f}".format(product['price']).replace(",", " ")
    currency = TEXTS["currency"][lang]
    
    caption = (
        f"🍰 <b>{name}</b>\n\n"
        f"📝 {desc}\n\n"
        f"💸 <b>{TEXTS['product_price'][lang]} {price} {currency}</b>"
    )

    await call.message.delete()
    
    markup = product_detail_markup(lang, product_id, quantity=1)

    if product.get('photo_id'):
        await call.message.answer_photo(
            photo=product['photo_id'],
            caption=caption,
            reply_markup=markup
        )
    else:
        await call.message.answer(
            text=caption,
            reply_markup=markup
        )


# =========================================================
# 3. MIQDORNI O'ZGARTIRISH (- / +)
# =========================================================
@router.callback_query(F.data.startswith("count:"))
async def change_quantity(call: CallbackQuery):
    try:
        # count:minus:id:qty
        parts = call.data.split(":")
        action = parts[1]
        prod_id = int(parts[2])
        qty = int(parts[3])
    except (ValueError, IndexError):
        return

    user_id = call.from_user.id
    lang = await db.get_user_lang(user_id)

    if action == "plus":
        qty += 1
    elif action == "minus":
        if qty > 1:
            qty -= 1
        else:
            await call.answer("Minimum 1")
            return

    # Faqat tugmani yangilash (xabar o'chib ketmasligi uchun)
    try:
        await call.message.edit_reply_markup(
            reply_markup=product_detail_markup(lang, prod_id, qty)
        )
    except Exception:
        # Agar kontent o'zgarmasa, Telegram xato berishi mumkin, shuning uchun pass
        pass


# =========================================================
# 4. SAVATGA QO'SHISH
# =========================================================
@router.callback_query(F.data.startswith("cart:add:"))
async def add_to_cart_handler(call: CallbackQuery):
    user_id = call.from_user.id
    lang = await db.get_user_lang(user_id)

    if not is_working_hours(user_id):
        await send_closed_message(call, lang)
        return

    try:
        data = call.data.split(":")
        prod_id = int(data[2])
        qty = int(data[3])
    except (ValueError, IndexError):
        await call.answer("Xatolik: Ma'lumot noto'g'ri", show_alert=True)
        return
    
    product = await db.get_product_by_id(prod_id)
    if not product:
        await call.answer("Xatolik: Mahsulot bazada yo'q", show_alert=True)
        return
    
    price = product['price'] 
    name = product['name_uz'] if lang == 'uz' else product['name_ru']
    
    # Bazaga qo'shish
    await db.add_to_cart(user_id, name, qty, price)
    
    # Tasdiqlash va menyuga qaytish
    await call.answer(TEXTS["added_to_cart"][lang], show_alert=True)
    await show_all_products_handler(call)