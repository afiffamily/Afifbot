from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from loader import db, bot
from states.admin_states import ProductState, EditProductState
from keyboards.inline.admin_inline import cancel_kb, get_confirm_kb

router = Router()

# =========================================================
# 1. MAHSULOTLAR RO'YXATI (MENYU)
# =========================================================
@router.message(F.text == "🍴 Menyu va Mahsulotlar")
async def menu_manage(message: types.Message):
    products = await db.get_all_products()
    
    text = "<b>🍴 MENYU VA MAHSULOTLAR BOSHQARUVI</b>\n\nQuyidagi ro'yxatdan mahsulotni tanlang yoki yangisini qo'shing:"
    
    kb = InlineKeyboardBuilder()
    
    for prod in products:
        kb.button(text=f"{prod['name_uz']}", callback_data=f"view_prod_{prod['id']}")
    
    kb.button(text="➕ Yangi Mahsulot Qo'shish", callback_data="add_prod")
    kb.adjust(1) 
    
    await message.answer(text, reply_markup=kb.as_markup())


# =========================================================
# 2. YANGI MAHSULOT QO'SHISH (WIZARD)
# =========================================================
@router.callback_query(F.data == "add_prod")
async def start_add_prod(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("📸 <b>1. Mahsulot rasmini yuboring:</b>", reply_markup=cancel_kb)
    await state.set_state(ProductState.photo)

@router.message(ProductState.photo)
async def add_prod_photo(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer("❌ Faqat rasm yuboring!")
        return
    await state.update_data(photo=message.photo[-1].file_id)
    await message.answer("🇺🇿 <b>2. Nomi (O'zbekcha):</b>\nMasalan: <i>Pechenye</i>", reply_markup=cancel_kb)
    await state.set_state(ProductState.name_uz)

@router.message(ProductState.name_uz)
async def add_prod_name_uz(message: types.Message, state: FSMContext):
    await state.update_data(name_uz=message.text)
    await message.answer("🇷🇺 <b>3. Nomi (Ruscha):</b>\nMasalan: <i>Печенье</i>", reply_markup=cancel_kb)
    await state.set_state(ProductState.name_ru)

@router.message(ProductState.name_ru)
async def add_prod_name_ru(message: types.Message, state: FSMContext):
    await state.update_data(name_ru=message.text)
    await message.answer("🇺🇿 <b>4. Tarkibi/Tarifi (O'zbekcha):</b>", reply_markup=cancel_kb)
    await state.set_state(ProductState.desc_uz)

@router.message(ProductState.desc_uz)
async def add_prod_desc_uz(message: types.Message, state: FSMContext):
    await state.update_data(desc_uz=message.text)
    await message.answer("🇷🇺 <b>5. Tarkibi/Tarifi (Ruscha):</b>", reply_markup=cancel_kb)
    await state.set_state(ProductState.desc_ru)

@router.message(ProductState.desc_ru)
async def add_prod_desc_ru(message: types.Message, state: FSMContext):
    await state.update_data(desc_ru=message.text)
    
    await state.update_data(weight_prices={})
    
    await message.answer(
        "⚖️ <b>6. O'lchovni kiriting (gr yoki kg):</b>\n\n"
        "Masalan: <b>500gr</b> yoki <b>1kg</b>.",
        reply_markup=cancel_kb
    )
    await state.set_state(ProductState.weights)

@router.message(ProductState.weights)
async def add_prod_weights(message: types.Message, state: FSMContext):
    weight = message.text.strip() 
    await state.update_data(current_weight=weight)
    
    await message.answer(f"💰 <b>{weight}</b> uchun narxni kiriting (so'mda):")
    await state.set_state(ProductState.price)

@router.message(ProductState.price)
async def add_prod_weight_price(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam (narx) kiriting!")
        return
        
    price = int(message.text)
    data = await state.get_data()
    
    weight_prices = data.get('weight_prices', {})
    weight = data.get('current_weight')
    
    weight_prices[weight] = price
    await state.update_data(weight_prices=weight_prices)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tugatish (Keyingisi)", callback_data="finish_weights")]
    ])
    
    saved_text = ""
    for w, p in weight_prices.items():
        saved_text += f"▫️ {w} = {p} so'm\n" 
        
    await message.answer(
        f"✅ Saqlandi!\n\n"
        f"<b>Hozirgi ro'yxat:</b>\n{saved_text}\n"
        "Yana boshqa <b>o'lchov</b> kiritasizmi? (Shunchaki yozing, masalan: 1kg 👇)\n"
        "Yoki hamma o'lchovni kiritib bo'lgan bo'lsangiz <b>✅ Tugatish</b> tugmasini bosing.",
        reply_markup=kb
    )
    await state.set_state(ProductState.weights)

@router.callback_query(ProductState.weights, F.data == "finish_weights")
async def finish_weights_and_prices(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    weight_prices = data.get('weight_prices', {})
    
    if not weight_prices:
        await call.answer("⚠️ Kamida bitta o'lchov va narx kiritishingiz kerak!", show_alert=True)
        return
        
    wp_text = ""
    for w, p in weight_prices.items():
        wp_text += f"▫️ {w} - {'{:,.0f}'.format(p).replace(',', ' ')} so'm\n"
    
    info = (
        f"🇺🇿 <b>{data['name_uz']}</b>\n{data['desc_uz']}\n\n"
        f"🇷🇺 <b>{data['name_ru']}</b>\n{data['desc_ru']}\n\n"
        f"⚖️💰 <b>Narxlar (O'lchov bo'yicha):</b>\n{wp_text}"
    )
    
    await call.message.delete()
    await call.message.answer_photo(
        photo=data['photo'],
        caption=info + "\n\n✅ <b>Menyuga qo'shaymi?</b>",
        reply_markup=get_confirm_kb("prod")
    )
    await state.set_state(ProductState.confirm)

@router.callback_query(ProductState.confirm, F.data == "confirm_prod")
async def save_new_prod(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    weight_prices = data.get('weight_prices', {})
    
    wp_str_list = [f"{w}={p}" for w, p in weight_prices.items()]
    weights_str = ",".join(wp_str_list)
    
    await db.add_product(
        category=None, 
        photo=data['photo'], 
        n_uz=data['name_uz'], 
        n_ru=data['name_ru'],
        d_uz=data['desc_uz'], 
        d_ru=data['desc_ru'], 
        price=0, 
        weights=weights_str
    )
    
    await call.message.delete()
    await call.message.answer("✅ <b>Mahsulot muvaffaqiyatli qo'shildi!</b>")
    await state.clear()
    
    await menu_manage(call.message)


# =========================================================
# 3. MAHSULOTNI KO'RISH (VIEW)
# =========================================================
@router.callback_query(F.data.startswith("view_prod_"))
async def view_product(call: types.CallbackQuery):
    prod_id = int(call.data.split("_")[2])
    prod = await db.get_product_by_id(prod_id)
    
    if not prod:
        await call.answer("Mahsulot topilmadi", show_alert=True)
        return

    weights_raw = prod.get('weights')
    wp_text = ""
    
    if weights_raw:
        items = weights_raw.split(",")
        for item in items:
            if "=" in item:
                w, p = item.split("=")
                p_fmt = "{:,.0f}".format(int(p)).replace(",", " ")
                wp_text += f"▫️ {w} - {p_fmt} so'm\n" 
    else:
        wp_text = "Kiritilmagan"
    
    text = (
        f"🆔 <b>ID: {prod['id']}</b>\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"🇺🇿 <b>{prod['name_uz']}</b>\n📄 {prod['desc_uz']}\n\n"
        f"🇷🇺 <b>{prod['name_ru']}</b>\n📄 {prod['desc_ru']}\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"⚖️💰 <b>Narxlar:</b>\n{wp_text}"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ TAHRIRLASH", callback_data=f"edit_prod_menu_{prod_id}")],
        [InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"del_prod_{prod_id}")],
        [InlineKeyboardButton(text="🔙 Ortga", callback_data="back_to_menu")]
    ])
    
    await call.message.delete()
    await call.message.answer_photo(photo=prod['photo_id'], caption=text, reply_markup=kb)


# =========================================================
# 4. TAHRIRLASH (SMART EDIT)
# =========================================================
@router.callback_query(F.data.startswith("edit_prod_menu_"))
async def show_edit_prod_options(call: types.CallbackQuery):
    prod_id = int(call.data.split("_")[3]) 
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 Nomini (Uz)", callback_data=f"chg_name_uz_{prod_id}"), 
         InlineKeyboardButton(text="🇷🇺 Nomini (Ru)", callback_data=f"chg_name_ru_{prod_id}")],
        
        [InlineKeyboardButton(text="🇺🇿 Tarifni (Uz)", callback_data=f"chg_desc_uz_{prod_id}"), 
         InlineKeyboardButton(text="🇷🇺 Tarifni (Ru)", callback_data=f"chg_desc_ru_{prod_id}")],
         
        [InlineKeyboardButton(text="📸 Rasmni", callback_data=f"chg_photo_id_{prod_id}"),
         InlineKeyboardButton(text="⚖️💰 O'lchovlar/Narxlar", callback_data=f"chg_weights_{prod_id}")],
         
        [InlineKeyboardButton(text="🔙 Bekor qilish", callback_data=f"view_prod_{prod_id}")]
    ])
    
    await call.message.edit_caption(caption="📝 <b>Nimani o'zgartirmoqchisiz?</b>", reply_markup=kb)

@router.callback_query(F.data.startswith("chg_"))
async def ask_prod_value(call: types.CallbackQuery, state: FSMContext):
    parts = call.data.split("_")
    prod_id = int(parts[-1])
    field = "_".join(parts[1:-1]) 
    
    await state.update_data(edit_id=prod_id, edit_field=field)
    
    if field == "weights":
        msg = "⚖️💰 Yangi <b>O'lchov=Narx</b> qiymatlarini kiriting.\n<i>(Vergul bilan ajrating. Masalan: 500gr=50000, 1kg=60000)</i>:"
    else:
        msg_map = {
            "name_uz": "🇺🇿 Yangi <b>Nomi (Uz)</b>:",
            "name_ru": "🇷🇺 Yangi <b>Nomi (Ru)</b>:",
            "desc_uz": "🇺🇿 Yangi <b>Tarifi (Uz)</b>:",
            "desc_ru": "🇷🇺 Yangi <b>Tarifi (Ru)</b>:",
            "photo_id": "📸 Yangi <b>Rasm</b> yuboring:"
        }
        msg = msg_map.get(field, "Qiymatni kiriting:")
    
    await call.message.delete()
    await call.message.answer(msg, reply_markup=cancel_kb)
    await state.set_state(EditProductState.input_new_value)

@router.message(EditProductState.input_new_value)
async def save_prod_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    prod_id = data['edit_id']
    field = data['edit_field']
    
    new_value = None
    
    if field == "photo_id":
        if not message.photo:
            await message.answer("❌ Rasm yuboring!")
            return
        new_value = message.photo[-1].file_id
        
    elif field == "weights":
        raw_list = message.text.split(",")
        clean_list = []
        try:
            for item in raw_list:
                if "=" in item:
                    w, p = item.split("=")
                    clean_list.append(f"{w.strip()}={int(p.strip())}") 
        except:
            await message.answer("❌ Xato! Misol: 500gr=50000, 1kg=60000")
            return
            
        if not clean_list:
            await message.answer("❌ Xato format!")
            return
            
        new_value = ",".join(clean_list)
        
    else:
        new_value = message.text
        
    await db.update_product_field(prod_id, field, new_value)
    await message.answer("✅ <b>Muvaffaqiyatli yangilandi!</b>")
    await state.clear()
    await menu_manage(message)


# =========================================================
# 5. O'CHIRISH (DELETE)
# =========================================================
@router.callback_query(F.data.startswith("del_prod_"))
async def ask_prod_del(call: types.CallbackQuery):
    prod_id = int(call.data.split("_")[2])
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Ha, o'chirilsin", callback_data=f"cfm_del_prod_{prod_id}")],
        [InlineKeyboardButton(text="🔙 Yo'q", callback_data=f"view_prod_{prod_id}")]
    ])
    await call.message.delete()
    await call.message.answer("⚠️ <b>Rostdan ham o'chirasizmi?</b>\nMijozlar bu mahsulotni ko'ra olmay qoladi.", reply_markup=kb)

@router.callback_query(F.data.startswith("cfm_del_prod_"))
async def confirm_prod_del(call: types.CallbackQuery):
    prod_id = int(call.data.split("_")[3])
    await db.delete_product(prod_id)
    await call.answer("O'chirildi!", show_alert=True)
    await call.message.delete()
    await menu_manage(call.message)

@router.callback_query(F.data == "back_to_menu")
async def back_to_main_menu(call: types.CallbackQuery):
    await call.message.delete()
    await menu_manage(call.message)
