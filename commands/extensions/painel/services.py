import disnake
from disnake.ext import commands
from database import Database

class Services:
    @staticmethod
    def services_builder(inter: disnake.MessageInteraction):
        services = Database.obter("services.json")
        options = []

        embed = disnake.Embed(
            title="Serviços disponíveis",
            description="Selecione o serviço que deseja adquirir para criar o pagamento. O pagamento será feito através do Mercado Pago e, quando aprovado, a aplicação será criada.",
            color=disnake.Color.blurple()
        )
        embed.add_field(name="Serviços disponíveis", value=f"`{len(services)}`", inline=False)
        for service in services.values():
            price_str = f"{float(service['price']):.2f}".replace('.', ',')
            options.append(disnake.SelectOption(label=service["name"], description=f"R$ {price_str} | {service['pre-description']}", value=service["id"]))
        
        if not options:
            options.append(disnake.SelectOption(label="Nenhum serviço disponível"))
        
        components = [
            disnake.ui.StringSelect(
                placeholder=f"[{len(services)}] Selecione o serviço que deseja adquirir",
                options=options,
                custom_id="Painel_SelecionarServico",
                disabled=True if len(services) == 0 else False
            ),
            disnake.ui.Button(label="Voltar", custom_id="Painel_Voltar")
        ]

        return embed, components

    class ComprarServico:
        @staticmethod
        def comprar_servico_builder(inter: disnake.MessageInteraction, id: str):
            services = Database.obter("services.json")
            service = services[id]
            embed = disnake.Embed(
                title=f"Comprar serviço — {service['name']}",
                description=service["description"],
                color=disnake.Color.blurple()
            )
            embed.add_field(name="Preço mensal", value=f"`R$ {float(service['price']):.2f}`".replace('.', ','), inline=True)
            embed.add_field(name="Serviço disponível para compra", value=f"`{'Sim' if service['apps']['filename'] else 'Não'}`", inline=True)

            components = [
                disnake.ui.StringSelect(
                    placeholder="Selecione o plano que deseja adquirir",
                    options=[
                        disnake.SelectOption(label="Mensal", description=f"R$ {float(service['price']):.2f}".replace('.', ',') + " | 1 mês de uso", value="mensal"),
                        disnake.SelectOption(label="Trimensal", description=f"R$ {float(service['price'])*3.00:.2f}".replace('.', ',') + " | 3 meses de uso", value="trimensal"),
                        disnake.SelectOption(label="Anual", description=f"R$ {float(service['price'])*12.00:.2f}".replace('.', ',') + " | 12 meses de uso", value="anual"),
                    ],
                    custom_id=f"Painel_SelecionarPlano_{id}",
                    disabled=True if not service["apps"]["filename"] else False
                ),
                disnake.ui.Button(label="Voltar", custom_id="Painel_ComprarServicos")
            ]

            return embed, components

class ServicesExtension(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_button_click")
    async def on_button_click(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "Painel_ComprarServicos":
            embed, components = Services.services_builder(inter)
            await inter.response.edit_message(embed=embed, components=components)

    @commands.Cog.listener("on_dropdown")
    async def on_dropdown(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "Painel_SelecionarServico":
            id = inter.values[0]
            embed, components = Services.ComprarServico.comprar_servico_builder(inter, id)
            await inter.response.edit_message(embed=embed, components=components)

def setup(bot):
    bot.add_cog(ServicesExtension(bot))