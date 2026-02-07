import asyncio
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import db, bot
from states.admin_states import BroadcastState, DirectMessageState
from keyboards.inline.admin_inline import marketing_kb, get_confirm_kb, cancel_kb

router = Router()

# =========================================================
# 1. MARKETING MENYUSI
# =========================================================
@router.message(F.text == "📢 Smart Marketing")
async def marketing_menu(message: types.Message):
    users_uz = await db.get_users_by_lang('uz')
    users_ru = await db.get_users_by_lang('ru')
    
    text = (
        "<b>📢 SMART MARKETING MARKAZI</b>\n\n"
        f"👥 <b>Jami auditoriya:</b> {len(users_uz) + len(users_ru)} ta\n"
        f"├ 🇺🇿 O'zbek tilida: <b>{len(users_uz)} ta</b>\n"
        f"└ 🇷🇺 Rus tilida: <b>{len(users_ru)} ta</b>\n\n"
        "Qaysi usulda xabar yubormoqchisiz?"
    )
    await message.answer(text, reply_markup=marketing_kb)

@router.callback_query(F.data == "close_panel")
async def close_panel(call: types.CallbackQuery):
    await call.message.delete()


# =========================================================
# 2. BROADCAST (OMMAVIY XABAR - DUAL LANGUAGE)
# =========================================================

# --- 1. O'zbekcha post ---
@router.callback_query(F.data == "mkt_broadcast")
async def start_broadcast(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "🇺🇿 <b>1-BOSQICH: O'zbek auditoriyasi uchun post.</b>\n\n"
        "Rasm (caption bilan) yoki shunchaki Matn yuboring:", 
        reply_markup=cancel_kb
    )
    await state.set_state(BroadcastState.post_uz)

@router.message(BroadcastState.post_uz)
async def get_post_uz(message: types.Message, state: FSMContext):
    if message.photo:
        await state.update_data(
            uz_type='photo', 
            uz_file=message.photo[-1].file_id, 
            uz_caption=message.caption or ""
        )
    else:
        await state.update_data(
            uz_type='text', 
            uz_text=message.text
        )
    
    await message.answer(
        "🇷🇺 <b>2-BOSQICH: Rus auditoriyasi uchun post.</b>\n\n"
        "Endi xuddi shu mazmundagi postni Rus tilida yuboring:", 
        reply_markup=cancel_kb
    )
    await state.set_state(BroadcastState.post_ru)

# --- 2. Ruscha post ---
@router.message(BroadcastState.post_ru)
async def get_post_ru(message: types.Message, state: FSMContext):
    if message.photo:
        await state.update_data(
            ru_type='photo', 
            ru_file=message.photo[-1].file_id, 
            ru_caption=message.caption or ""
        )
    else:
        await state.update_data(
            ru_type='text', 
            ru_text=message.text
        )
    
    
    users_uz = await db.get_users_by_lang('uz')
    users_ru = await db.get_users_by_lang('ru')
    total = len(users_uz) + len(users_ru)
    
    confirm_text = (
        "<b>✅ POSTLAR TAYYOR!</b>\n\n"
        f"📨 <b>Yuboriladi:</b> {total} ta mijozga\n"
        f"🇺🇿 O'zbekcha: {len(users_uz)} ta\n"
        f"🇷🇺 Ruscha: {len(users_ru)} ta\n\n"
        "🚀 <b>Reklamani boshlaymi?</b>"
    )
    
    await message.answer(confirm_text, reply_markup=get_confirm_kb("broadcast"))
    await state.set_state(BroadcastState.confirm)

@router.callback_query(BroadcastState.confirm, F.data == "confirm_broadcast")
async def send_broadcast(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.edit_text("🚀 <b>Reklama yuborish boshlandi...</b>\n\n<i>Iltimos, kuting. Jarayon tugagach hisobot beraman.</i>")
    
    users_uz = await db.get_users_by_lang('uz')
    users_ru = await db.get_users_by_lang('ru')
    
    success = 0
    blocked = 0
    
    # 1. O'ZBEK AUDITORIYASI
    for user_id in users_uz:
        try:
            if data['uz_type'] == 'photo':
                await bot.send_photo(chat_id=user_id, photo=data['uz_file'], caption=data['uz_caption'])
            else:
                await bot.send_message(chat_id=user_id, text=data['uz_text'])
            success += 1
            await asyncio.sleep(0.05) # Spamdan himoya
        except:
            blocked += 1

    # 2. RUS AUDITORIYASI
    for user_id in users_ru:
        try:
            if data['ru_type'] == 'photo':
                await bot.send_photo(chat_id=user_id, photo=data['ru_file'], caption=data['ru_caption'])
            else:
                await bot.send_message(chat_id=user_id, text=data['ru_text'])
            success += 1
            await asyncio.sleep(0.05)
        except:
            blocked += 1

    report = (
        "<b>🏁 REKLAMA YAKUNLANDI</b>\n\n"
        f"✅ Yetkazildi: <b>{success} ta</b>\n"
        f"🚫 Bloklangan/O'chgan: <b>{blocked} ta</b>"
    )
    await call.message.answer(report)
    await state.clear()


# =========================================================
# 3. DIRECT MESSAGE (SHAXSIY - TARGET)
# =========================================================
@router.callback_query(F.data == "mkt_direct")
async def start_direct(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "🎯 <b>SHAXSIY XABAR (TARGET)</b>\n\n"
        "Mijozning <b>ID raqamini</b> yozing yoki uning xabarini menga <b>Forward</b> qiling:",
        reply_markup=cancel_kb
    )
    await state.set_state(DirectMessageState.user_id)

@router.message(DirectMessageState.user_id)
async def check_user_direct(message: types.Message, state: FSMContext):
    target_id = None
    if message.forward_from:
        target_id = message.forward_from.id
    elif message.text.isdigit():
        target_id = int(message.text)
    
    if not target_id:
        await message.answer("❌ Iltimos, to'g'ri ID raqam yuboring.")
        return

    user_info = await db.get_user_info(target_id)
    if not user_info:
        await message.answer("❌ Bunday mijoz bazada topilmadi. Qayta urinib ko'ring.")
        return

    lang = user_info.get('language', 'uz')
    
    if lang == 'ru':
        lang_emoji = "🇷🇺"
        advice = "⚠️ <b>DIQQAT:</b> Mijoz rus tilida gaplashadi.\nIltimos, xabarni <b>RUSCHA</b> yozing!"
    else:
        lang_emoji = "🇺🇿"
        advice = "ℹ️ <b>ESLATMA:</b> Mijoz o'zbek tilida gaplashadi.\nXabarni <b>O'ZBEKCHA</b> yozing."

    reg_date = user_info['reg_date'].strftime('%d.%m.%Y') if user_info.get('reg_date') else "Noma'lum"
    phone = user_info.get('phone_number') or "Kiritilmagan"
    username = f"@{user_info['username']}" if user_info.get('username') else "Yo'q"
    full_name = user_info.get('full_name', "Noma'lum")
    orders_count = user_info.get('order_count', 0)

    profile_text = (
        f"👤 <b>MIJOZ PROFILI (DOSYE):</b>\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"📛 <b>Ism:</b> {full_name}\n"
        f"🆔 <b>ID:</b> <code>{user_info['user_id']}</code>\n"
        f"📱 <b>Tel:</b> {phone}\n"
        f"🔗 <b>Link:</b> {username}\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"🗣 <b>Til:</b> {lang_emoji} ({lang.upper()})\n"
        f"📅 <b>Ro'yxatdan o'tgan:</b> {reg_date}\n"
        f"🛍 <b>Buyurtmalar:</b> {orders_count} ta\n\n"
        f"{advice}\n\n"
        "✍️ <b>Xabarni yozing (Matn, Rasm, Video yoki Ovozli):</b>"
    )
    
    await state.update_data(target_id=target_id)
    await message.answer(profile_text, reply_markup=cancel_kb)
    await state.set_state(DirectMessageState.message_content)

@router.message(DirectMessageState.message_content)
async def confirm_direct_msg(message: types.Message, state: FSMContext):
    await state.update_data(msg_id=message.message_id, chat_id=message.chat.id)
    await message.copy_to(chat_id=message.chat.id)
    await message.answer(
        "Xabar mijozga shu ko'rinishda boradi.\n<b>Yuboraymi?</b>", 
        reply_markup=get_confirm_kb("direct")
    )
    await state.set_state(DirectMessageState.confirm)

@router.callback_query(DirectMessageState.confirm, F.data == "confirm_direct")
async def send_direct_msg(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    try:
        await bot.copy_message(
            chat_id=data['target_id'], 
            from_chat_id=data['chat_id'], 
            message_id=data['msg_id']
        )
        await call.message.edit_text("✅ <b>Xabar muvaffaqiyatli yetkazildi!</b>")
    except Exception as e:
        await call.message.edit_text(f"❌ <b>Xatolik!</b> Xabar yetib bormadi.\nMijoz botni bloklagan bo'lishi mumkin.\n\n(Error: {e})")
    
    await state.clear()

@router.callback_query(F.data == "cancel_action")
async def cancel_marketing(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.delete()
    await call.message.answer("❌ Bekor qilindi.")