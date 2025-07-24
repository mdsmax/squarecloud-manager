import disnake
from disnake.ext import commands
from database import Database
from functions.squarecloud import SquareCloud

class Config:
    @staticmethod
    def aplicacoes_builder(inter: disnake.MessageInteraction | None, id: str | None = None):
        aplicacoes = Database.obter("apps.json")
        user_apps = []
        for app in aplicacoes.values():
            if inter:
                if str(app["owner"]) == str(inter.user.id):
                    user_apps.append(app)
            elif id:
                if str(app["owner"]) == str(id):
                    user_apps.append(app)

        embed = disnake.Embed(
            title="Aplicações",
            description="Utilize este painel para configurar e gerenciar suas aplicações - você pode ver informações e gerenciar o estado delas.",
            color=disnake.Color.blurple()
        )
        embed.add_field(name="Aplicações", value=f"`{len(user_apps)}`", inline=True)

        if user_apps:
            options = [
                disnake.SelectOption(
                    label=app["name"],
                    description=f"Plano: {app['plano'].capitalize()} | ID: {app['id']}",
                    value=app["id"]
                )
                for app in user_apps
            ]
        else:
            options = [
                disnake.SelectOption(
                    label="Nenhuma aplicação encontrada",
                    description="Você não possui nenhuma aplicação",
                    value="Nenhuma aplicação encontrada"
                )
            ]

        components = [
            disnake.ui.StringSelect(
                placeholder=f"Selecione a aplicação que deseja configurar",
                options=options,
                custom_id="Painel_SelecionarAplicacao" if inter else "Config_AplicacoesUsuarios_Aplicacao",
                disabled=len(user_apps) == 0
            ),
            disnake.ui.Button(label="Voltar", custom_id="Painel_Voltar")
        ]

        return embed, components

    class Aplicacao:
        @staticmethod
        async def aplicacao_builder(inter: disnake.MessageInteraction, id: str = None, loading: bool = False, config: bool = False):
            aplicacoes = Database.obter("apps.json")
            user_apps = []
            for app in aplicacoes.values():
                if str(app["owner"]) == str(inter.user.id):
                    user_apps.append(app)

            app = aplicacoes[id]
            
            embed = disnake.Embed(
                title=f"Configurar aplicação — {app['name']}",
                description="Utilize este painel para configurar e gerenciar essa aplicação - você pode ver informações e gerenciar o estado dela.",
                color=disnake.Color.blurple()
            )
            embed.add_field(name="Nome da aplicação", value=f"`{app['name']}`", inline=True)
            embed.add_field(name="Plano", value=f"`{app['plano'].capitalize()}`", inline=True)
            embed.add_field(name="ID da aplicação", value=f"`{app['id']}`", inline=True)
            app_status = None
            try:
                app_status = await SquareCloud.get_bot_status(app["id"])
                if app_status.running or app_status.exited: embed.add_field(name="Status da aplicação", value=f"`{'Ligada' if app_status.running else 'Desligada'}`", inline=True)
                if app_status.cpu: embed.add_field(name="CPU", value=f"`{app_status.cpu}`", inline=True)
                if app_status.ram: embed.add_field(name="RAM", value=f"`{app_status.ram}`", inline=True)
                if app_status.uptime: embed.add_field(name="Uptime", value=f"<t:{app_status.uptime // 1000}:R> (<t:{app_status.uptime // 1000}:f>)", inline=False)
                if app_status.network['now']: embed.add_field(name="Rede (agora)", value=f"`{app_status.network['now']}`", inline=True)
                if app_status.storage: embed.add_field(name="Armazenamento", value=f"`{app_status.storage}`", inline=True)

            except Exception:
                if app_status.running != bool:
                    embed.add_field(name="Status da aplicação", value=f"`Não encontrado`", inline=True)
                if not app_status.cpu:
                    embed.add_field(name="CPU", value=f"`Não encontrado`", inline=True)
                if not app_status.ram:
                    embed.add_field(name="RAM", value=f"`Não encontrado`", inline=True)
                if not app_status.uptime:
                    embed.add_field(name="Uptime", value=f"`Não encontrado`", inline=True)
                if not app_status.network['now']:
                    embed.add_field(name="Rede (agora)", value=f"`Não encontrado`", inline=True)
                if not app_status.storage:
                    embed.add_field(name="Armazenamento", value=f"`Não encontrado`", inline=True)

            if app_status:
                button_gerenciarstatus = {
                    "label": "Ligar aplicação" if not app_status.running else "Desligar aplicação",
                    "style": disnake.ButtonStyle.green if not app_status.running else disnake.ButtonStyle.red,
                    "custom_id": f"Painel_LigarDesligarAplicacao_{app['id']}" if not config else f"Config_AplicacoesUsuarios_LigarDesligarAplicacao_{app['id']}",
                    "disabled": loading
                }
            else:
                embed.add_field(name="Informação da aplicação", value=f"A aplicação não foi encontrada na SquareCloud. Se isso for um erro, contate o suporte e informe o ID da aplicação: `{app['id']}`", inline=False)
                button_gerenciarstatus = {
                    "label": "Ligar aplicação",
                    "style": disnake.ButtonStyle.green,
                    "disabled": True
                }

            components = [
                disnake.ui.StringSelect(
                    placeholder=f"Selecione a aplicação que deseja configurar",
                    options=[
                        disnake.SelectOption(label=app["name"], description=f"Plano: {app['plano'].capitalize()} | ID: {app['id']}", value=app["id"], default=True if app["id"] == id else False)
                        for app in aplicacoes.values()
                    ],
                    custom_id="Painel_SelecionarAplicacao"
                ),
                disnake.ui.Button(**button_gerenciarstatus),
                disnake.ui.Button(label="Reiniciar aplicação", style=disnake.ButtonStyle.blurple, custom_id=f"Painel_ReiniciarAplicacao_{app['id']}" if not config else f"Config_AplicacoesUsuarios_ReiniciarAplicacao_{app['id']}", disabled=True if loading or not app_status else False),
                disnake.ui.Button(label="Voltar", custom_id="Painel_ConfigurarAplicacoes")
            ]

            if config:
                components.pop(0)
                components.pop(2)
                components.append(
                    disnake.ui.Button(label="Excluir aplicação", style=disnake.ButtonStyle.red, custom_id=f"Config_AplicacoesUsuarios_DeletarAplicacao_{id}", disabled=loading),
                )
                components.append(
                    disnake.ui.Button(label="Voltar", custom_id="Config_AplicacoesUsuarios")
                )
                embed.add_field(name="Dono da aplicação", value=f"<@{app['owner']}>", inline=True)

            return embed, components

class ConfigExtension(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener("on_button_click")
    async def on_button_click(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "Painel_ConfigurarAplicacoes":
            embed, components = Config.aplicacoes_builder(inter)
            await inter.response.edit_message(embed=embed, components=components)

        elif inter.component.custom_id.startswith("Painel_LigarDesligarAplicacao_"):
            app_id = inter.component.custom_id.replace("Painel_LigarDesligarAplicacao_", "")
            embed, components = await Config.Aplicacao.aplicacao_builder(inter, app_id, loading=True)
            await inter.response.edit_message(embed=embed, components=components)

            try:
                status = await SquareCloud.get_bot_status(app_id)
                if status.running:
                    await SquareCloud.stop_bot(app_id)
                else:
                    await SquareCloud.start_bot(app_id)
            except: pass

            embed, components = await Config.Aplicacao.aplicacao_builder(inter, app_id)
            await inter.edit_original_message(embed=embed, components=components)
        
        elif inter.component.custom_id.startswith("Painel_ReiniciarAplicacao_"):
            app_id = inter.component.custom_id.replace("Painel_ReiniciarAplicacao_", "")
            embed, components = await Config.Aplicacao.aplicacao_builder(inter, app_id, loading=True)
            await inter.response.edit_message(embed=embed, components=components)

            try: await SquareCloud.restart_bot(app_id)
            except: pass

            embed, components = await Config.Aplicacao.aplicacao_builder(inter, app_id)
            await inter.edit_original_message(embed=embed, components=components)

    @commands.Cog.listener("on_dropdown")
    async def on_dropdown(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "Painel_SelecionarAplicacao":
            embed, components = await Config.Aplicacao.aplicacao_builder(inter, inter.values[0])
            await inter.response.edit_message(embed=embed, components=components)

def setup(bot):
    bot.add_cog(ConfigExtension(bot))