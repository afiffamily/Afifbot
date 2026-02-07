from aiogram.fsm.state import State, StatesGroup

# =========================================================
# 1. MARKETING (Reklama va Xabarlar)
# =========================================================
class BroadcastState(StatesGroup):
    post_uz = State()
    post_ru = State()
    confirm = State()

class DirectMessageState(StatesGroup):
    user_id = State()
    message_content = State()
    confirm = State()

# =========================================================
# 2. HR (Admin boshqaruvi)
# =========================================================
class NewAdminState(StatesGroup):
    user_id = State()

# =========================================================
# 3. MAHSULOTLAR (MENYU)
# =========================================================
class ProductState(StatesGroup):
    photo = State()
    name_uz = State()
    name_ru = State()
    desc_uz = State()
    desc_ru = State()
    price = State()  
    confirm = State()

class EditProductState(StatesGroup):
    input_new_value = State()

# =========================================================
# 4. AKSIYALAR 
# =========================================================
class PromoState(StatesGroup):
    photo = State()
    name_uz = State()      
    name_ru = State()      
    caption_uz = State()
    caption_ru = State()
    price = State()        
    confirm = State()

class EditPromoState(StatesGroup):
    input_new_value = State()