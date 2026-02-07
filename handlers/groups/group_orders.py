from aiogram import Router, F, types
from loader import db, bot
from locales.texts import TEXTS

router = Router()
async def get_admin_name(user_id, telegram_name):
    admin_data = await db.get_admin_info(user_id)
    if admin_data and admin_data.get('full_name'):
        return admin_data['full_name']
    else:
        return telegram_name

@router.callback_query(F.data.startswith("group_confirm_"))
async def admin_confirm_order(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[2])
    
    # 1. BAZADA STATUSNI YANGILASH 
    await db.update_order_status(user_id, 'confirmed')

    admin_name = await get_admin_name(call.from_user.id, call.from_user.full_name)
    original_text = call.message.caption if call.message.caption else call.message.text
    
    if "✅ Qabul qilindi" not in original_text:
        new_text = f"{original_text}\n\n✅ <b>Qabul qilindi:</b> {admin_name}"
        try:
            if call.message.caption:
                await call.message.edit_caption(caption=new_text, reply_markup=None)
            else:
                await call.message.edit_text(text=new_text, reply_markup=None)
        except Exception as e:
            print(f"Xato: {e}")

    try:
        lang = await db.get_user_lang(user_id)
        msg = "🚀 <b>Buyurtmangiz tasdiqlandi!</b>\n\nKuryer tez orada siz bilan bog'lanadi." if lang == 'uz' else "🚀 <b>Ваш заказ подтвержден!</b>"
        await bot.send_message(chat_id=user_id, text=msg)
    except:
        pass
    
    await call.answer(f"Tasdiqlandi: {admin_name}")

@router.callback_query(F.data.startswith("group_cancel_"))
async def admin_cancel_order(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[2])
    
    await db.update_order_status(user_id, 'canceled')
    
    admin_name = await get_admin_name(call.from_user.id, call.from_user.full_name)
    original_text = call.message.caption if call.message.caption else call.message.text
    
    if "❌ Bekor qilindi" not in original_text:
        new_text = f"{original_text}\n\n❌ <b>Bekor qilindi:</b> {admin_name}"
        try:
            if call.message.caption:
                await call.message.edit_caption(caption=new_text, reply_markup=None)
            else:
                await call.message.edit_text(text=new_text, reply_markup=None)
        except:
            pass
        
    try:
        lang = await db.get_user_lang(user_id)
        msg = "❌ <b>Buyurtmangiz bekor qilindi.</b>" if lang == 'uz' else "❌ <b>Ваш заказ отменен.</b>"
        await bot.send_message(chat_id=user_id, text=msg)
    except:
        pass
        
    await call.answer(f"Bekor qilindi: {admin_name}")