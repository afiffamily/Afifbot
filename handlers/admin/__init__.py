from . import statistika
from . import aksiya
from . import menu
from . import hr      
from . import marketing

admin_routers = [
    statistika.router,
    aksiya.router,
    menu.router,
    hr.router,
    marketing.router         
]