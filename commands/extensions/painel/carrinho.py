import asyncio
import os
import disnake
from disnake.ext import commands
from database import Database
from functions.mercadopago import MercadoPago
from functions.squarecloud import SquareCloud

CARRINHO_TIMEOUT_TASKS = {}
PAGAMENTO_TASKS = {}

class Carrinho:
    @staticmethod
    def carrinho_builder(inter: disnake.MessageInteraction):
        carrinho = Database.obter("carrinhos.json")[str(inter.user.id)]
        service = Database.obter("services.json")[carrinho["serviceID"]]

        embed = disnake.Embed(
            title="Carrinho de compras",
            description="Este é o seu carrinho de compras. Aqui você pode ver o preço final, efetuar o pagamento e configurar seu serviço.",
            color=disnake.Color.blurple()
        )
        embed.add_field(name="Serviço selecionado", value=f"`{service['name']}`\n`{service['pre-description']}`", inline=False)
        embed.add_field(name="Preço final", value=f"`R$ {float(carrinho['price']):.2f}`", inline=True)
        embed.add_field(name="Plano selecionado", value=f"`{carrinho['plano'].capitalize()}`", inline=True)
        components = [
            disnake.ui.StringSelect(
                placeholder="Selecione o plano que deseja adquirir",
                custom_id=f"Painel_EditarPlano",
                max_values=1,
                options=[
                    disnake.SelectOption(label="Mensal", description=f"R$ {float(service['price']):.2f}".replace('.', ',') + " | 1 mês de uso", value="mensal", default=True if carrinho["plano"] == "mensal" else False),
                    disnake.SelectOption(label="Trimensal", description=f"R$ {float(service['price'])*3.00:.2f}".replace('.', ',') + " | 3 meses de uso", value="trimensal", default=True if carrinho["plano"] == "trimensal" else False),
                    disnake.SelectOption(label="Anual", description=f"R$ {float(service['price'])*12.00:.2f}".replace('.', ',') + " | 12 meses de uso", value="anual", default=True if carrinho["plano"] == "anual" else False),
                ]
            ),
            disnake.ui.Button(label="Efetuar pagamento", style=disnake.ButtonStyle.green, custom_id=f"Painel_EfetuarPagamento_{inter.user.id}"),
            disnake.ui.Button(label="Cancelar compra", style=disnake.ButtonStyle.red, custom_id=f"Carrinho_CancelarCompra_{inter.user.id}"),
        ]

        return embed, components

    @staticmethod
    def cancelar_compra(inter: disnake.MessageInteraction):
        carrinhos = Database.obter("carrinhos.json")
        carrinhos.pop(str(inter.user.id))
        Database.salvar("carrinhos.json", carrinhos)

    @staticmethod
    def start_or_renew_carrinho_timeout(inter: disnake.MessageInteraction, timeout: int = 600):
        user_id = str(inter.user.id)

        task = CARRINHO_TIMEOUT_TASKS.pop(user_id, None)
        if task:
            task.cancel()

        task = asyncio.create_task(Carrinho.carrinho_timeout(inter, timeout))
        CARRINHO_TIMEOUT_TASKS[user_id] = task

    @staticmethod
    async def carrinho_timeout(inter: disnake.MessageInteraction, timeout: int = 600):
        await asyncio.sleep(timeout)
        carrinho = Database.obter("carrinhos.json")[str(inter.user.id)]
        carrinho_obj = inter.guild.get_channel_or_thread(carrinho["guild"]["channelID"])
        try:
            await carrinho_obj.delete()
        except Exception as e:
            print(f"Erro ao deletar canal do carrinho: {e}")
        Carrinho.cancelar_compra(inter)
        CARRINHO_TIMEOUT_TASKS.pop(str(inter.user.id), None)

    class Pagamento:
        @staticmethod
        def pagamento_builder(inter: disnake.MessageInteraction):
            carrinho = Database.obter("carrinhos.json")[str(inter.user.id)]
            service = Database.obter("services.json")[carrinho["serviceID"]]
            embed = disnake.Embed(
                title=f"Pagamento — {service['name']}",
                description="Utilize este painel para efetuar o pagamento e configurar o serviço. O bot está verificando periodicamente se o pagamento foi aprovado. Quando aprovado, a aplicação será criada e enviada para você.",
                color=disnake.Color.blurple()
            )
            embed.set_image(url=carrinho["payment"]["qrcodeURL"])
            embed.add_field(name="Código Copia e Cola", value=f"```{carrinho['payment']['qrcode']}```", inline=False)
            embed.add_field(name="Preço final", value=f"`R$ {float(carrinho['price']):.2f}`", inline=True)
            embed.add_field(name="Plano selecionado", value=f"`{carrinho['plano'].capitalize()}`", inline=True)
            components = [
                disnake.ui.Button(label="Copiar código Copia e Cola", style=disnake.ButtonStyle.blurple, custom_id=f"Painel_CopiarCodigo_{inter.user.id}"),
                disnake.ui.Button(label="Cancelar compra", style=disnake.ButtonStyle.red, custom_id=f"Carrinho_CancelarCompra_{inter.user.id}"),
            ]
            return embed, components
        
        @staticmethod
        def start_pagamento_task(inter: disnake.MessageInteraction):
            user_id = str(inter.user.id)
            task = PAGAMENTO_TASKS.pop(user_id, None)
            if task:
                task.cancel()

            task = asyncio.create_task(Carrinho.Pagamento.verificar_pagamento_task(inter))
            PAGAMENTO_TASKS[user_id] = task

        @staticmethod
        async def verificar_pagamento_task(inter: disnake.MessageInteraction):
            user_id = str(inter.user.id)
            elapsed = 0
            while elapsed < 600:
                await asyncio.sleep(3)
                pagamento = MercadoPago.verificar_pagamento(str(inter.user.id))
                if pagamento == True:
                    task = CARRINHO_TIMEOUT_TASKS.pop(user_id, None)
                    if task:
                        task.cancel()

                    PAGAMENTO_TASKS.pop(user_id, None)
                    await Carrinho.Entrega.entregar(inter)
                    return
                elapsed += 3

            carrinho = Database.obter("carrinhos.json")[str(inter.user.id)]
            carrinho_obj = inter.guild.get_channel_or_thread(carrinho["guild"]["channelID"])
            await carrinho_obj.delete()
            Carrinho.cancelar_compra(inter)
            CARRINHO_TIMEOUT_TASKS.pop(user_id, None)

    class Entrega:
        @staticmethod
        def entrega_builder(inter: disnake.MessageInteraction):
            carrinho = Database.obter("carrinhos.json")[str(inter.user.id)]
            service = Database.obter("services.json")[carrinho["serviceID"]]
            
            embed = disnake.Embed(
                title="Entrega de serviço",
                description="O seu pagamento foi aprovado e agora estamos processando a sua entrega. Pedimos que você aguarde um momento enquanto eu configuro o seu serviço. Quando pronto, você receberá um notificação aqui e no seu privado - e após ela, você poderá configurar a sua aplicação em `/painel > Configurar suas aplicações`",
                color=disnake.Color.blurple()
            )
            embed.add_field(name="Serviço", value=f"`{service['name']}`", inline=True)
            embed.add_field(name="Plano", value=f"`{carrinho['plano'].capitalize()}`", inline=True)
            embed.add_field(name="Preço", value=f"`R$ {float(carrinho['price']):.2f}`", inline=True)

            components = [
                disnake.ui.Button(label="Configurar aplicação", style=disnake.ButtonStyle.blurple, custom_id=f"Painel_ConfigurarAplicacao_{inter.user.id}", disabled=True),
            ]

            return embed, components

        @staticmethod
        def entrega_concluida_builder(inter: disnake.MessageInteraction, app_id: str):
            carrinho = Database.obter("carrinhos.json")[str(inter.user.id)]
            service = Database.obter("services.json")[carrinho["serviceID"]]

            embed = disnake.Embed(
                title="Entrega de serviço concluída",
                description="O seu pagamento já foi aprovado e hospedamos sua aplicação com sucesso. Você pode configurar a sua aplicação em `/painel > Configurar suas aplicações`.",
                color=disnake.Color.blurple()
            )
            embed.add_field(name="Serviço", value=f"`{service['name']}`", inline=True)
            embed.add_field(name="Plano", value=f"`{carrinho['plano'].capitalize()}`", inline=True)
            embed.add_field(name="Preço", value=f"`R$ {float(carrinho['price']):.2f}`", inline=True)

            components = [
                disnake.ui.Button(label="Configurar aplicação", style=disnake.ButtonStyle.blurple, custom_id=f"Painel_ConfigurarAplicacao_{inter.user.id}", disabled=False),
            ]
            return embed, components

        @staticmethod
        async def entregar(inter: disnake.MessageInteraction):
            carrinho = Database.obter("carrinhos.json")[str(inter.user.id)]
            service = Database.obter("services.json")[carrinho["serviceID"]]

            embed, components = Carrinho.Entrega.entrega_builder(inter)
            await inter.edit_original_message("", embed=embed, components=components)
            
            bot_id = await SquareCloud.upload_bot(f"{service['apps']['filename']}")
            await SquareCloud.start_bot(bot_id)

            embed, components = Carrinho.Entrega.entrega_concluida_builder(inter, bot_id)
            embed.add_field(name="ID da aplicação", value=f"`{bot_id}`", inline=False)
            embed.add_field(name="Informação adicional", value="Este carrinho será excluído em 10 segundos. Enviei uma mensagem privada para você com as instruções de configuração da aplicação.", inline=False)
            await inter.user.send(embed=embed)
            await inter.edit_original_message(f"{inter.user.mention}", embed=embed, components=components)
            await asyncio.sleep(10)
            Carrinho.cancelar_compra(inter)
            CARRINHO_TIMEOUT_TASKS.pop(str(inter.user.id), None)
            PAGAMENTO_TASKS.pop(str(inter.user.id), None)
            await inter.channel.delete()
            
class CarrinhoExtension(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_button_click")
    async def on_button_click(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id.startswith("Carrinho_CancelarCompra_"):
            carrinho = Database.obter("carrinhos.json")[str(inter.user.id)]
            carrinho_obj = inter.guild.get_channel_or_thread(carrinho["guild"]["channelID"])
            await carrinho_obj.delete()
            Carrinho.cancelar_compra(inter)

        elif inter.component.custom_id.startswith("Painel_CopiarCodigo_"):
            carrinho = Database.obter("carrinhos.json")[str(inter.user.id)]
            await inter.response.send_message(f"{carrinho['payment']['qrcode']}", ephemeral=True)
        
        elif inter.component.custom_id.startswith("Painel_EfetuarPagamento_"):
            await inter.response.defer(ephemeral=True)
            carrinhos = Database.obter("carrinhos.json")
            carrinho = Database.obter("carrinhos.json")[str(inter.user.id)]
            service = Database.obter("services.json")[carrinho["serviceID"]]

            if not service["apps"]["filename"]:
                await inter.followup.send("Este serviço não possui um arquivo de configuração da SquareCloud válido.", ephemeral=True)
                return
            
            if not os.path.exists(f"{service['apps']['filename']}"):
                await inter.followup.send("O arquivo de configuração da SquareCloud não foi encontrado.", ephemeral=True)
                return
            
            if not MercadoPago.verificar_conta():
                await inter.followup.send("A conta do Mercado Pago não está configurada corretamente.", ephemeral=True)
                return
            
            await inter.edit_original_message(content="Aguarde um momento enquanto eu processo o seu pagamento...", embed=None, components=[])

            if carrinho["price"] == 0:
                await Carrinho.Entrega.entregar(inter)
                return

            qrcode, qrcodeURL, paymentID = MercadoPago.criar_pagamento(carrinho["price"])
            if not qrcode or not qrcodeURL or not paymentID:
                embed, components = Carrinho.carrinho_builder(inter)
                await inter.edit_original_message(content="Ocorreu um erro ao processar o pagamento.", embed=embed, components=components)
                await inter.followup.send("Ocorreu um erro ao processar o pagamento.", ephemeral=True)
                return

            carrinho["payment"]["qrcode"] = qrcode
            carrinho["payment"]["qrcodeURL"] = qrcodeURL
            carrinho["payment"]["paymentID"] = paymentID
            carrinhos[str(inter.user.id)] = carrinho
            Database.salvar("carrinhos.json", carrinhos)

            embed, components = Carrinho.Pagamento.pagamento_builder(inter)
            await inter.edit_original_message("", embed=embed, components=components)

            Carrinho.start_or_renew_carrinho_timeout(inter)
            Carrinho.Pagamento.start_pagamento_task(inter)

    @commands.Cog.listener("on_dropdown")
    async def on_dropdown(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id.startswith("Painel_SelecionarPlano_"):
            await inter.response.send_message("Aguarde um momento enquanto eu processo o seu carrinho...", ephemeral=True)
            id = inter.component.custom_id.split("_")[2]
            plano = inter.values[0]
            services = Database.obter("services.json")
            service = services[id]
            if plano == "mensal": price = float(service["price"])
            elif plano == "trimensal": price = float(service["price"])*3.00
            elif plano == "anual": price = float(service["price"])*12.00
            price = float(f"{price:.2f}")

            carrinhos = Database.obter("carrinhos.json")

            if str(inter.user.id) in carrinhos:
                try:
                    channel = inter.guild.get_channel_or_thread(carrinhos[str(inter.user.id)]["guild"]["channelID"])
                    if channel:
                        return await inter.edit_original_message(content="Você já possui um carrinho de compras ativo. Por favor, finalize o carrinho atual antes de criar um novo.", components=[disnake.ui.Button(label="Ir para o carrinho", url=channel.jump_url)])
                except:
                    carrinhos.pop(str(inter.user.id))

            topico = await inter.channel.create_thread(
                name=f"Carrinho de compras — {service['name']}",
                type=disnake.ChannelType.private_thread,
                invitable=False
            )

            carrinhos[str(inter.user.id)] = {
                "serviceID": service["id"],
                "price": price,
                "plano": plano,
                "guild": {"guildID": inter.guild.id, "channelID": topico.id, "userID": str(inter.user.id)},
                "payment": {"qrcode": None, "qrcodeURL": None, "paymentID": None}
            }
            Database.salvar("carrinhos.json", carrinhos)
            embed, components = Carrinho.carrinho_builder(inter)
            await topico.send(content=f"{inter.user.mention}", embed=embed, components=components)
            await inter.edit_original_message(content="Carrinho de compras criado com sucesso.", embed=None, components=[disnake.ui.Button(label="Ir para o carrinho", url=topico.jump_url)])
            Carrinho.start_or_renew_carrinho_timeout(inter)
        
        elif inter.component.custom_id.startswith("Painel_EditarPlano"):
            carrinhos = Database.obter("carrinhos.json")
            services = Database.obter("services.json")
            carrinhos[str(inter.user.id)]["plano"] = inter.values[0]
            carrinhos[str(inter.user.id)]["price"] = float(f"{float(services[carrinhos[str(inter.user.id)]["serviceID"]]["price"])*(1 if carrinhos[str(inter.user.id)]["plano"] == "mensal" else 3 if carrinhos[str(inter.user.id)]["plano"] == "trimensal" else 12):.2f}")
            Database.salvar("carrinhos.json", carrinhos)
            embed, components = Carrinho.carrinho_builder(inter)
            await inter.response.edit_message(embed=embed, components=components)

def setup(bot):
    bot.add_cog(CarrinhoExtension(bot))