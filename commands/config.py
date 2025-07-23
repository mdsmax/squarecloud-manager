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
        memory_available = memory_limit - memory_used

        embed = disnake.Embed(
            title="Painel de controle",
            description=f"Bem-vindo ao painel de controle, {self.inter.author.mention}!",
            color=disnake.Color.blurple(),
            timestamp=disnake.utils.utcnow()
        )
        embed.add_field(name="Plano", value=f"`{plan['name'].capitalize()}`", inline=True)
        embed.add_field(name="RAM utilizada", value=f"`{memory_used}/{memory_limit} MB ({memory_percent_str} - Disponível: {memory_available} MB)`", inline=True)
        embed.add_field(name="Informações", value=f"`{account_informations['apps']} aplicações`\n`{len(clients)} clientes`", inline=True)
        embed.add_field(name="Email", value=f"`{account_informations['email']}`", inline=True)
        embed.add_field(name="ID do usuário", value=f"`{account_informations['user_id']}`", inline=True)

        components = [
            disnake.ui.Button(label="Planos e arquivos", style=disnake.ButtonStyle.blurple, custom_id="Config_PlanosArquivos"),
            disnake.ui.Button(label="Aplicações e usuários", style=disnake.ButtonStyle.blurple, custom_id="Config_AplicacoesUsuarios"),
            disnake.ui.Button(label="Rendimentos", style=disnake.ButtonStyle.green, custom_id="Config_Rendimentos"),
        ]

        return embed, components


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="config", description="[DEV] Configure as aplicações, serviços e usuários registrados")
    async def config(self, inter: disnake.ApplicationCommandInteraction):
        embed, components = await Builder(inter).build()
        await inter.response.send_message(embed=embed, components=components, ephemeral=True)

def setup(bot):
    bot.add_cog(Config(bot))