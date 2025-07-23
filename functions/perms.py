import os
import disnake

class Perms:
    @staticmethod
    def is_owner(inter: disnake.ApplicationCommandInteraction):
        return inter.author.id == int(os.getenv("OWNER_ID"))