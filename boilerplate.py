# This file servers as a boilerplate for cog files
import typing
import nextcord
from nextcord.ext import commands
from nextcord import SlashOption

class name(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(name(bot))