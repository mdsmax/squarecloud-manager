import disnake
from disnake.ext import commands

from functions.squarecloud import SquareCloud
from functions.perms import Perms
from database import Database

class Builder:
    def __init__(self, inter: disnake.ApplicationCommandInteraction):
        self.inter = inter
    
    async def build(self):
        apps = Database.obter("apps.json")
        clients = Database.obter("clientes.json")
        user_apps = []
        for app in apps:
            if str(app["owner"]) == str(self.inter.user.id):
                user_apps.append(app)

        embed = disnake.Embed(
            title="Painel de controle",
            description=f"""
Seja bem-vindo ao painel de controle, {self.inter.user.mention}!
Utilize os botões abaixo para configurar ou comprar serviços.
            """,
            color=disnake.Color.blurple(),
            timestamp=disnake.utils.utcnow()
        )
        embed.add_field(name="Aplicações", value=f"`{len(user_apps)}`", inline=True)
        embed.add_field(name="ID do usuário", value=f"`{self.inter.user.id}`", inline=True)

        components = [
            disnake.ui.Button(label="Comprar serviços", style=disnake.ButtonStyle.blurple, custom_id="Painel_ComprarServicos"),
            disnake.ui.Button(label="Configurar suas aplicações", style=disnake.ButtonStyle.grey, custom_id="Painel_ConfigurarAplicacoes"),
        ]

        return embed, components


class Painel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="painel", description="Acesse o painel de controle para gerenciar e comprar serviços")
    @Perms.owner_only()
    async def painel(self, inter: disnake.ApplicationCommandInteraction):
        # coloquei essa verificação apenas como precaução
        if not Perms.is_owner(inter):
            return await inter.response.send_message("Você não tem permissão para acessar o painel de controle", ephemeral=True)
        
        embed, components = await Builder(inter).build()
        await inter.response.send_message(embed=embed, components=components, ephemeral=True)

def setup(bot):
    bot.add_cog(Painel(bot))