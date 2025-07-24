import disnake
from disnake.ext import commands

import dotenv
import os

bot = commands.Bot(command_prefix=commands.when_mentioned, intents=disnake.Intents.all())

@bot.event
async def on_ready():
    os.system("cls" if os.name == "nt" else "clear")
    print("""
  _______                                  _______ __                __ 
 |   _   .-----.--.--.---.-.----.-----.   |   _   |  .-----.--.--.--|  |
 |   1___|  _  |  |  |  _  |   _|  -__|   |.  1___|  |  _  |  |  |  _  |
 |____   |__   |_____|___._|__| |_____|   |.  |___|__|_____|_____|_____|
 |:  1   |  |  |                          |:  1   |
 |::.. . |  |__|                          |::.. . |
 `-------'                                `-------'
 @mdsmax | squarecloud.app | github.com/mdsmax/squarecloud-manager/
    """)
    print(f" o bot está conectado como {bot.user.name} (ID:{bot.user.id})")
    print(f" o bot está em {len(bot.guilds)} servidor(es)")
    await bot.change_presence(activity=disnake.CustomActivity(name="💙 squarecloud.app"))

for root, dirs, files in os.walk("commands"):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            module_path = path.replace(os.sep, ".")[:-3]
            try:
                bot.load_extension(module_path)
            except Exception:
                pass

dotenv.load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
SQUARECLOUD_TOKEN = os.getenv("SQUARECLOUD_TOKEN")
MERCADOPAGO_TOKEN = os.getenv("MERCADOPAGO_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")

if not TOKEN or not SQUARECLOUD_TOKEN or not MERCADOPAGO_TOKEN or not OWNER_ID:
    raise ValueError("Variáveis de ambiente não encontradas - configure-as no arquivo .env")

bot.run(TOKEN)