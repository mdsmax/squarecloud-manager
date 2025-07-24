import os
import asyncio
import disnake
from disnake.ext import commands
from database import Database
from commands.extensions.painel.services import Services
from functions.gerar_codigo import GerarCodigo
from functions.cleanup import limpar_temp
from functions.zip import Zip

class Plans:
    plano_modal_components = lambda plano=None: [
        disnake.ui.TextInput(label="Nome do plano", custom_id="name", style=disnake.TextInputStyle.short, value=(plano or {}).get("name", "")),
        disnake.ui.TextInput(label="Descrição do plano", custom_id="description", style=disnake.TextInputStyle.long, required=False, value=(plano or {}).get("description", "")),
        disnake.ui.TextInput(label="Pré-descrição do plano", custom_id="pre-description", max_length=100, required=False, style=disnake.TextInputStyle.long, value=(plano or {}).get("pre-description", "")),
        disnake.ui.TextInput(label="Preço do plano", placeholder="Exemplo: 10.00 -> R$10,00", custom_id="price", style=disnake.TextInputStyle.short, value=(plano or {}).get("price", "")),
    ]

    @staticmethod
    def validar_preco(price):
        try:
            price = float(price)
            if price < 0:
                raise ValueError
            return "{:.2f}".format(price)
        except ValueError:
            return None

    @staticmethod
    def plans_builder(inter: disnake.MessageInteraction):
        services = Database.obter("services.json")
        embed = disnake.Embed(
            title="Planos disponíveis",
            description="Selecione o plano que deseja configurar/editar no Select Menu. Se quiser, pode criar um novo plano no botão abaixo.",
            color=disnake.Color.blurple()
        )
        embed.add_field(name="Planos disponíveis", value=f"`{len(services)}`", inline=False)
        embed.add_field(name="Informação adicional", value="Se você quiser deixar um bot gratuito e não pular a parte do pagamento com Mercado Pago, basta configurar o plano com o preço `0`", inline=False)
        options = [
            disnake.SelectOption(
                label=s["name"],
                description=f"R$ {float(s['price']):.2f}".replace('.', ',') + f" | {s['pre-description']}",
                value=s["id"]
            ) for s in services.values()
        ] or [disnake.SelectOption(label="Nenhum plano disponível")]
        components = [
            disnake.ui.StringSelect(
                placeholder=f"[{len(services)}] Selecione o plano que deseja configurar/editar",
                options=options,
                custom_id="Config_SelecionarPlano",
                disabled=not bool(services)
            ),
            disnake.ui.Button(label="Criar novo plano", style=disnake.ButtonStyle.green, custom_id="Config_CriarPlano"),
            disnake.ui.Button(label="Voltar", custom_id="Config_Voltar")
        ]
        return embed, components

    class CriarPlano(disnake.ui.Modal):
        def __init__(self):
            super().__init__(
                title="Criar novo plano",
                custom_id="Config_CriarPlano",
                components=Plans.plano_modal_components()
            )

        async def callback(self, inter: disnake.ModalInteraction):
            name = inter.text_values["name"]
            description = inter.text_values.get("description") or "Nenhuma descrição disponível"
            pre_description = inter.text_values.get("pre-description") or "Nenhuma pré-descrição disponível"
            price = Plans.validar_preco(inter.text_values["price"])
            if not price:
                await inter.response.send_message("O preço do plano deve ser um número válido e maior que 0", ephemeral=True)
                return
            price = float(price)
            id = GerarCodigo()
            planos = Database.obter("services.json")
            planos[id] = {
                "id": id,
                "name": name,
                "description": description,
                "pre-description": pre_description,
                "price": price,
                "apps": {"id_list": [], "filename": ""}
            }
            Database.salvar("services.json", planos)
            embed, components = Plans.plans_builder(inter)
            await inter.response.edit_message(embed=embed, components=components)
    
    class GerenciarPlano:
        class EditarPlano(disnake.ui.Modal):
            def __init__(self, id: str):
                self.id = id
                plano = Database.obter("services.json")[id]
                super().__init__(
                    title="Editar plano",
                    custom_id=f"Config_EditarPlano_{id}",
                    components=Plans.plano_modal_components(plano)
                )
            
            async def callback(self, inter: disnake.ModalInteraction):
                name = inter.text_values["name"]
                description = inter.text_values.get("description") or "Nenhuma descrição disponível"
                pre_description = inter.text_values.get("pre-description") or "Nenhuma pré-descrição disponível"
                price = Plans.validar_preco(inter.text_values["price"])
                if not price:
                    await inter.response.send_message("O preço do plano deve ser um número válido e maior que 0", ephemeral=True)
                    return
                price = float(price)
                id = self.id
                planos = Database.obter("services.json")
                planos[id].update({
                    "id": id,
                    "name": name,
                    "description": description,
                    "pre-description": pre_description,
                    "price": price
                })
                Database.salvar("services.json", planos)
                embed, components = Plans.GerenciarPlano.gerenciar_plano_builder(inter, id)
                await inter.response.edit_message(embed=embed, components=components)

        @staticmethod
        def gerenciar_plano_builder(inter: disnake.MessageInteraction, id: str):
            planos = Database.obter("services.json")
            plano = planos[id]
            embed = disnake.Embed(
                title=f"Gerenciar plano — {plano['name']}",
                description=(
                    f"Utilize este painel para configurar e gerenciar o plano, além de configurar os arquivos que serão usados para criar as aplicações.\n\n"
                    f"**Descrição do plano**\n```{plano['description']}```\n**Pré-descrição**\n```{plano['pre-description']}```"
                ),
                color=disnake.Color.blurple()
            )
            embed.add_field(name="Preço (mensal) do plano", value=f"`R$ {float(plano['price']):.2f}`".replace('.', ','), inline=True)
            embed.add_field(name="Aplicações registradas no plano", value=f"`{len(plano['apps']['id_list'])}`", inline=True)
            embed.add_field(name="Arquivo disponível", value=f"`{'Sim' if plano['apps']['filename'] else 'Não'}`", inline=True)
            components = [
                [
                    disnake.ui.Button(label="Editar plano", custom_id=f"Config_EditarPlano_{id}"),
                    disnake.ui.Button(label="Apagar plano", style=disnake.ButtonStyle.red, custom_id=f"Config_DeletarPlano_{id}"),
                    disnake.ui.Button(label="Configurar arquivos", style=disnake.ButtonStyle.blurple, custom_id=f"Config_ConfigurarArquivos_{id}"),
                ],
                [
                    disnake.ui.Button(label="Enviar mensagem para compra", style=disnake.ButtonStyle.green, custom_id=f"Config_EnviarMensagemCompra_{id}"),
                    disnake.ui.Button(label="Voltar", custom_id="Config_PlanosArquivos")
                ]
            ]
            return embed, components
        
        @staticmethod
        def deletar_plano(inter: disnake.MessageInteraction, id: str):
            planos = Database.obter("services.json")
            Plans.GerenciarPlano.ConfigurarArquivos.remover_arquivo(id)
            del planos[id]
            Database.salvar("services.json", planos)

        class ConfigurarArquivos:
            @staticmethod
            def configurar_arquivos_builder(inter: disnake.MessageInteraction, id: str):
                planos = Database.obter("services.json")
                arquivo = planos[id]["apps"]["filename"]
                embed = disnake.Embed(
                    title=f"Configurar arquivos do plano — {planos[id]['name']}",
                    description="Utilize este painel para configurar o arquivo que será usado para criar as aplicações quando o plano for selecionado.",
                    color=disnake.Color.blurple()
                )
                embed.add_field(name="Arquivo disponível", value=f"`{'Sim' if arquivo else 'Não'}`", inline=False)
                components = [
                    disnake.ui.Button(label="Adicionar arquivo" if not arquivo else "Reenviar arquivo", style=disnake.ButtonStyle.blurple, custom_id=f"Config_AdicionarArquivo_{id}"),
                    disnake.ui.Button(label="Remover arquivo", style=disnake.ButtonStyle.red, custom_id=f"Config_RemoverArquivo_{id}", disabled=not bool(arquivo)),
                    disnake.ui.Button(label="Voltar", custom_id=f"Config_GerenciarPlano_{id}")
                ]
                return embed, components
            
            @staticmethod
            def remover_arquivo(id: str):
                planos = Database.obter("services.json")
                filename = planos[id]["apps"]["filename"]
                if filename and os.path.exists(f"database/apps/{filename}"):
                    os.remove(f"database/apps/{filename}")
                planos[id]["apps"]["filename"] = ""
                Database.salvar("services.json", planos)

            @staticmethod
            async def adicionar_arquivo(bot, inter: disnake.MessageInteraction, id: str):
                await inter.response.edit_message(f"Envie em `120` segundos o arquivo que deseja adicionar ao plano.", embed=None, components=None)
                try:
                    msg = await bot.wait_for("message", timeout=120, check=lambda m: m.author == inter.author and m.channel == inter.channel)
                except asyncio.TimeoutError:
                    await inter.followup.send("Tempo esgotado, tente novamente.", ephemeral=True)
                    embed, components = Plans.GerenciarPlano.ConfigurarArquivos.configurar_arquivos_builder(inter, id)
                    await inter.edit_original_message("", embed=embed, components=components)
                    return
                
                if msg.attachments:
                    try:
                        file = msg.attachments[0]
                        if file.filename.endswith(".zip"):
                            filename = f".temp/{id}-{file.filename}"
                            await file.save(filename)
                            await msg.delete()
                            pasta = Zip.descompactar(filename, f".temp/{id}-{file.filename.split('.')[0]}")
                            if Zip.verify_squarecloud_config(pasta):
                                await asyncio.sleep(3)
                                try: os.rename(filename, f"sources/{id}.zip")
                                except: pass

                                planos = Database.obter("services.json")
                                planos[id]["apps"]["filename"] = f"sources/{id}.zip"
                                Database.salvar("services.json", planos)

                                embed, components = Plans.GerenciarPlano.ConfigurarArquivos.configurar_arquivos_builder(inter, id)
                                await inter.edit_original_message("", embed=embed, components=components)

                                return
                            else:
                                limpar_temp()
                                await inter.followup.send("O arquivo `.zip` não possui um arquivo de configuração da SquareCloud válido.", ephemeral=True)
                                embed, components = Plans.GerenciarPlano.ConfigurarArquivos.configurar_arquivos_builder(inter, id)
                                await inter.edit_original_message("", embed=embed, components=components)
                                return
                            
                    except Exception as e:
                        limpar_temp()
                        print(e)
                        
                        await inter.followup.send(
                            content=f"Ocorreu um erro ao adicionar o arquivo. Tente novamente enviando um arquivo `.zip` válido.",
                            ephemeral=True
                        )
                        embed, components = Plans.GerenciarPlano.ConfigurarArquivos.configurar_arquivos_builder(inter, id)
                        await inter.edit_original_message("", embed=embed, components=components)
                        return

class PlansExtension(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_button_click")
    async def on_button_click(self, inter: disnake.MessageInteraction):
        cid = inter.component.custom_id
        if cid == "Config_PlanosArquivos":
            embed, components = Plans.plans_builder(inter)
            await inter.response.edit_message(embed=embed, components=components)
        elif cid == "Config_CriarPlano":
            await inter.response.send_modal(Plans.CriarPlano())
        elif cid.startswith("Config_EditarPlano_"):
            id = cid.split("_")[2]
            await inter.response.send_modal(Plans.GerenciarPlano.EditarPlano(id))
        elif cid.startswith("Config_DeletarPlano_"):
            id = cid.split("_")[2]
            Plans.GerenciarPlano.deletar_plano(inter, id)
            embed, components = Plans.plans_builder(inter)
            await inter.response.edit_message(embed=embed, components=components)
        elif cid.startswith("Config_GerenciarPlano_"):
            id = cid.split("_")[2]
            embed, components = Plans.GerenciarPlano.gerenciar_plano_builder(inter, id)
            await inter.response.edit_message(embed=embed, components=components)
        elif cid.startswith("Config_AdicionarArquivo_"):
            id = cid.split("_")[2]
            await Plans.GerenciarPlano.ConfigurarArquivos.adicionar_arquivo(self.bot, inter, id)
        elif cid.startswith("Config_RemoverArquivo_"):
            id = cid.split("_")[2]
            Plans.GerenciarPlano.ConfigurarArquivos.remover_arquivo(id)
            embed, components = Plans.GerenciarPlano.ConfigurarArquivos.configurar_arquivos_builder(inter, id)
            await inter.response.edit_message(embed=embed, components=components)
        elif cid.startswith("Config_ConfigurarArquivos_"):
            id = cid.split("_")[2]
            embed, components = Plans.GerenciarPlano.ConfigurarArquivos.configurar_arquivos_builder(inter, id)
            await inter.response.edit_message(embed=embed, components=components)
        elif cid.startswith("Config_EnviarMensagemCompra_"):
            await inter.response.defer(ephemeral=True)
            id = cid.split("_")[2]
            embed, components = Services.ComprarServico.comprar_servico_builder(inter, id)
            components.pop(1)
            await inter.channel.send(embed=embed, components=components)


    @commands.Cog.listener("on_dropdown")
    async def on_dropdown(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "Config_SelecionarPlano":
            id = inter.values[0]
            embed, components = Plans.GerenciarPlano.gerenciar_plano_builder(inter, id)
            await inter.response.edit_message(embed=embed, components=components)

def setup(bot):
    bot.add_cog(PlansExtension(bot))