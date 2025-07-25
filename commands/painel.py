import disnake
from disnake.ext import commands
from database import Database

class Builder:
    def __init__(self, inter: disnake.ApplicationCommandInteraction):
        self.inter = inter
    
    async def build(self):
        apps = Database.obter("apps.json")
        services = Database.obter("services.json")
        user_apps = []
        for app in apps.values():
            if str(app["owner"]) == str(self.inter.user.id):
                user_apps.append(app)

        embed = disnake.Embed(
            title="Painel de controle",
            description=f"""
Prezado(a) {self.inter.user.mention}, seja bem-vindo(a) ao painel de controle.
Através dos botões abaixo, você poderá configurar e adquirir os serviços disponíveis. Todos os serviços são hospedados 24 horas por dia pela plataforma [SquareCloud](https://squarecloud.app).
            """,
            color=disnake.Color.blurple(),
            timestamp=disnake.utils.utcnow()
        )
        embed.add_field(name="Aplicações", value=f"`{len(user_apps)}`", inline=True)
        embed.add_field(name="ID do usuário", value=f"`{self.inter.user.id}`", inline=True)
        embed.add_field(name="Serviços disponíveis", value=f"`{len(services)}`", inline=True)

        components = [
            disnake.ui.Button(label="Comprar serviços", style=disnake.ButtonStyle.blurple, custom_id="Painel_ComprarServicos"),
            disnake.ui.Button(label="Configurar suas aplicações", style=disnake.ButtonStyle.grey, custom_id="Painel_ConfigurarAplicacoes"),
        ]

        return embed, components

class Painel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="painel", description="Acesse o painel de controle para gerenciar e comprar serviços")
    async def painel(self, inter: disnake.ApplicationCommandInteraction):
        embed, components = await Builder(inter).build()
        await inter.response.send_message(embed=embed, components=components, ephemeral=True)

    @commands.Cog.listener("on_button_click")
    async def on_button_click(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "Painel_Voltar":
            embed, components = await Builder(inter).build()
            await inter.response.edit_message(embed=embed, components=components)

def setup(bot):
    bot.add_cog(Painel(bot))