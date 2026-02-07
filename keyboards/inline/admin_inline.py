from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_confirm_kb(action_code):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"confirm_{action_code}"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action")
        ]
    ])

cancel_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action")]
])

marketing_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📡 Ommaviy Xabar (Broadcast)", callback_data="mkt_broadcast")],
    [InlineKeyboardButton(text="🎯 Shaxsiy Xabar (Direct)", callback_data="mkt_direct")],
    [InlineKeyboardButton(text="🔙 Yopish", callback_data="close_panel")]
])