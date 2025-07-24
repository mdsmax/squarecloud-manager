import disnake
from disnake import *
from disnake.ext import commands
from database import Database
from commands.extensions.painel.config import Config
from functions.squarecloud import SquareCloud

class Apps:
    PAGE_LIMIT = 25

    class ProcurarAplicacao(disnake.ui.Modal):
        def __init__(self):
            super().__init__(
                title="Procurar aplicação",
                custom_id="Config_AplicacoesUsuarios_ProcurarAplicacao",
                components=[
                    disnake.ui.TextInput(
                        label="ID da aplicação",
                        custom_id="appID",
                        placeholder="Digite o ID da aplicação",
                        required=True
                    )
                ]
            )
        
        async def callback(self, inter: disnake.ModalInteraction):
            id = inter.text_values["appID"]
            if id in Database.obter("apps.json"):
                embed, components = await Apps.GerenciarAplicacao.aplicacao_builder(inter, id)
                await inter.response.edit_message(embed=embed, components=components)
            else:
                await inter.response.send_message("Aplicação não encontrada", ephemeral=True)

    @staticmethod
    def aplicacoes_usuarios_builder(inter: disnake.MessageInteraction, pagina: int = 0):
        aplicacoes = list(Database.obter("apps.json").values())
        total_paginas = (len(aplicacoes) - 1) // Apps.PAGE_LIMIT + 1

        inicio = pagina * Apps.PAGE_LIMIT
        fim = inicio + Apps.PAGE_LIMIT
        aplicacoes_pagina = aplicacoes[inicio:fim]

        embed = disnake.Embed(
            title="Aplicações e usuários",
            description=(
                "Utilize os botões abaixo para configurar e gerenciar as aplicações registradas na SquareCloud e seus clientes.\n"
                "Utilize o Select Menu abaixo para selecionar uma aplicação ou um cliente."
            ),
            color=disnake.Color.blurple(),
            timestamp=disnake.utils.utcnow()
        )

        options = []
        for app in aplicacoes_pagina:
            options.append(
                disnake.SelectOption(
                    label=app["name"],
                    description=f"Plano: {app['plano'].capitalize()} | ID: {app['id']}",
                    value=app["id"]
                )
            )
        
        if not options:
            options.append(
                disnake.SelectOption(
                    label="Nenhuma aplicação encontrada",
                    description="Nenhuma aplicação encontrada",
                    value="Nenhuma aplicação encontrada"
                )
            )

        select_app = disnake.ui.StringSelect(
            placeholder=f"Página {pagina + 1}/{total_paginas} - Selecione uma aplicação",
            custom_id=f"Config_AplicacoesUsuarios_Aplicacao",
            disabled=len(aplicacoes_pagina) == 0,
            options=options,
        )

        components = [
            [
                select_app,
            ],
            [
                disnake.ui.Button(
                    emoji="◀️",
                    custom_id=f"Config_AplicacoesUsuarios_Voltar_{pagina}",
                    disabled=(pagina == 0)
                ),
                disnake.ui.Button(
                    emoji="🔎",
                    custom_id="Config_AplicacoesUsuarios_Pesquisar",
                    disabled=len(aplicacoes_pagina) == 0
                ),
                disnake.ui.Button(
                    emoji="▶️",
                    custom_id=f"Config_AplicacoesUsuarios_Avancar_{pagina}",
                    disabled=(pagina >= total_paginas - 1)
                )
            ],
            [
                disnake.ui.UserSelect(
                    placeholder="Selecione um cliente para gerenciar",
                    custom_id="Config_AplicacoesUsuarios_Cliente"
                ),
            ],
            disnake.ui.Button(label="Voltar", custom_id="Config_Voltar")
        ]

        return embed, components

    class GerenciarAplicacao:
        @staticmethod
        async def aplicacao_builder(inter: disnake.MessageInteraction, id: str):
            aplicacao = Database.obter("apps.json")[id]
            embed, components = await Config.Aplicacao.aplicacao_builder(inter, id, config=True)

            return embed, components
    
    class GerenciarCliente:
        @staticmethod
        async def cliente_builder(inter: disnake.MessageInteraction, id: str):
            embed, components = Config.aplicacoes_builder(None, id)
            components.pop(1)
            components.append([
                disnake.ui.Button(label="Voltar", custom_id="Config_AplicacoesUsuarios")
            ])
            return embed, components

class AppsExtension(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener("on_button_click")
    async def on_button_click(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "Config_AplicacoesUsuarios":
            embed, components = Apps.aplicacoes_usuarios_builder(inter)
            await inter.response.edit_message(embed=embed, components=components)

        elif inter.component.custom_id.startswith("Config_AplicacoesUsuarios_Voltar_"):
            pagina_atual = int(inter.component.custom_id.split("_")[-1])
            nova_pagina = pagina_atual - 1
            embed, components = Apps.aplicacoes_usuarios_builder(inter, nova_pagina)
            await inter.response.edit_message(embed=embed, components=components)

        elif inter.component.custom_id.startswith("Config_AplicacoesUsuarios_Avancar_"):
            pagina_atual = int(inter.component.custom_id.split("_")[-1])
            nova_pagina = pagina_atual + 1
            embed, components = Apps.aplicacoes_usuarios_builder(inter, nova_pagina)
            await inter.response.edit_message(embed=embed, components=components)

        elif inter.component.custom_id.startswith("Config_AplicacoesUsuarios_DeletarAplicacao_"):
            id = inter.component.custom_id.replace("Config_AplicacoesUsuarios_DeletarAplicacao_", "")
            aplicacoes = Database.obter("apps.json")
            aplicacoes.pop(id)
            Database.salvar("apps.json", aplicacoes)

            services = Database.obter("services.json")
            for service in services.values():
                if id in service["apps"]["id_list"]:
                    service["apps"]["id_list"].remove(id)
                    break
            Database.salvar("services.json", services)

            try: await SquareCloud.delete_bot(id)
            except: pass
   
            embed, components = Apps.aplicacoes_usuarios_builder(inter)
            await inter.response.edit_message(embed=embed, components=components)

        elif inter.component.custom_id == "Config_AplicacoesUsuarios_Pesquisar":
            await inter.response.send_modal(Apps.ProcurarAplicacao())
        
        elif inter.component.custom_id.startswith("Config_AplicacoesUsuarios_LigarDesligarAplicacao_"):
            app_id = inter.component.custom_id.replace("Config_AplicacoesUsuarios_LigarDesligarAplicacao_", "")
            embed, components = await Config.Aplicacao.aplicacao_builder(inter, app_id, loading=True, config=True)
            await inter.response.edit_message(embed=embed, components=components)

            status = await SquareCloud.get_bot_status(app_id)
            if status.running:
                await SquareCloud.stop_bot(app_id)
            else:
                await SquareCloud.start_bot(app_id)
            
            embed, components = await Config.Aplicacao.aplicacao_builder(inter, app_id, config=True)
            await inter.edit_original_message(embed=embed, components=components)
        
        elif inter.component.custom_id.startswith("Config_AplicacoesUsuarios_ReiniciarAplicacao_"):
            app_id = inter.component.custom_id.replace("Config_AplicacoesUsuarios_ReiniciarAplicacao_", "")
            embed, components = await Config.Aplicacao.aplicacao_builder(inter, app_id, loading=True, config=True)
            await inter.response.edit_message(embed=embed, components=components)

            await SquareCloud.restart_bot(app_id)
            embed, components = await Config.Aplicacao.aplicacao_builder(inter, app_id, config=True)
            await inter.edit_original_message(embed=embed, components=components)

    @commands.Cog.listener("on_dropdown")
    async def on_dropdown(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id.startswith("Config_AplicacoesUsuarios_Aplicacao"):
            id = inter.values[0]
            embed, components = await Apps.GerenciarAplicacao.aplicacao_builder(inter, id)
            await inter.response.edit_message(embed=embed, components=components)

        elif inter.component.custom_id == "Config_AplicacoesUsuarios_Cliente":
            id = str(inter.values[0])
            embed, components = await Apps.GerenciarCliente.cliente_builder(inter, id)
            await inter.response.edit_message(embed=embed, components=components)

def setup(bot):
    bot.add_cog(AppsExtension(bot)) 