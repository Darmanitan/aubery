import nextcord
import aiohttp

from nextcord.ext import commands
from nextcord import SlashOption

class lookup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name='anime', description='shows information of a given animes')
    async def anime(self, interaction: nextcord.Interaction, anime: str = SlashOption(required=True, description='anime to look up')):
        arg = anime.replace(" ", "%20")
        print(arg)
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.jikan.moe/v4/anime?q={arg}&order_by=popularity") as api:
                data = await api.json()
                try:
                    embed = nextcord.Embed(
                        title=(data['data'][0]['title']),
                        url=(data['data'][0]['url']),
                        description=(data['data'][0]['synopsis'])
                    )
                    embed.set_thumbnail(url=(data['data'][0]['images']['webp']['large_image_url'])) # sets image
                    embed.add_field(name="⭐ Average Rating", value=(data['data'][0]['score'])) # sets rating
                    embed.add_field(name="💽 Type", value=(data['data'][0]['type'])) # sets type
                    embed.add_field(name="⁉️ Genres", value=(", ".join([g['name'] for g in data['data'][0]['genres']]))) # sets genres
                    embed.add_field(name="⏳ Status", value=(data['data'][0]['status'])) # sets status
                    embed.add_field(name="🕛 Aired", value=f"Aired from {(data['data'][0]['aired']['string'])}") # sets aired
                    embed.add_field(name="🏆 Rank", value=f"Top {(data['data'][0]['rank'])}") # sets rank
                except IndexError:
                    await interaction.send("failed to lookup anime")
                else:
                    await interaction.send(embed=embed)
def setup(bot):
    bot.add_cog(lookup(bot))