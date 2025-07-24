from .get_account_informations import get_account_informations
from .upload_bot import upload_bot
from .manage_bot import start_bot, stop_bot, restart_bot, delete_bot
from .get_app_status import get_bot_status

class SquareCloud:
    get_account_informations = get_account_informations
    upload_bot = upload_bot
    start_bot = start_bot
    stop_bot = stop_bot
    restart_bot = restart_bot
    delete_bot = delete_bot
    get_bot_status = get_bot_status