from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import pytz

from loader import db, bot
from data.config import ADMIN_GROUP_ID, ADMINS
from locales.texts import TEXTS
from states.user_states import CheckoutState
from utils.location import get_address_from_coords
from keyboards.inline.buttons import main_user_menu
from keyboards.inline.cart_buttons import (
    cart_markup, location_markup, 
    phone_markup, confirm_order_markup,
    saved_address_markup
)

router = Router()

def is_working_hours(user_id):
    if str(user_id) in ADMINS or user_id in [int(x) for x in ADMINS]:
        return True

    tz = pytz.timezone('Asia/Tashkent')
    now = datetime.now(tz)
    hour = now.hour

    if 9 <= hour < 21:
        return True
    return False

async def send_closed_message(call: types.CallbackQuery, lang):
    msg = (
        "😴 <b>Biz hozir dam olyapmiz.</b>\n\n"
        "⏰ <b>Ish vaqti:</b> 09:00 — 21:00\n"
        "☀️ <i>Ertalab soat 09:00 da yana xizmatingizdamiz!</i>"
    ) if lang == 'uz' else (
        "😴 <b>Мы сейчас отдыхаем.</b>\n\n"
        "⏰ <b>Режим работы:</b> 09:00 — 21:00\n"
        "☀️ <i>Ждем вас завтра с 09:00 утра!</i>"
    )
    await call.answer(show_alert=True, text="😴 09:00 dan 21:00 gacha ishlaymiz!")
    await call.message.delete()
    await call.message.answer(msg, reply_markup=main_user_menu(lang))


@router.callback_query(F.data == "menu_cart")
@router.callback_query(F.data == "back_to_cart")
async def show_cart(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = call.from_user.id
    lang = await db.get_user_lang(user_id)
    if not is_working_hours(user_id):
        await send_closed_message(call, lang)
        return
    cart_items = await db.get_user_cart(user_id)
    if not cart_items:
        await call.answer(TEXTS["cart_empty"][lang], show_alert=True)
        return
        
    text_items = ""
    total_sum = 0
    for i, item in enumerate(cart_items, 1):
        total_price = item['total_price']
        total_sum += total_price
        price_fmt = "{:,.0f}".format(total_price).replace(",", " ")
        text_items += f"{i}. <b>{item['product_name']}</b>\n   {item['quantity']} x {item['price']} = {price_fmt}\n"
    final_total = "{:,.0f}".format(total_sum).replace(",", " ")
    
    await call.message.delete()
    await call.message.answer(
        TEXTS["cart_title"][lang].format(items=text_items, total=final_total),
        reply_markup=cart_markup(lang)
    )

@router.callback_query(F.data == "cart_clear")
async def clear_cart_handler(call: types.CallbackQuery):
    user_id = call.from_user.id
    lang = await db.get_user_lang(user_id)
    await db.clear_cart(user_id)
    await call.answer(TEXTS["cart_empty"][lang], show_alert=True)
    await call.message.delete()
    await call.message.answer(TEXTS["welcome"][lang], reply_markup=main_user_menu(lang))


@router.callback_query(F.data == "order_start")
async def start_checkout(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    lang = await db.get_user_lang(user_id)
    if not is_working_hours(user_id):
        await send_closed_message(call, lang)
        return
    user = await db.get_user_info(user_id)
    
    if user and user.get('full_name'):
        real_name = user['full_name']
    else:
        real_name = call.from_user.full_name

    await state.update_data(full_name=real_name)
    await state.update_data(delivery="dlv_delivery")

    saved_addr = await db.get_user_last_address(user_id)
    
    if saved_addr:
        await call.message.delete()
        await call.message.answer(
            TEXTS["ask_saved_address"][lang].format(address=saved_addr),
            reply_markup=saved_address_markup(lang, saved_addr)
        )
        await state.update_data(temp_saved_addr=saved_addr)
        await state.set_state(CheckoutState.choose_address)
    else:
        await ask_location(call, state, lang)

async def ask_location(call, state, lang):
    await call.message.delete()
    await call.message.answer(TEXTS["ask_location"][lang], reply_markup=location_markup(lang))
    await state.set_state(CheckoutState.location)

@router.callback_query(CheckoutState.choose_address, F.data == "use_saved_addr")
async def use_saved_address(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    lang = await db.get_user_lang(user_id)
    data = await state.get_data()
    saved_addr = data.get("temp_saved_addr")
    
    await state.update_data(extra_info=saved_addr, location=None)
    
    last_loc = await db.get_user_last_location(user_id)
    if last_loc and last_loc['latitude']:
        await state.update_data(location=f"{last_loc['latitude']},{last_loc['longitude']}")

    user = await db.get_user_info(user_id)
    if user and user.get('phone_number'):
        await state.update_data(phone=user['phone_number'])
        await state.update_data(payment="Karta (Click/Payme)")
        await finalize_order_preview(call, state, lang)
    else:
        await call.message.delete()
        await call.message.answer(TEXTS["ask_phone"][lang], reply_markup=phone_markup(lang))
        await state.set_state(CheckoutState.phone)

@router.callback_query(CheckoutState.choose_address, F.data == "use_new_addr")
async def use_new_address(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    lang = await db.get_user_lang(user_id)
    await ask_location(call, state, lang)


@router.message(CheckoutState.location, F.location)
async def get_location(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await db.get_user_lang(user_id)
    
    lat = message.location.latitude
    lon = message.location.longitude
    await db.update_user_location(user_id, lat, lon)
    await state.update_data(location=f"{lat},{lon}")
    wait_msg = await message.answer("⏳ <i>Lokatsiya aniqlanmoqda...</i>", reply_markup=ReplyKeyboardRemove())
    address_name = await get_address_from_coords(lat, lon)
    
    await wait_msg.delete()
    
    if address_name:
        await state.update_data(detected_address=address_name)
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=TEXTS["btn_yes_confirm"][lang], callback_data="loc_confirm")],
            [InlineKeyboardButton(text=TEXTS["btn_no_retry"][lang], callback_data="loc_retry")]
        ])
        
        await message.answer(
            TEXTS["confirm_geo_address"][lang].format(address=address_name),
            reply_markup=kb
        )
        await state.set_state(CheckoutState.confirm_location)
    else:
        await message.answer(TEXTS["geo_not_found"][lang])
        await message.answer(TEXTS["ask_extra_info"][lang])
        await state.set_state(CheckoutState.extra_info)


@router.callback_query(CheckoutState.confirm_location, F.data == "loc_confirm")
async def location_confirmed(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    lang = await db.get_user_lang(user_id)
    
    data = await state.get_data()
    detected_addr = data.get("detected_address", "")
    
    await call.message.delete()
    await call.message.answer(
        f"✅ Manzil qabul qilindi: <b>{detected_addr}</b>\n\n" + TEXTS["ask_extra_info"][lang]
    )
    await state.set_state(CheckoutState.extra_info)

@router.callback_query(CheckoutState.confirm_location, F.data == "loc_retry")
async def location_retry(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    lang = await db.get_user_lang(user_id)
    
    await call.message.delete()
    await call.message.answer(TEXTS["ask_location"][lang], reply_markup=location_markup(lang))
    await state.set_state(CheckoutState.location)


@router.message(CheckoutState.extra_info)
async def get_extra_info(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await db.get_user_lang(user_id)
    
    data = await state.get_data()
    base_address = data.get("detected_address", "")
    
    if base_address:
        full_address_text = f"{base_address}\n(Qo'shimcha: {message.text})"
    else:
        full_address_text = message.text
        
    await state.update_data(extra_info=full_address_text)
    
    await message.answer(TEXTS["ask_phone"][lang], reply_markup=phone_markup(lang))
    await state.set_state(CheckoutState.phone)


@router.message(CheckoutState.phone)
async def get_phone(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await db.get_user_lang(user_id)
    phone = message.contact.phone_number if message.contact else message.text
    await db.update_user_phone(user_id, phone)
    await state.update_data(phone=phone)
    await message.answer("...", reply_markup=ReplyKeyboardRemove())
    
    await state.update_data(payment="Karta (Click/Payme)")
    await finalize_order_preview(message, state, lang)

async def finalize_order_preview(event_obj, state: FSMContext, lang):
    if isinstance(event_obj, types.CallbackQuery):
        message = event_obj.message
        user_id = event_obj.from_user.id
    else:
        message = event_obj
        user_id = event_obj.from_user.id

    data = await state.get_data()
    cart_items = await db.get_user_cart(user_id)
    total_sum = sum([item['total_price'] for item in cart_items])
    total_fmt = "{:,.0f}".format(total_sum).replace(",", " ")
    
    client_name = data.get('full_name', "Noma'lum")
    client_addr = data.get('extra_info', '-')
    pay_type = data.get('payment', "Karta (Click/Payme)")
    
    info = (
        f"👤 <b>Mijoz:</b> {client_name}\n"
        f"📞 <b>Tel:</b> {data['phone']}\n"
        f"🚖 <b>Xizmat:</b> Yetkazib berish\n"
        f"🏢 <b>Manzil:</b> {client_addr}\n"
        f"💳 <b>To'lov:</b> {pay_type}\n"
        f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"💰 <b>JAMI:</b> {total_fmt} so'm"
    )
    
    if isinstance(event_obj, types.CallbackQuery):
        await message.delete()
        await message.answer(TEXTS["confirm_order"][lang].format(info=info), reply_markup=confirm_order_markup(lang))
    else:
        await message.answer(TEXTS["confirm_order"][lang].format(info=info), reply_markup=confirm_order_markup(lang))
        
    await state.set_state(CheckoutState.confirm)


@router.callback_query(F.data == "order_confirm")
async def send_order_to_group(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    lang = await db.get_user_lang(user_id)
    data = await state.get_data()
    
    if not data or not data.get('payment'):
        await call.answer("⚠️ Sessiya eskirdi. Qaytadan buyurtma bering.", show_alert=True)
        await show_cart(call, state)
        return
    
    await call.message.delete()
    await call.message.answer(TEXTS["order_sent"][lang])
    await call.message.answer(TEXTS["welcome"][lang], reply_markup=main_user_menu(lang))
    
    cart_items = await db.get_user_cart(user_id)
    if not cart_items:
        await state.clear()
        return

    total_sum = sum([item['total_price'] for item in cart_items])
    total_formatted = "{:,.0f}".format(total_sum).replace(",", " ")

    if data.get('extra_info'):
        await db.update_user_last_address(user_id, data['extra_info'])

    order_id = await db.create_order(
        user_id, 
        total_sum, 
        address_text=data.get('extra_info'), 
        payment_type=data.get('payment')
    )

    for item in cart_items:
        await db.add_order_item(
            order_id=order_id,
            product_name=item['product_name'],
            quantity=item['quantity'],
            price=item['price']
        )

    await db.clear_cart(user_id)
    
    full_name_val = data.get('full_name', "Noma'lum")
    username_val = f"@{call.from_user.username}" if call.from_user.username else "Yo'q"
    extra_info_val = data.get('extra_info', '-')
    
    order_text = (
        f"🆕 <b>YANGI BUYURTMA!</b>\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"👤 <b>Mijoz:</b> <a href='tg://user?id={user_id}'>{full_name_val}</a>\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
        f"🏷 <b>Username:</b> {username_val}\n"
        f"📞 <b>Tel:</b> {data['phone']}\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"🚖 <b>Tur:</b> Yetkazib berish\n"
        f"🏢 <b>Manzil:</b> {extra_info_val}\n"
        f"💳 <b>To'lov:</b> {data['payment']}\n"
        f"💰 <b>Jami Summa:</b> {total_formatted} so'm\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        "🛒 <b>Savatcha tarkibi:</b>\n"
    )
    for item in cart_items:
        order_text += f"- {item['product_name']} ({item['quantity']}x)\n"

    group_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"group_confirm_{user_id}"),
         InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"group_cancel_{user_id}")]
    ])
    
    try:
        if ADMIN_GROUP_ID:
            if data.get('location'):
                try:
                    lat, lon = data['location'].split(",")
                    await bot.send_location(chat_id=ADMIN_GROUP_ID, latitude=float(lat), longitude=float(lon))
                except: pass
            await bot.send_message(chat_id=ADMIN_GROUP_ID, text=order_text, reply_markup=group_kb)
    except Exception as e:
        print(f"Error sending to group: {e}")
            
    await state.clear()

@router.callback_query(F.data == "order_cancel")
async def cancel_order(call: types.CallbackQuery, state: FSMContext):
    lang = await db.get_user_lang(call.from_user.id)
    await state.clear()
    await db.clear_cart(call.from_user.id)
    await call.message.delete()
    await call.message.answer("❌ Buyurtma bekor qilindi.", reply_markup=main_user_menu(lang))