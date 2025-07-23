import os
import disnake
from disnake.ext import commands

class Perms:
    @staticmethod
    def is_owner(inter: disnake.ApplicationCommandInteraction):
        return inter.author.id == int(os.getenv("OWNER_ID"))
    
    @staticmethod
    def owner_only():
        def predicate(inter: disnake.ApplicationCommandInteraction):
            return Perms.is_owner(inter)
        return commands.check(predicate)
