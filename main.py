import disnake
from disnake.ext import commands

import dotenv
import os

# Vai ser um bot com apenas Slash Commands, porém preciso usar as Intents
bot = commands.Bot(command_prefix=commands.when_mentioned, intents=disnake.Intents.all())

@bot.event
async def on_ready():
    os.system("cls" if os.name == "nt" else "clear")
    print(f"O bot está conectado como {bot.user.name} (ID:{bot.user.id})")
    print(f"O bot está em {len(bot.guilds)} servidor(es)")
    await bot.change_presence(activity=disnake.CustomActivity(name="💙 squarecloud.app"))

# Carregar comandos do diretório 'commands'
for command in os.listdir("commands"):
    if command.endswith(".py"):
        try:
            bot.load_extension(f"commands.{command[:-3]}")
        except Exception as e:
            pass

# Inicialização 
dotenv.load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
SQUARECLOUD_TOKEN = os.getenv("SQUARECLOUD_TOKEN")
MERCADOPAGO_TOKEN = os.getenv("MERCADOPAGO_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")

if not TOKEN or not SQUARECLOUD_TOKEN or not MERCADOPAGO_TOKEN or not OWNER_ID:
    raise ValueError("Variáveis de ambiente não encontradas - configure-as no arquivo .env")

bot.run(TOKEN)