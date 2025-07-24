import disnake
from disnake.ext import commands

from functions.squarecloud import SquareCloud
from functions.perms import Perms
from database import Database

class Builder:
    def __init__(self, inter: disnake.ApplicationCommandInteraction):
        self.inter = inter
    
    async def build(self):
        account_informations = await SquareCloud.get_account_informations()
        clients = Database.obter("clientes.json")
        plan = account_informations['plan']
        memory_used = plan['memory']['used']
        memory_limit = plan['memory']['limit']
        memory_percent = (memory_used / memory_limit) * 100 if memory_limit else 0
        memory_percent_str = f"{memory_percent:.1f}%"

        embed = disnake.Embed(
            title="Configurações",
            description=(
                f"Bem-vindo ao painel de controle, {self.inter.author.mention}!\n"
                "Utilize os botões abaixo para configurar e gerenciar seus serviços e clientes."
            ),
            color=disnake.Color.blurple(),
            timestamp=disnake.utils.utcnow()
        )
        embed.add_field(name="Plano", value=f"`{plan['name'].capitalize()}`", inline=True)
        embed.add_field(name="RAM utilizada", value=f"`{memory_used}/{memory_limit} MB ({memory_percent_str})`", inline=True)
        embed.add_field(name="Informações", value=f"`{account_informations['apps']} aplicações` | `{len(clients)} clientes` | `{len(Database.obter('services.json'))} planos`", inline=True)
        embed.add_field(name="Email", value=f"||`{account_informations['email']}`||", inline=True)
        embed.add_field(name="ID do usuário", value=f"||`{account_informations['user_id']}`||", inline=True)

        components = [
            disnake.ui.Button(label="Planos e arquivos", style=disnake.ButtonStyle.blurple, custom_id="Config_PlanosArquivos"),
            disnake.ui.Button(label="Aplicações e usuários", style=disnake.ButtonStyle.blurple, custom_id="Config_AplicacoesUsuarios"),
            disnake.ui.Button(label="Rendimentos", style=disnake.ButtonStyle.green, custom_id="Config_Rendimentos"),
        ]

        return embed, components


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="configurações", description="[DEV] Configure as aplicações, serviços e usuários registrados")
    async def config(self, inter: disnake.ApplicationCommandInteraction):
        if not Perms.is_owner(inter):
            return await inter.response.send_message("Você não tem permissão para acessar o painel de controle", ephemeral=True)

        embed, components = await Builder(inter).build()
        await inter.response.send_message(embed=embed, components=components, ephemeral=True)

    @commands.Cog.listener("on_button_click")
    async def on_button_click(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "Config_Voltar":
            embed, components = await Builder(inter).build()
            await inter.response.edit_message(embed=embed, components=components)

def setup(bot):
    bot.add_cog(Config(bot))