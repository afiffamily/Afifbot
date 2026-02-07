import re
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from loader import db
from locales.texts import TEXTS
from keyboards.inline.buttons import get_settings_kb, get_lang_kb, main_user_menu
from states.user_states import SettingsState

router = Router()

# =========================================================
# 1. SOZLAMALARNI KO'RSATISH
# =========================================================
@router.callback_query(F.data == "menu_settings")
@router.callback_query(F.data == "back_to_settings")
async def show_settings(call: CallbackQuery, state: FSMContext):
    await state.clear()
    
    user_id = call.from_user.id
    user = await db.get_user_info(user_id)
    
    if not user:
        await call.answer("Foydalanuvchi topilmadi!", show_alert=True)
        return

    lang = user['language'] if user['language'] else 'uz'
    
    lang_display = "🇺🇿 O'zbekcha" if lang == 'uz' else "🇷🇺 Русский"
    phone = user.get('phone_number', '---')
    name = user.get('full_name', '---')
    
    text = TEXTS["settings_info"][lang].format(
        lang=lang_display,
        phone=phone,
        name=name
    )
    
    try:
        await call.message.edit_text(text, reply_markup=get_settings_kb(lang))
    except:
        await call.message.delete()
        await call.message.answer(text, reply_markup=get_settings_kb(lang))


# =========================================================
# 2. TILNI O'ZGARTIRISH
# =========================================================
@router.callback_query(F.data == "set_edit_lang")
async def edit_lang_start(call: CallbackQuery):
    user_id = call.from_user.id
    lang = await db.get_user_lang(user_id)
    
    await call.message.edit_text(
        TEXTS["settings_title"][lang], 
        reply_markup=get_lang_kb(lang)
    )

@router.callback_query(F.data.startswith("lang_set_"))
async def lang_selected(call: CallbackQuery, state: FSMContext):
    new_lang = call.data.split("_")[2] 
    user_id = call.from_user.id
    
    await db.update_user_lang(user_id, new_lang)
    await call.answer(TEXTS["success_lang"][new_lang], show_alert=True)
    
    await show_settings(call, state)


# =========================================================
# 3. TELEFONNI O'ZGARTIRISH
# =========================================================
@router.callback_query(F.data == "set_edit_phone")
async def edit_phone_start(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    lang = await db.get_user_lang(user_id)
    
    await call.message.delete()
    await call.message.answer(
        TEXTS["ask_new_phone"][lang], 
    )
    await state.set_state(SettingsState.edit_phone)

@router.message(SettingsState.edit_phone)
async def edit_phone_save(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await db.get_user_lang(user_id)
    
    raw_phone = message.text or ""
    only_digits = re.sub(r"\D", "", raw_phone)
    final_phone = ""

    if len(only_digits) == 9: 
        final_phone = f"+998{only_digits}"
    elif len(only_digits) == 12 and only_digits.startswith("998"):
        final_phone = f"+{only_digits}"
    else:
        await message.answer(TEXTS["error_format"][lang])
        return

    await db.update_user_phone(user_id, final_phone)
    await message.answer(TEXTS["success_phone"][lang])
    
    user = await db.get_user_info(user_id)
    lang_display = "🇺🇿 O'zbekcha" if lang == 'uz' else "🇷🇺 Русский"
    phone = user.get('phone_number', '---')
    name = user.get('full_name', '---')
    
    text = TEXTS["settings_info"][lang].format(
        lang=lang_display,
        phone=phone,
        name=name
    )
    await message.answer(text, reply_markup=get_settings_kb(lang))
    await state.clear()


# =========================================================
# 4. ISMNI O'ZGARTIRISH
# =========================================================
@router.callback_query(F.data == "set_edit_name")
async def edit_name_start(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    lang = await db.get_user_lang(user_id)
    
    await call.message.delete()
    await call.message.answer(TEXTS["ask_new_name"][lang])
    await state.set_state(SettingsState.edit_name)

@router.message(SettingsState.edit_name)
async def edit_name_save(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await db.get_user_lang(user_id)
    
    new_name = message.text
    if len(new_name) < 3:
        await message.answer(TEXTS["error_short"][lang])
        return
        
    await db.update_user_fullname(user_id, new_name)
    await message.answer(TEXTS["success_name"][lang])
    
    user = await db.get_user_info(user_id)
    lang_display = "🇺🇿 O'zbekcha" if lang == 'uz' else "🇷🇺 Русский"
    phone = user.get('phone_number', '---')
    name = user.get('full_name', '---')
    
    text = TEXTS["settings_info"][lang].format(
        lang=lang_display,
        phone=phone,
        name=name
    )
    await message.answer(text, reply_markup=get_settings_kb(lang))
    await state.clear()


# =========================================================
# 5. ORQAGA (BOSH SAHIFAGA) QAYTISH
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