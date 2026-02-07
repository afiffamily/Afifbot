from aiogram.fsm.state import State, StatesGroup

class RegisterState(StatesGroup):
    language = State()   
    phone = State()      
    fullname = State()  

class SettingsState(StatesGroup):
    edit_phone = State()
    edit_name = State()    


class SettingsState(StatesGroup):
    edit_lang = State()
    edit_phone = State()
    edit_name = State()

class CheckoutState(StatesGroup):
    choose_address = State()
    delivery_type = State()
    location = State()
    confirm_location = State() 
    extra_info = State()
    phone = State()
    payment_type = State()
    confirm = State()