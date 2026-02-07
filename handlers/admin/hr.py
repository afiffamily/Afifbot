from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from loader import db, bot
from data.config import ADMINS
from states.admin_states import NewAdminState

router = Router()

SUPER_ADMIN_ID = int(ADMINS[0])

# ==========================================================
# 1. ADMINLAR RO'YXATI (Eski uslubda)
# ==========================================================
@router.message(F.text == "👥 HR (Xodimlar)")
async def show_admin_list_entry(message: Message):
    await show_admin_list(message)

async def show_admin_list(event):
    user_id = event.from_user.id
    if user_id != SUPER_ADMIN_ID:
        if isinstance(event, Message):
            await event.answer("⛔️ <b>Ruxsat yo'q!</b>\nBu bo'lim faqat Boshliq uchun.")
        elif isinstance(event, CallbackQuery):
            await event.answer("⛔️ Ruxsat yo'q!", show_alert=True)
        return

    admins = await db.get_all_admins()
    
    text = (
        "🛡 <b>ADMINLAR RO'YXATI</b>\n\n"
        "Hozirgi vaqtda botni boshqaruvchi shaxslar:\n\n"
    )
    
    count = 1
    for admin in admins:
        if admin['user_id'] != SUPER_ADMIN_ID:
            name = admin['full_name']
            
            # Sanani formatlash
            try:
                joined = admin['added_at'].strftime("%d.%m.%Y")
            except:
                joined = "Eski"
            
            text += f"{count}. 👤 <b>{name}</b>\n🆔 ID: <code>{admin['user_id']}</code>\n📅 Sana: {joined}\n\n"
            count += 1
            
    if count == 1:
        text += "<i>Qo'shimcha adminlar yo'q.</i>"
        
    text += "\n<i>⚠️ Super Admin (Siz) ro'yxatda ko'rinmaysiz.</i>"

    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Admin qo'shish", callback_data="admin_add_new")
    builder.button(text="➖ Admin o'chirish", callback_data="admin_delete_start")
    

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=builder.as_markup())
    else:
        await event.answer(text, reply_markup=builder.as_markup())


# ==========================================================
# 2. ADMIN QO'SHISH (Bazani tekshirish bilan)
# ==========================================================
@router.callback_query(F.data == "admin_add_new")
async def start_add_admin(call: CallbackQuery, state: FSMContext):
    if call.from_user.id != SUPER_ADMIN_ID:
        return await call.answer("Ruxsat yo'q!", show_alert=True)

    await call.message.delete()
    await call.message.answer(
        "➕ <b>YANGI ADMIN QO'SHISH</b>\n\n"
        "Yangi admin qilmoqchi bo'lgan foydalanuvchining <b>ID raqamini</b> yuboring:\n"
        "<i>Eslatma: U avval botga /start bosgan bo'lishi kerak.</i>",
        reply_markup=InlineKeyboardBuilder().button(text="🔙 Bekor qilish", callback_data="admin_cancel_action").as_markup()
    )
    await state.set_state(NewAdminState.user_id)

@router.message(NewAdminState.user_id)
async def save_new_admin(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("⚠️ Faqat raqamli ID kiriting!")
        return
    
    new_id = int(message.text)
    
    if new_id == message.from_user.id:
        await message.answer("😅 Siz allaqachon adminsiz.")
        return

    user = await db.get_user_info(new_id)
    
    if not user:
        await message.answer(
            "❌ <b>Foydalanuvchi topilmadi!</b>\n"
            "Bu odam botga hali /start bosmagan. Avval botga kirsin, keyin ID sini yuboring."
        )
        return

    if await db.is_admin(new_id):
        await message.answer("⚠️ Bu foydalanuvchi allaqachon admin!")
        return

    if user.get('username'):
        display_name = f"{user['username']}"
    else:
        display_name = user['full_name']

    await db.add_admin(new_id, display_name, message.from_user.id)
    
    await message.answer(f"✅ <b>Muvaffaqiyatli!</b>\n\n👤 <b>{display_name}</b> endi adminlar safida.")
    await state.clear()
    
    await show_admin_list(message)


# ==========================================================
# 3. ADMIN O'CHIRISH
# ==========================================================
@router.callback_query(F.data == "admin_delete_start")
async def start_delete_admin(call: CallbackQuery):
    if call.from_user.id != SUPER_ADMIN_ID:
        return await call.answer("Ruxsat yo'q!", show_alert=True)

    admins = await db.get_all_admins()
    
    builder = InlineKeyboardBuilder()
    has_candidates = False

    for admin in admins:
        if admin['user_id'] != SUPER_ADMIN_ID:
            name = admin['full_name']
            builder.button(text=f"🗑 {name}", callback_data=f"del_adm_{admin['user_id']}")
            has_candidates = True
    
    builder.adjust(1)
    builder.button(text="🔙 Bekor qilish", callback_data="admin_cancel_action")

    if not has_candidates:
        await call.answer("O'chirish uchun boshqa adminlar yo'q.", show_alert=True)
        return

    await call.message.edit_text(
        "➖ <b>ADMINNI O'CHIRISH</b>\n\n"
        "Qaysi adminni huquqdan mahrum qilmoqchisiz? Tanlang:",
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data.startswith("del_adm_"))
async def confirm_delete_admin(call: CallbackQuery):
    target_id = int(call.data.split("_")[2])
    
    if target_id == SUPER_ADMIN_ID:
        return await call.answer("Boshliqni o'chirish mumkin emas!", show_alert=True)

    await db.delete_admin(target_id)
    await call.answer("✅ Admin o'chirildi!", show_alert=True)
    
    await show_admin_list(call)


# ==========================================================
# BEKOR QILISH / ORQAGA
# ==========================================================
@router.callback_query(F.data == "admin_cancel_action")
async def cancel_manage_action(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await show_admin_list(call)