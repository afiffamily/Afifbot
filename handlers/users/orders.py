from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from loader import db
from locales.texts import TEXTS
from keyboards.inline.buttons import main_user_menu

router = Router()

# =========================================================
# 📦 BUYURTMALAR TARIXINI KO'RSATISH
# =========================================================
@router.callback_query(F.data == "menu_orders")
async def my_orders_history(call: CallbackQuery):
    user_id = call.from_user.id
    lang = await db.get_user_lang(user_id)
    
    orders = await db.get_user_last_orders(user_id)
    
    if not orders:
        text = "🤷‍♂️ Sizda hali buyurtmalar tarixi mavjud emas." if lang == 'uz' else "🤷‍♂️ У вас пока нет истории заказов."
        await call.answer(text, show_alert=True)
        return

    await call.message.delete()
    
    for order in orders:
        order_id = order['id']
        status_raw = order['status']
        total_amount = "{:,.0f}".format(order['total_amount']).replace(",", " ")
        created_at = order['created_at'].strftime("%d.%m.%Y | %H:%M")
        
        address = order.get('address_text')
        if not address:
             address = "Belgilanmagan" if lang == 'uz' else "Не указан"
             
        payment = order.get('payment_type') or "Noma'lum"
        
        if status_raw == 'confirmed':
            status_emoji = "🟢"
            status_text = "Tasdiqlandi" if lang == 'uz' else "Подтвержден"
        elif status_raw == 'canceled':
            status_emoji = "🔴"
            status_text = "Bekor qilindi" if lang == 'uz' else "Отменен"
        else:
            status_emoji = "🟡"
            status_text = "Yangi (Kutilmoqda)" if lang == 'uz' else "Новый (Ожидание)"
            
        items = await db.get_order_items(order_id)
        
        items_text = ""
        for item in items:
            p_price = "{:,.0f}".format(item['price']).replace(",", " ")
            line_total = item['price'] * item['quantity']
            p_total = "{:,.0f}".format(line_total).replace(",", " ")
            
            items_text += (
                f"▫️ <b>{item['product_name']}</b>\n"
                f"   └ <code>{item['quantity']}</code> x {p_price} = <b>{p_total}</b>\n"
            )

        msg = (
            f"🧾 <b>Buyurtma tarixi: #{order_id}</b>\n"
            f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            f"📅 <b>Vaqt:</b> {created_at}\n"
            f"🎨 <b>Holati:</b> {status_emoji} {status_text}\n"
            f"📍 <b>Manzil:</b> {address}\n\n"
            f"🛒 <b>Mahsulotlar:</b>\n"
            f"{items_text}"
            f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            f"💳 <b>To'lov:</b> {payment}\n"
            f"💸 <b>JAMI:</b> {total_amount} so'm"
        )
        
        close_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=TEXTS["btn_close"][lang], callback_data="delete_order_msg")]
        ])
        
        await call.message.answer(msg, reply_markup=close_kb)

    await call.message.answer(TEXTS["select_category"][lang], reply_markup=main_user_menu(lang))


# =========================================================
# ❌ XABARNI O'CHIRISH (YOPISH)
# =========================================================
@router.callback_query(F.data == "delete_order_msg")
async def delete_msg(call: CallbackQuery):
    try:
        await call.message.delete()
    except:
        pass