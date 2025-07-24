import disnake
from disnake.ext import commands
from database import Database

class Config:
    @staticmethod
    def services_builder(inter: disnake.MessageInteraction):
        services = Database.obter("services.json")
        embed = disnake.Embed(
            title="Serviços disponíveis",
            description="Selecione o serviço que deseja adquirir para criar o pagamento. O pagamento será feito através do Mercado Pago e, quando aprovado, a aplicação será criada.",
            color=disnake.Color.blurple()
        )
        embed.add_field(name="Serviços disponíveis", value=f"`{len(services)}`", inline=False)
        options = [
            disnake.SelectOption(label=s["name"], description=f"R$ {s['price'].replace('.', ',')} | {s['pre-description']}", value=s["id"])
            for s in services
        ]

        if not options:
            options.append(disnake.SelectOption(label="Nenhum serviço disponível"))
        components = [
            disnake.ui.StringSelect(
                placeholder=f"[{len(services)}] Selecione o serviço que deseja adquirir",
                options=options,
                custom_id="Painel_SelecionarServico",
                disabled=not bool(services)
            ),
            disnake.ui.Button(label="Voltar", custom_id="Painel_Voltar")
        ]
        return embed, components

class ConfigExtension(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(ConfigExtension(bot))