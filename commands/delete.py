import disnake
from disnake.ext import commands
from functions.perms import Perms
from database import Database
from functions.squarecloud import SquareCloud

class Delete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="deletar", description="[DEV] Deletar uma aplicação na SquareCloud e no banco de dados")
    async def delete(
        self,
        inter: disnake.ApplicationCommandInteraction,
        aplicacao: str = commands.Param(description="Aplicação a ser deletada", autocomplete=True),
    ):
        if not Perms.is_owner(inter):
            return await inter.response.send_message("Faltam permissões para acessar este comando", ephemeral=True)

        if aplicacao == "MISSING_PERMISSIONS":
            return await inter.response.send_message("Faltam permissões para acessar este comando", ephemeral=True)

        if aplicacao == "NO_APPLICATION":
            return await inter.response.send_message("Nenhuma aplicação encontrada no banco de dados", ephemeral=True)

        apps = Database.obter("apps.json")
        app = apps[aplicacao]
        try: await SquareCloud.delete_bot(app["id"])
        except: pass

        apps.pop(aplicacao)
        Database.salvar("apps.json", apps)

        await inter.response.send_message(f"Aplicação `{app['name']} - {app['id']}` deletada com sucesso do banco de dados e da SquareCloud", ephemeral=True)
    
    @delete.autocomplete("aplicacao")
    async def delete_autocomplete(self, inter: disnake.ApplicationCommandInteraction, aplicacao: str):
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
                    value="NO_APPLICATION"
                )
            ]

        return suggestions

def setup(bot):
    bot.add_cog(Delete(bot))