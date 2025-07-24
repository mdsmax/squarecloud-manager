from .get_account_informations import get_account_informations
from .get_bot_info import get_bot_info
from .upload_bot import upload_bot
from .manage_bot import start_bot, stop_bot, restart_bot, delete_bot

class SquareCloud:
    get_account_informations = get_account_informations
    get_bot_info = get_bot_info
    upload_bot = upload_bot
    start_bot = start_bot
    stop_bot = stop_bot
    restart_bot = restart_bot
    delete_bot = delete_bot