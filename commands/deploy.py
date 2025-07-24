import disnake
from disnake.ext import commands
from functions.perms import Perms
from database import Database
from functions.squarecloud import SquareCloud
from commands.extensions.painel.carrinho import Carrinho

class Deploy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @staticmethod
    def criar_aplicacao(bot_id: str, service_id: str, plano: str, price: float, guild_id: str, channel_id: str, user_id: str):
        services = Database.obter("services.json")

        apps = Database.obter("apps.json")
        apps[bot_id] = {
            "id": bot_id,
            "name": services[service_id]["name"],
            "owner": user_id,
            "serviceID": service_id,
            "plano": plano,
            "price": price,
            "guild": {"guildID": guild_id, "channelID": channel_id, "userID": str(user_id)},
            "payment": {"qrcode": None, "qrcodeURL": None, "paymentID": None}
        }
        Database.salvar("apps.json", apps)

        services[service_id]["apps"]["id_list"].append(bot_id)
        Database.salvar("services.json", services)
    
    @staticmethod
    def criar_atualizar_cliente(user: disnake.Member, bot_id: str):
        clients = Database.obter("clientes.json")
        if str(user.id) in clients:
            clients[str(user.id)]["apps"].append(bot_id)
        else:
            clients[str(user.id)] = {
                "id": str(user.id),
                "name": user.name,
                "apps": [bot_id]
            }
        Database.salvar("clientes.json", clients)

    @commands.slash_command(name="deploy", description="[DEV] Deployar um serviço como presente para um usuário na SquareCloud")
    async def deploy(
        self,
        inter: disnake.ApplicationCommandInteraction,
        servico: str = commands.Param(description="Serviço a ser criado", autocomplete=True),
        plano: str = commands.Param(description="Plano a ser criado", autocomplete=True),
        usuario: disnake.Member = commands.Param(description="Usuário para receber o serviço"),
    ):
        if not Perms.is_owner(inter):
            return await inter.response.send_message("Faltam permissões para acessar este comando", ephemeral=True)
        
        if servico == "MISSING_PERMISSIONS":
            return await inter.response.send_message("Faltam permissões para acessar este comando", ephemeral=True)
        
        if servico == "NO_SERVICE":
            return await inter.response.send_message("Nenhum serviço encontrado no banco de dados", ephemeral=True)

        await inter.response.defer(ephemeral=True, with_message=True)
        service = Database.obter("services.json")[servico]
        
        bot_id = await SquareCloud.upload_bot(f"{service['apps']['filename']}")
        try: await SquareCloud.start_bot(bot_id)
        except Exception: pass

        Deploy.criar_aplicacao(bot_id, servico, plano, service["price"], inter.guild.id, inter.channel.id, usuario.id)
        Deploy.criar_atualizar_cliente(usuario, bot_id)

        embed = disnake.Embed(
            title="Serviço deployado com sucesso",
            description=f"O serviço `{service['name']}` foi deployado com sucesso para o usuário {usuario.mention}.",
            color=disnake.Color.blurple()
        )
        embed.add_field(name="ID da aplicação", value=f"`{bot_id}`", inline=True)
        embed.add_field(name="Plano", value=f"`{plano.capitalize()}`", inline=True)
        embed.add_field(name="Preço", value=f"`R$ {service['price']:.2f}`", inline=True)
        embed.add_field(name="Serviço", value=f"`{service['name']}`", inline=True)
        embed.add_field(name="Usuário", value=f"{usuario.mention}", inline=True)

        try: await inter.followup.send(embed=embed, ephemeral=True)
        except: pass
        try: await usuario.send(embed=embed)
        except: pass
    
    @deploy.autocomplete("servico")
    async def deploy_servico_autocomplete(self, inter: disnake.ApplicationCommandInteraction, servico: str):
        if not Perms.is_owner(inter):
            return [
                disnake.OptionChoice(
                    name="❌ Faltam permissões para acessar este comando",
                    value="MISSING_PERMISSIONS"
                )
            ]
        
        services = Database.obter("services.json")
        suggestions = [
            disnake.OptionChoice(
                name=f"📄 {service['name']}",
                value=service["id"]
            )
            for service in services.values()
            if servico.lower() in service["name"].lower()
        ]

        if not suggestions:
            return [
                disnake.OptionChoice(
                    name="❌ Nenhum serviço encontrado",
                    value="NO_SERVICE"
                )
            ]

        return suggestions

    @deploy.autocomplete("plano")
    async def deploy_plano_autocomplete(self, inter: disnake.ApplicationCommandInteraction, plano: str):
        if not Perms.is_owner(inter):
            return [
                disnake.OptionChoice(
                    name="❌ Faltam permissões para acessar este comando",
                    value="MISSING_PERMISSIONS"
                )
            ]
        
        planos = [
            disnake.OptionChoice(
                name=f"📆 Mensal",
                value="mensal"
            ),
            disnake.OptionChoice(
                name=f"📆 Trimestral",
                value="trimestral"
            ),
            disnake.OptionChoice(
                name=f"📆 Anual",
                value="anual"
            )
        ]

        return planos
    

def setup(bot):
    bot.add_cog(Deploy(bot))