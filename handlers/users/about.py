from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile 
from loader import db
from locales.texts import TEXTS
from keyboards.inline.buttons import get_back_kb, main_user_menu

router = Router()

# =========================================================
# 1. BIZ HAQIMIZDA 
# =========================================================
@router.callback_query(F.data == "menu_about")
async def show_about_handler(call: CallbackQuery):
    user_id = call.from_user.id
    lang = await db.get_user_lang(user_id)
    
    await call.message.delete()

    photo_file = FSInputFile("images/logo.png")

    try:
        await call.message.answer_photo(
            photo=photo_file,
            caption=TEXTS["about_text"][lang],
            reply_markup=get_back_kb(lang)
        )
    except Exception as e:
        print(f"Rasm yuklashda xatolik: {e}")
        await call.message.answer(
            text=TEXTS["about_text"][lang],
            reply_markup=get_back_kb(lang)
        )


# =========================================================
# 2. ORQAGA 
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