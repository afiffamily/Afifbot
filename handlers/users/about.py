from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile 
from loader import db
from locales.texts import TEXTS
from keyboards.inline.buttons import get_back_kb

router = Router()

# =========================================================
# BIZ HAQIMIZDA 
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