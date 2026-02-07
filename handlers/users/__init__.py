from . import start
from . import aksiya
from . import settings  
from . import about
from . import menu
from . import contact
from . import cart
from . import orders

users_routers = [
    start.router,
    aksiya.router,
    settings.router,
    about.router,
    menu.router,
    contact.router,
    cart.router,
    orders.router,
]