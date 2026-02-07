from aiogram import Router, F
from aiogram.types import CallbackQuery
from loader import db, bot
from locales.texts import TEXTS
from keyboards.inline.contact_buttons import get_contact_kb

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
        phone_number="+998901234567",
        first_name="Afif Family",
        last_name="Aloqa Markazi"
    )
    await call.answer()

# =========================================================
# 📍 LOKATSIYA TUGMASI 
# =========================================================
OFFICE_LAT = 41.315083
OFFICE_LON = 69.155194

@router.callback_query(F.data == "contact_action_location")
async def send_location_map(call: CallbackQuery):
    await call.message.answer_location(
        latitude=OFFICE_LAT,
        longitude=OFFICE_LON
    )
    await call.answer()