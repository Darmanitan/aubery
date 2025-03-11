import typing
import nextcord
from nextcord.ext import commands
from nextcord import SlashOption

class moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name='purge', description='purges an amount of messages')
    @commands.has_permissions(manage_messages = True)
    async def purge(self, interaction: nextcord.Interaction, count: typing.Optional[int] = SlashOption(required=False, description='amount of messages to purge', default=10)):
        await interaction.channel.purge(limit = count)
        await interaction.send(f"Successfuly purged `{count}` messages!", ephemeral=True)

def setup(bot):
    bot.add_cog(moderation(bot))