import re
from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, Message, CallbackQuery
from loader import db
from data.config import ADMINS
from states.user_states import RegisterState
from keyboards.default.admin_kb import super_admin_panel, admin_panel
from keyboards.inline.buttons import main_user_menu
from keyboards.default.register_kb import lang_kb, phone_kb_uz, phone_kb_ru
from locales.texts import TEXTS

router = Router()

# ==========================================================
# 1. UNIQUITY START (Boshqaruv Markazi)
# ==========================================================
@router.message(CommandStart())
async def bot_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    if str(user_id) in ADMINS or user_id in [int(x) for x in ADMINS]:
        await message.answer(
            f"🕴 <b>Admin Panelga xush kelibsiz, BOSS!</b>\n\n"
            "Sizda to'liq boshqaruv huquqi mavjud.",
            reply_markup=super_admin_panel
        )
        return

    is_admin = await db.is_admin(user_id)
    if is_admin:
        await message.answer(
            f"👔 <b>Ishchi Panelga xush kelibsiz!</b>\n\n"
            "Ishlash uchun bo'limni tanlang 👇",
            reply_markup=admin_panel
        )
        return

    user = await db.get_user_info(user_id)
    
    if user:
        lang = user['language']
        full_name = user.get('full_name') or message.from_user.full_name
        if lang == 'uz':
            welcome_header = f"👋 <b>Assalomu alaykum, {full_name}!</b>\n\n"
        else:
            welcome_header = f"👋 <b>Здравствуйте, {full_name}!</b>\n\n"
            
        welcome_text = TEXTS["welcome"][lang]
        final_text = welcome_header + welcome_text.replace("<b>Xush kelibsiz!</b> 🌮\n\n", "").replace("<b>Добро пожаловать!</b> 🌮\n\n", "")
        
        await message.answer(
            text=final_text,
            reply_markup=main_user_menu(lang)
        )
    else:
        await message.answer(
            "👋 <b>Assalomu alaykum! / Здравствуйте!</b>\n\n"
            "🤖 Botdan foydalanish uchun, iltimos, tilingizni tanlang:\n"
            "➖➖➖➖➖➖➖➖➖➖\n"
            "🤖 Для использования бота, пожалуйста, выберите язык:",
            reply_markup=lang_kb
        )
        await state.set_state(RegisterState.language)


# ==========================================================
# 2. ORQAGA / BOSH SAHIFA 
# ==========================================================
@router.callback_query(F.data == "main_menu_start")
async def back_to_main_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    
    user_id = call.from_user.id
    user = await db.get_user_info(user_id)
    
    if not user:
        await call.message.delete()
        await call.message.answer("⚠️ Iltimos, /start bosing.")
        return

    lang = user['language']
    full_name = user.get('full_name') or call.from_user.full_name
    
    if lang == 'uz':
        welcome_header = f"👋 <b>Assalomu alaykum, {full_name}!</b>\n\n"
    else:
        welcome_header = f"👋 <b>Здравствуйте, {full_name}!</b>\n\n"
        
    welcome_text = TEXTS["welcome"][lang]
    final_text = welcome_header + welcome_text.replace("<b>Xush kelibsiz!</b> 🌮\n\n", "").replace("<b>Добро пожаловать!</b> 🌮\n\n", "")
    
    await call.message.delete()
    await call.message.answer(text=final_text, reply_markup=main_user_menu(lang))


# ==========================================================
# 3. REGISTRATSIYA JARAYONI 
# ==========================================================

@router.message(RegisterState.language)
async def register_lang(message: Message, state: FSMContext):
    text = message.text
    
    if text == "🇺🇿 O'zbekcha":
        lang = 'uz'
        msg_text = (
            "✅ <b>Til tanlandi: O'zbekcha</b>\n\n"
            "📞 <b>Telefon raqamingizni yuboring.</b>\n"
            "Pastdagi tugmani bosing yoki raqamni qo'lda yozing:\n"
            "<i>(Masalan: +998901234567)</i>"
        )
        kb = phone_kb_uz
    elif text == "🇷🇺 Русский":
        lang = 'ru'
        msg_text = (
            "✅ <b>Язык выбран: Русский</b>\n\n"
            "📞 <b>Отправьте ваш номер телефона.</b>\n"
            "Нажмите кнопку ниже или введите номер вручную:\n"
            "<i>(Например: +998901234567)</i>"
        )
        kb = phone_kb_ru
    else:
        await message.answer("Iltimos, tugmalardan birini tanlang! / Пожалуйста, выберите одну из кнопок!")
        return

    await state.update_data(reg_lang=lang)
    await message.answer(msg_text, reply_markup=kb)
    await state.set_state(RegisterState.phone)


@router.message(RegisterState.phone)
async def register_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('reg_lang')
    
    final_phone = ""
    
    if message.contact:
        final_phone = message.contact.phone_number
        if not final_phone.startswith("+"):
            final_phone = f"+{final_phone}"
    else:
        raw_phone = message.text or ""
        only_digits = re.sub(r"\D", "", raw_phone)

        if len(only_digits) == 9: 
            final_phone = f"+998{only_digits}"
        elif len(only_digits) == 12 and only_digits.startswith("998"): 
            final_phone = f"+{only_digits}"
        else:
            error = "🚫 <b>Noto'g'ri format!</b>\n+998901234567" if lang == 'uz' else "🚫 <b>Неверный формат!</b>\n+998901234567"
            await message.answer(error)
            return

    if not final_phone.startswith("+998"):
        error = "🚫 Faqat O'zbekiston raqamlari (+998)" if lang == 'uz' else "🚫 Только номера Узбекистана (+998)"
        await message.answer(error)
        return

    await state.update_data(reg_phone=final_phone)
    
    msg_text = (
        "✅ <b>Raqam qabul qilindi.</b>\n\n✍️ <b>Ismingizni kiriting:</b>"
    ) if lang == 'uz' else (
        "✅ <b>Номер принят.</b>\n\n✍️ <b>Введите ваше имя:</b>"
    )
    
    await message.answer(msg_text, reply_markup=ReplyKeyboardRemove())
    await state.set_state(RegisterState.fullname)


@router.message(RegisterState.fullname)
async def register_fullname(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('reg_lang')
    phone = data.get('reg_phone')
    
    raw_name = message.text
    
    if not raw_name or len(raw_name) < 3 or any(char.isdigit() for char in raw_name):
        error = "🚫 Ism noto'g'ri (raqamsiz, min 3 harf)." if lang == 'uz' else "🚫 Имя некорректно (без цифр, мин 3 буквы)."
        await message.answer(error)
        return

    full_name = raw_name.title() 
    
    user_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else None
    
    await db.add_user(user_id, username, full_name, lang, phone)
    
    welcome_text = TEXTS["welcome"][lang]
    
    if lang == 'uz':
        final_msg = f"🎉 <b>Tabriklaymiz, {full_name}!</b>\nRo'yxatdan o'tdingiz.\n\n{welcome_text}"
    else:
        final_msg = f"🎉 <b>Поздравляем, {full_name}!</b>\nВы зарегистрированы.\n\n{welcome_text}"
    
    await message.answer(
        final_msg,
        reply_markup=main_user_menu(lang)
    )
    
    await state.clear()