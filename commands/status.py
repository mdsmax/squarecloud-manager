import disnake
from disnake.ext import commands

from database import Database
from functions.perms import Perms
from functions.squarecloud import SquareCloud

from commands.extensions.painel.config import Config

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.slash_command(name="status", description="[DEV] Veja o status e informações de uma aplicação")
    async def status(self, inter: disnake.ApplicationCommandInteraction, aplicacao: str = commands.Param(description="Aplicação a ser consultada", autocomplete=True)):
        if not Perms.is_owner(inter):
            return await inter.response.send_message("Faltam permissões para acessar este comando", ephemeral=True)
        
        if aplicacao == "MISSING_PERMISSIONS":
            return await inter.response.send_message("Faltam permissões para acessar este comando", ephemeral=True)
        
        if aplicacao == "NO_APPLICATIONS":
            return await inter.response.send_message("Nenhuma aplicação encontrada", ephemeral=True)

        embed, components = await Config.Aplicacao.aplicacao_builder(inter, aplicacao, config=True)
        await inter.response.send_message(embed=embed, components=components, ephemeral=True)

    @status.autocomplete("aplicacao")
    async def status_autocomplete(self, inter: disnake.ApplicationCommandInteraction, aplicacao: str):
        if not Perms.is_owner(inter):
            return [
                disnake.OptionChoice(
                    name="❌ Faltam permissões para acessar este comando",
                    value="MISSING_PERMISSIONS"
                )
            ]
        
        apps = Database.obter("apps.json")
        suggestions = [
            disnake.OptionChoice(
                name=f"📡 {app['name']} - {app['id']}",
                value=app["id"]
            )
            for app in apps.values()
            if aplicacao.lower() in app["name"].lower()
        ]

        if not suggestions:
            return [
                disnake.OptionChoice(
                    name="❌ Nenhuma aplicação encontrada",
                    value="NO_APPLICATIONS"
                )
            ]

        return suggestions

def setup(bot):
    bot.add_cog(Status(bot))