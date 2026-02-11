import csv
import io
from datetime import datetime
import pytz  

from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from loader import db

router = Router()

# =========================================================
# 1. DASHBOARD (KREATIV DIZAYN)
# =========================================================
@router.message(F.text.in_({"📊 Kengaytirilgan Statistika", "📊 Kunlik hisobot"}))
async def show_dashboard(message: types.Message):
    tz = pytz.timezone('Asia/Tashkent')
    date_now = datetime.now(tz).strftime("%d.%m.%Y %H:%M")

    stats = await db.get_full_stats()
    admin_count = await db.count_admins()
    
    sales = stats.get('sales', 0) or 0
    sales_fmt = "{:,.0f}".format(sales).replace(",", " ")
    
    text = (
        f"📅 <b>HISOBOT VAQTI:</b> {date_now}\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
        
        "💰 <b>MOLIYAVIY KO'RSATKICH (Bugun):</b>\n"
        f"├ 💸 Tushum: <b>{sales_fmt} so'm</b>\n"
        f"└ 📦 Cheklar soni: <b>{stats.get('orders', 0)} ta</b>\n\n"
        
        "👥 <b>AUDITORIYA TARQIBI:</b>\n"
        f"├ 🇺🇿 O'zbek tilida: <b>{stats.get('users_uz', 0)} ta</b>\n"
        f"├ 🇷🇺 Rus tilida: <b>{stats.get('users_ru', 0)} ta</b>\n"
        f"└ 👤 Jami mijozlar: <b>{stats.get('users', 0)} ta</b>\n\n"
        
        f"👮‍♂️ <b>Xodimlar shtati:</b> {admin_count} kishi\n\n"
        "<i>📊 Batafsil tahlil va raqamlar uchun Excel faylni yuklab oling 👇</i>"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 To'liq hisobotni yuklash (.csv)", callback_data="download_excel")],
        [InlineKeyboardButton(text="🔄 Yangilash", callback_data="refresh_stats")]
    ])
    
    await message.answer(text, reply_markup=kb)

@router.callback_query(F.data == "refresh_stats")
async def refresh_statistics(call: types.CallbackQuery):
    try:
        await call.message.delete()
        await show_dashboard(call.message)
    except:
        await call.answer("Ma'lumotlar yangilandi!")


# =========================================================
# 2. EXCEL YUKLASH (FAYL YARATISH QISMI)
# =========================================================
@router.callback_query(F.data == "download_excel")
async def download_excel_real(call: types.CallbackQuery):
    await call.answer("⏳ Fayl tayyorlanmoqda...", show_alert=False)
    
    tz = pytz.timezone('Asia/Tashkent')
    now = datetime.now(tz)
    
    users = await db.get_all_users_detailed()
    
    if not users:
        await call.message.answer("📂 Bazada mijozlar yo'q.")
        return
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Ism Familiya", "Username", "Telefon", "Til", "Ro'yxatdan o'tgan sana"])
    
    for user in users:
        reg_date = user['reg_date'].strftime("%Y-%m-%d %H:%M") if user['reg_date'] else "Noma'lum"
        phone = user['phone_number'] if user['phone_number'] else "Kiritilmagan"
        username = f"@{user['username']}" if user['username'] else "Yo'q"
        
        writer.writerow([
            user['user_id'],
            user['full_name'],
            username,
            phone,
            user['language'],
            reg_date
        ])
    
    output.seek(0)
    bytes_io = io.BytesIO(output.getvalue().encode('utf-8-sig'))
    filename = f"Mijozlar_Bazasi_{now.strftime('%Y%m%d')}.csv"
    document = BufferedInputFile(bytes_io.read(), filename=filename)
    
    await call.message.answer_document(
        document=document,
        caption=f"📂 <b>To'liq mijozlar bazasi</b>\n📅 Sana: {now.strftime('%d.%m.%Y %H:%M')}"
    )
