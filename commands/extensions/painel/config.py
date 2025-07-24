import disnake
from disnake.ext import commands
from database import Database

class Config:
    @staticmethod
    def aplicacoes_builder(inter: disnake.MessageInteraction):
        aplicacoes = Database.obter("apps.json")
        user_apps = []
        for app in aplicacoes.values():
            if str(app["owner"]) == str(inter.user.id):
                user_apps.append(app)

        embed = disnake.Embed(
            title="Aplicações",
            description="Utilize este painel para configurar e gerenciar suas aplicações - você pode ver informações e gerenciar o estado delas.",
            color=disnake.Color.blurple()
        )
        embed.add_field(name="Aplicações", value=f"`{len(user_apps)}`", inline=True)

        components = [
            disnake.ui.StringSelect(
                placeholder=f"Selecione a aplicação que deseja configurar",
                options=[
                    disnake.SelectOption(label=app["name"], description=f"Plano: {app['plano'].capitalize()} | ID: {app['id']}", value=app["id"])
                    for app in user_apps
                ],
                custom_id="Painel_SelecionarAplicacao"
            ),
            disnake.ui.Button(label="Voltar", custom_id="Painel_Voltar")
        ]

        return embed, components

class ConfigExtension(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener("on_button_click")
    async def on_button_click(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "Painel_ConfigurarAplicacoes":
            embed, components = Config.aplicacoes_builder(inter)
            await inter.response.edit_message(embed=embed, components=components)

    @commands.Cog.listener("on_dropdown")
    async def on_dropdown(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "Painel_SelecionarAplicacao":
            await inter.response.send_message(f"Aplicação selecionada: {inter.values[0]}")

def setup(bot):
    bot.add_cog(ConfigExtension(bot))