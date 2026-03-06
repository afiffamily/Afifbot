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
# YORDAMCHI FUNKSIYALAR
# =========================================================
def is_working_hours(user_id):
    if str(user_id) in ADMINS or user_id in [int(x) for x in ADMINS]:
        return True
    tz = pytz.timezone('Asia/Tashkent')
    now = datetime.now(tz)
    if 9 <= now.hour < 21:
        return True
    return False

async def send_closed_message(call: CallbackQuery, lang):
    msg_uz = "😴 <b>Biz hozir dam olyapmiz.</b>\n\n⏰ <b>Ish vaqti:</b> 09:00 — 21:00\n☀️ <i>Ertalab soat 09:00 da yana xizmatingizdamiz!</i>"
    msg_ru = "😴 <b>Мы сейчас отдыхаем.</b>\n\n⏰ <b>Режим работы:</b> 09:00 — 21:00\n☀️ <i>Ждем вас завтра с 09:00 утра!</i>"
    text = msg_uz if lang == 'uz' else msg_ru
    await call.answer("😴 Zzz... 09:00 dan 21:00 gacha ishlaymiz!", show_alert=True)
    await call.message.delete()
    await call.message.answer(text, reply_markup=main_user_menu(lang))


# =========================================================
# KLAVIATURA YASOVCHILAR
# =========================================================
def products_markup(lang, products, has_cart_items=False):
    kb = InlineKeyboardBuilder()
    
    for prod in products:
        name = prod['name_uz'] if lang == 'uz' else prod['name_ru']
        kb.button(text=name, callback_data=f"product:{prod['id']}")
    
    kb.adjust(2)

    if has_cart_items:
        kb.row(InlineKeyboardButton(text=TEXTS["btn_cart"][lang], callback_data="menu_cart"))

    kb.row(InlineKeyboardButton(text=TEXTS["back"][lang], callback_data="main_menu_start"))
    return kb.as_markup()

def product_detail_markup(lang, prod_id, product, cart_items):
    kb = InlineKeyboardBuilder()
    
    weights_raw = product.get('weights')
    weight_dict = {}
    
    if weights_raw:
        items = weights_raw.split(",")
        for item in items:
            if "=" in item:
                parts = item.split("=")
                if len(parts) >= 2:
                    w, p = parts[0], parts[1]
                    weight_dict[w.strip()] = int(p.strip())
                
    base_name = product['name_uz'] if lang == 'uz' else product['name_ru']
    
    cart_dict = {}
    for item in cart_items:
        cart_dict[item['product_name']] = item['quantity']
        
    for w, w_price in weight_dict.items():
        if w == "1":
            p_name = base_name
            w_label = "Dona" if lang == 'uz' else "Шт"
        else:
            p_name = f"{base_name} ({w})"
            w_label = f"{w}"
            
        qty = cart_dict.get(p_name, 0)
        
        if qty == 0:
            price_fmt = "{:,.0f}".format(w_price).replace(",", " ")
            btn_text = f"➕ {w_label} - {price_fmt} so'm"
            kb.row(InlineKeyboardButton(text=btn_text, callback_data=f"cart:add:{prod_id}:{w}"))
        else:
            kb.row(
                InlineKeyboardButton(text="➖", callback_data=f"cart:minus:{prod_id}:{w}"),
                InlineKeyboardButton(text=f"{qty} x {w_label}", callback_data="ignore"),
                InlineKeyboardButton(text="➕", callback_data=f"cart:add:{prod_id}:{w}")
            )
            
    total_sum = sum([item['total_price'] for item in cart_items])
    if total_sum > 0:
        cart_btn_text = TEXTS["btn_cart"][lang] 
        kb.row(InlineKeyboardButton(text=cart_btn_text, callback_data="menu_cart"))
        
    kb.row(InlineKeyboardButton(text=TEXTS["back"][lang], callback_data="back_to_products"))
    return kb.as_markup()


# =========================================================
# 1. MAHSULOTLAR RO'YXATINI KO'RSATISH
# =========================================================
@router.callback_query(F.data.in_({"menu_products", "menu_food", "back_to_products"}))
async def show_all_products_handler(call: CallbackQuery):
    user_id = call.from_user.id
    lang = await db.get_user_lang(user_id)
    
    if not is_working_hours(user_id):
        await send_closed_message(call, lang)
        return

    products = await db.get_all_products()
    if not products:
        await call.answer(TEXTS["menu_empty"][lang], show_alert=True)
        return

    cart_items = await db.get_user_cart(user_id)
    has_items = True if cart_items else False

    await call.message.delete()
    await call.message.answer(
        text=TEXTS["select_product"][lang],
        reply_markup=products_markup(lang, products, has_cart_items=has_items)
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

    name = product['name_uz'] if lang == 'uz' else product['name_ru']
    desc = product['desc_uz'] if lang == 'uz' else product['desc_ru']
    
    select_text = (
        "👇 <i>Kerakli miqdor va o'lchovni tanlang:</i>" if lang == 'uz' 
        else "👇 <i>Выберите нужное количество и размер:</i>"
    )
    
    caption = (
        f"🍰 <b>{name}</b>\n\n"
        f"📝 {desc}\n\n"
        f"{select_text}"
    )

    await call.message.delete()
    
    cart_items = await db.get_user_cart(user_id)
    markup = product_detail_markup(lang, product_id, product, cart_items)

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
# 3. SAVATNI DINAMIK BOSHQARISH (+ VA -)
# =========================================================
@router.callback_query(F.data.startswith("cart:"))
async def handle_cart_actions(call: CallbackQuery):
    parts = call.data.split(":")
    action = parts[1] 
    prod_id = int(parts[2])
    weight = parts[3]
    
    user_id = call.from_user.id
    lang = await db.get_user_lang(user_id)
    
    product = await db.get_product_by_id(prod_id)
    if not product:
        await call.answer("Xatolik: Mahsulot topilmadi", show_alert=True)
        return
        
    base_name = product['name_uz'] if lang == 'uz' else product['name_ru']
    
    weights_raw = product.get('weights', '')
    w_price = 0
    for item in weights_raw.split(","):
        if "=" in item:
            sub_parts = item.split("=")
            if len(sub_parts) >= 2 and sub_parts[0].strip() == weight:
                w_price = int(sub_parts[1].strip())
                break
                
    if weight == "1":
        p_name = base_name
    else:
        p_name = f"{base_name} ({weight})"
        
    cart_items = await db.get_user_cart(user_id)
    target_item = next((item for item in cart_items if item['product_name'] == p_name), None)
    
    if action == "add":
        if target_item:
            new_qty = target_item['quantity'] + 1
            await db.execute("UPDATE cart SET quantity = $1 WHERE id = $2", new_qty, target_item['id'])
        else:
            await db.add_to_cart(user_id, p_name, 1, w_price)
            
    elif action == "minus":
        if target_item:
            new_qty = target_item['quantity'] - 1
            if new_qty > 0:
                await db.execute("UPDATE cart SET quantity = $1 WHERE id = $2", new_qty, target_item['id'])
            else:
                await db.delete_cart_item(target_item['id'])
                
    updated_cart = await db.get_user_cart(user_id)
    markup = product_detail_markup(lang, prod_id, product, updated_cart)
    
    try:
        await call.message.edit_reply_markup(reply_markup=markup)
    except Exception:
        pass
