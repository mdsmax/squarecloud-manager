import disnake
from disnake.ext import commands

class AppsExtension(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener("on_button_click")
    async def on_button_click(self, inter: disnake.MessageInteraction):
        ...

def setup(bot):
    bot.add_cog(AppsExtension(bot)) 