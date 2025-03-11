import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
class misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    IDS = [970839491700989952]
    
    
    @nextcord.slash_command(name='ping', description='displays ping from bot to discord')
    async def ping(self, interaction: nextcord.Interaction):
        await interaction.send(f'**Pong!** Latency: ~{round(self.bot.latency * 1000, 3)}ms')
    
    @nextcord.slash_command(name='avatar', description='displays a users avatar!')
    async def avatar(self, interaction: nextcord.Interaction, user: nextcord.User = SlashOption(required=True, description='user to get avatar from')):
        embed = nextcord.Embed(
            title = f"{user.name}'s avatar"
        )
        embed.set_author(name = user, icon_url = user.display_avatar.url)
        embed.set_image(url=user.display_avatar.url)
        await interaction.send(embed=embed)

    @nextcord.slash_command(name='serverinfo', description='displays information about server')
    async def serverinfo(self, interaction: nextcord.Interaction):
        member_count = interaction.guild.member_count
        owner = f"{interaction.guild.owner.name}#{interaction.guild.owner.discriminator}"
        channels = len(interaction.guild.text_channels)
        voice = len(interaction.guild.voice_channels)
        roles = len(interaction.guild.roles)
        categories = len(interaction.guild.categories)
        created_at = str(interaction.guild.created_at).split(" ")

        embed = nextcord.Embed()
        embed.set_author(name=f"{interaction.guild.name} | server info", icon_url=(interaction.guild.icon.url))
        embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.set_footer(text=f"ID: {interaction.guild.id} | created at: {created_at[0]}")
        embed.add_field(name="owner", value=owner)
        embed.add_field(name="members", value=member_count)
        embed.add_field(name="channel count", value=channels)
        embed.add_field(name="voice channels", value=voice)
        embed.add_field(name="roles", value=roles)
        embed.add_field(name="categories", value=categories)

        await interaction.send(embed=embed)


def setup(bot):
    bot.add_cog(misc(bot))