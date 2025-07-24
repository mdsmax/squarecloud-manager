import disnake
from disnake.ext import commands
from database import Database

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
        embed.add_field(name="Preço final", value=f"`R$ {carrinho['price']:.2f}`", inline=True)
        embed.add_field(name="Plano selecionado", value=f"`{carrinho['plano'].capitalize()}`", inline=True)
        components = [
            disnake.ui.StringSelect(
                placeholder="Selecione o plano que deseja adquirir",
                custom_id=f"Painel_EditarPlano",
                max_values=1,
                options=[
                    disnake.SelectOption(label="Mensal", description=f"R$ {service['price'].replace('.', ',')} | 1 mês de uso", value="mensal", default=True if carrinho["plano"] == "mensal" else False),
                    disnake.SelectOption(label="Trimensal", description=f"R$ {float(service['price'])*3.00:.2f} | 3 meses de uso", value="trimensal", default=True if carrinho["plano"] == "trimensal" else False),
                    disnake.SelectOption(label="Anual", description=f"R$ {float(service['price'])*12.00:.2f} | 12 meses de uso", value="anual", default=True if carrinho["plano"] == "anual" else False),
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
        
        elif inter.component.custom_id.startswith("Painel_EfetuarPagamento_"):
            carrinho = Database.obter("carrinhos.json")[str(inter.user.id)]

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
        
        elif inter.component.custom_id.startswith("Painel_EditarPlano"):
            carrinhos = Database.obter("carrinhos.json")
            services = Database.obter("services.json")
            carrinhos[str(inter.user.id)]["plano"] = inter.values[0]
            carrinhos[str(inter.user.id)]["price"] = float(services[carrinhos[str(inter.user.id)]["serviceID"]]["price"]) * (1 if carrinhos[str(inter.user.id)]["plano"] == "mensal" else 3 if carrinhos[str(inter.user.id)]["plano"] == "trimensal" else 12)
            Database.salvar("carrinhos.json", carrinhos)
            embed, components = Carrinho.carrinho_builder(inter)
            await inter.response.edit_message(embed=embed, components=components)

def setup(bot):
    bot.add_cog(CarrinhoExtension(bot))