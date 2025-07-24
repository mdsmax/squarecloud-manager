import disnake
from disnake.ext import commands
from database import Database
from functions.squarecloud import SquareCloud

class Rendimentos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener("on_button_click")
    async def on_button_click(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "Config_Rendimentos":
            valor_total = 0.0
            account_informations = await SquareCloud.get_account_informations()
            apps = Database.obter("apps.json")
            for app in apps.values():
                if app["price"]:
                    valor_total += app["price"]

            embed = disnake.Embed(
                title="Rendimentos",
                description="Utilize este painel para visualizar as informações sobre os rendimentos da plataforma. Todos os valores são em reais (R$).",
                color=disnake.Color.blurple()
            )
            embed.add_field(name="Valor total vendido", value=f"`R${valor_total:.2f}`", inline=True)
            embed.add_field(name="Informações gerais", value=f"`{len(apps)} aplicações` | `{len(Database.obter('clientes.json'))} clientes` | `{len(Database.obter('services.json'))} planos`", inline=True)
            embed.add_field(name="Informações da SquareCloud", value=f"Na SquareCloud, você possui `{account_informations['apps']}` aplicações. Acesse a [Dashboard](https://squarecloud.app/dashboard/) para gerenciar suas aplicações.", inline=False)

            await inter.response.send_message(embed=embed, ephemeral=True)
    
def setup(bot):
    bot.add_cog(Rendimentos(bot))