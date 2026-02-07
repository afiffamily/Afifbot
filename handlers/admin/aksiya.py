from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from loader import db, bot
from states.admin_states import PromoState, EditPromoState
from keyboards.inline.admin_inline import cancel_kb, get_confirm_kb

router = Router()

# =========================================================
# 1. AKSIYALAR RO'YXATI
# =========================================================
@router.message(F.text == "🔥 Aksiyalar")
async def promo_menu(message: types.Message):
    promos = await db.get_all_promotions()
    text = "<b>🔥 AKSIYALAR BOSHQARUVI</b>\n\nQuyidagi ro'yxatdan kerakli aksiyani tanlang yoki yangisini qo'shing:"
    
    kb = InlineKeyboardBuilder()
    for promo in promos:
        name = promo.get('name_uz', 'Nomsiz')
        price = "{:,.0f}".format(promo.get('price', 0)).replace(",", " ")
        btn_text = f"🏷 {name} ({price} so'm)"
        kb.button(text=btn_text, callback_data=f"view_promo_{promo['id']}")
    
    kb.button(text="➕ Yangi Aksiya Qo'shish", callback_data="add_promo")
    kb.adjust(1)
    
    await message.answer(text, reply_markup=kb.as_markup())


# =========================================================
# 2. YANGI AKSIYA QO'SHISH (FULL WIZARD)
# =========================================================
@router.callback_query(F.data == "add_promo")
async def start_add(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("📸 <b>1. Aksiya rasmini yuboring:</b>", reply_markup=cancel_kb)
    await state.set_state(PromoState.photo)

@router.message(PromoState.photo)
async def add_photo(message: types.Message, state: FSMContext):
    if not message.photo: return
    await state.update_data(photo=message.photo[-1].file_id)
    await message.answer("🇺🇿 <b>2. Nomi (O'zbekcha):</b>\nMasalan: <i>Super Set</i>", reply_markup=cancel_kb)
    await state.set_state(PromoState.name_uz)

@router.message(PromoState.name_uz)
async def add_name_uz(message: types.Message, state: FSMContext):
    await state.update_data(name_uz=message.text)
    await message.answer("🇷🇺 <b>3. Nomi (Ruscha):</b>", reply_markup=cancel_kb)
    await state.set_state(PromoState.name_ru)

@router.message(PromoState.name_ru)
async def add_name_ru(message: types.Message, state: FSMContext):
    await state.update_data(name_ru=message.text)
    await message.answer("🇺🇿 <b>4. Batafsil Matni (O'zbekcha):</b>", reply_markup=cancel_kb)
    await state.set_state(PromoState.caption_uz)

@router.message(PromoState.caption_uz)
async def add_cap_uz(message: types.Message, state: FSMContext):
    await state.update_data(cap_uz=message.text)
    await message.answer("🇷🇺 <b>5. Batafsil Matni (Ruscha):</b>", reply_markup=cancel_kb)
    await state.set_state(PromoState.caption_ru)

@router.message(PromoState.caption_ru)
async def add_cap_ru(message: types.Message, state: FSMContext):
    await state.update_data(cap_ru=message.text)
    await message.answer("💰 <b>6. Aksiya Narxi (so'mda):</b>\nFaqat raqam yozing (masalan: 120000)", reply_markup=cancel_kb)
    await state.set_state(PromoState.price)

@router.message(PromoState.price)
async def add_price(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam kiriting!")
        return
    
    price = int(message.text)
    await state.update_data(price=price)
    data = await state.get_data()
    
    caption = (
        f"🇺🇿 <b>{data['name_uz']}</b>\n{data['cap_uz']}\n\n"
        f"🇷🇺 <b>{data['name_ru']}</b>\n{data['cap_ru']}\n\n"
        f"💸 <b>Narxi:</b> {price} so'm"
    )
    
    await message.answer_photo(photo=data['photo'], caption=caption + "\n\n✅ <b>Tasdiqlaysizmi?</b>", reply_markup=get_confirm_kb("promo"))
    await state.set_state(PromoState.confirm)

@router.callback_query(PromoState.confirm, F.data == "confirm_promo")
async def save_new_promo(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await db.add_promotion(
        data['photo'], data['name_uz'], data['name_ru'],
        data['cap_uz'], data['cap_ru'], data['price']
    )
    await call.message.delete()
    await call.message.answer("✅ Aksiya muvaffaqiyatli qo'shildi!")
    await state.clear()
    await promo_menu(call.message)


# =========================================================
# 3. AKSIYANI KO'RISH VA BOSHQARISH
# =========================================================
@router.callback_query(F.data.startswith("view_promo_"))
async def view_promo(call: types.CallbackQuery):
    promo_id = int(call.data.split("_")[2])
    promo = await db.get_promotion_by_id(promo_id)
    
    if not promo:
        await call.answer("Topilmadi", show_alert=True)
        return

    price_fmt = "{:,.0f}".format(promo['price']).replace(",", " ")
    
    text = (
        f"🆔 <b>ID: {promo['id']}</b>\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"🇺🇿 <b>{promo['name_uz']}</b>\n{promo['caption_uz']}\n\n"
        f"🇷🇺 <b>{promo['name_ru']}</b>\n{promo['caption_ru']}\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"💸 <b>Narxi:</b> {price_fmt} so'm"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ TAHRIRLASH", callback_data=f"edit_menu_{promo_id}")],
        [InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"del_promo_{promo_id}")],
        [InlineKeyboardButton(text="🔙 Ortga", callback_data="back_to_promos")]
    ])
    
    await call.message.delete()
    await call.message.answer_photo(photo=promo['photo'], caption=text, reply_markup=kb)


# =========================================================
# 4. TAHRIRLASH (EDIT MENU)
# =========================================================
@router.callback_query(F.data.startswith("edit_menu_"))
async def show_edit_options(call: types.CallbackQuery, state: FSMContext):
    promo_id = int(call.data.split("_")[2])
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 Nomini (Uz)", callback_data=f"edt_name_uz_{promo_id}"), 
         InlineKeyboardButton(text="🇷🇺 Nomini (Ru)", callback_data=f"edt_name_ru_{promo_id}")],
        
        [InlineKeyboardButton(text="🇺🇿 Matnni (Uz)", callback_data=f"edt_caption_uz_{promo_id}"), 
         InlineKeyboardButton(text="🇷🇺 Matnni (Ru)", callback_data=f"edt_caption_ru_{promo_id}")],
         
        [InlineKeyboardButton(text="💸 Narxni", callback_data=f"edt_price_{promo_id}"),
         InlineKeyboardButton(text="📸 Rasmni", callback_data=f"edt_photo_{promo_id}")],
         
        [InlineKeyboardButton(text="🔙 Bekor qilish", callback_data=f"view_promo_{promo_id}")]
    ])
    
    await call.message.edit_caption(caption="📝 <b>Nimani o'zgartirmoqchisiz?</b>\nKerakli bo'limni tanlang:", reply_markup=kb)

@router.callback_query(F.data.startswith("edt_"))
async def ask_edit_value(call: types.CallbackQuery, state: FSMContext):
    parts = call.data.split("_")
    promo_id = int(parts[-1])
    
    field = "_".join(parts[1:-1]) 
    
    await state.update_data(edit_id=promo_id, edit_field=field)
    
    msg_map = {
        "name_uz": "🇺🇿 Yangi <b>Nomini (O'zbekcha)</b> yuboring:",
        "name_ru": "🇷🇺 Yangi <b>Nomini (Ruscha)</b> yuboring:",
        "caption_uz": "🇺🇿 Yangi <b>Matnni (O'zbekcha)</b> yuboring:",
        "caption_ru": "🇷🇺 Yangi <b>Matnni (Ruscha)</b> yuboring:",
        "price": "💸 Yangi <b>Narxni</b> raqamda yuboring:",
        "photo": "📸 Yangi <b>Rasmni</b> yuboring:"
    }
    
    await call.message.delete()
    await call.message.answer(msg_map.get(field, "Qiymatni kiriting:"), reply_markup=cancel_kb)
    await state.set_state(EditPromoState.input_new_value)

@router.message(EditPromoState.input_new_value)
async def save_edit_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    promo_id = data['edit_id']
    field = data['edit_field']
    
    new_value = None
    
    if field == "photo":
        if not message.photo:
            await message.answer("❌ Rasm yuboring!")
            return
        new_value = message.photo[-1].file_id
    elif field == "price":
        if not message.text.isdigit():
            await message.answer("❌ Faqat raqam yozing!")
            return
        new_value = int(message.text)
    else:
        new_value = message.text
        
    await db.update_promotion_field(promo_id, field, new_value)
    
    await message.answer("✅ <b>Muvaffaqiyatli o'zgartirildi!</b>")
    await state.clear()
    
    new_call = types.CallbackQuery(
        id='0', from_user=message.from_user, chat_instance='0',
        message=message, data=f"view_promo_{promo_id}"
    )
    await view_promo(new_call)


# =========================================================
# 5. O'CHIRISH (DELETE)
# =========================================================
@router.callback_query(F.data.startswith("del_promo_"))
async def ask_delete(call: types.CallbackQuery):
    promo_id = int(call.data.split("_")[2])
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Ha, o'chirilsin", callback_data=f"conf_del_{promo_id}")],
        [InlineKeyboardButton(text="🔙 Yo'q", callback_data=f"view_promo_{promo_id}")]
    ])
    await call.message.delete()
    await call.message.answer("⚠️ Rostdan ham o'chirasizmi?", reply_markup=kb)

@router.callback_query(F.data.startswith("conf_del_"))
async def confirm_delete(call: types.CallbackQuery):
    promo_id = int(call.data.split("_")[2])
    await db.delete_promotion(promo_id)
    await call.answer("O'chirildi!", show_alert=True)
    await call.message.delete()
    await promo_menu(call.message)

@router.callback_query(F.data == "back_to_promos")
async def back_main(call: types.CallbackQuery):
    await call.message.delete()
    await promo_menu(call.message)

@router.callback_query(F.data == "cancel_action")
async def cancel_op(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.delete()
    await promo_menu(call.message)