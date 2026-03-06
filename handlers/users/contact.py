from aiogram import Router, F
from aiogram.types import CallbackQuery
from loader import db, bot
from locales.texts import TEXTS
from keyboards.inline.contact_buttons import get_contact_kb
from keyboards.inline.buttons import main_user_menu

router = Router()

# =========================================================
# 📍 ALOQA MENYUSINI KO'RSATISH
# =========================================================
@router.callback_query(F.data == "menu_contact")
async def show_contact_handler(call: CallbackQuery):
    user_id = call.from_user.id
    lang = await db.get_user_lang(user_id)
    
    await call.message.delete()

    await call.message.answer(
        text=TEXTS["contact_text"][lang],
        reply_markup=get_contact_kb(lang)
    )

# =========================================================
# 📞 TELEFON TUGMASI 
# =========================================================
@router.callback_query(F.data == "contact_action_phone")
async def send_phone_contact(call: CallbackQuery):
    await call.message.answer_contact(
        phone_number="+998950942225",  
        first_name="Afif Family",
        last_name="Aloqa Markazi"
    )
    await call.answer()




# =========================================================
# 🔙 ORQAGA (BOSH SAHIFAGA) QAYTISH
# =========================================================
@router.callback_query(F.data == "back_to_main")
async def back_to_main_menu_handler(call: CallbackQuery):
    user_id = call.from_user.id
    
    user = await db.get_user_info(user_id)
    
    if user:
        lang = user['language']
        full_name = user.get('full_name') or call.from_user.full_name
    else:
        lang = 'uz'
        full_name = call.from_user.full_name

    if lang == 'uz':
        welcome_header = f"👋 <b>Assalomu alaykum, {full_name}!</b>\n\n"
    else:
        welcome_header = f"👋 <b>Здравствуйте, {full_name}!</b>\n\n"

    welcome_text = TEXTS["welcome"][lang]
    final_text = welcome_header + welcome_text.replace("<b>Xush kelibsiz!</b> 🌮\n\n", "").replace("<b>Добро пожаловать!</b> 🌮\n\n", "")

    await call.message.delete()
    await call.message.answer(
        text=final_text, 
        reply_markup=main_user_menu(lang)
    )
