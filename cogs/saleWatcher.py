import typing
import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
from nextcord.ui import Button
from nextcord.ui import View
import requests
from urllib.parse import urlparse
import asyncio
import db_manager

class saleWatcher(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="watch", description="Watches an item for a sale")
    async def watch(self,
                    interaction: nextcord.Interaction,
                    platform: str = SlashOption(description="Platform to watch a sale on",
                                                required=True,
                                                choices=["Steam", "Amazon"]),
                    link: str = SlashOption(description="Link to item you want to watch",
                                            required=True)):

        if platform == "Steam":
            if link.isnumeric():
                app_id = link
            else:
                app_id = urlparse(link).path.split('/')[2]

        if not app_id.isnumeric():
            await interaction.send("something is wrong")

        response = requests.get(f"https://store.steampowered.com/api/appdetails?appids={app_id}&cc=ca").json()
        if response[f"{app_id}"]["success"]:
            if response[f"{app_id}"]["data"]["is_free"]:
                await interaction.send("🚫💵 this game doesn't cost money")

            price_overview = response[f"{app_id}"]["data"]["price_overview"]

            embed = nextcord.Embed(
                title=response[f"{app_id}"]["data"]["name"],
                url=link,
                description=response[f"{app_id}"]["data"]["short_description"]
            )
            if response[f"{app_id}"]["data"]["header_image"]:
                embed.set_image(url=response[f"{app_id}"]["data"]["header_image"])
            if price_overview["initial"]:
                initial = str(price_overview["final_formatted"]).split(" ")[0] + " " + str(round(price_overview["initial"] * (10 ** -2), 2))
                embed.add_field(name="💵 Initial Price", value=initial)
            if price_overview["final_formatted"]:
                embed.add_field(name="💵 Current Price", value=price_overview["final_formatted"])
            if price_overview['discount_percent']:
                embed.add_field(name="% Current Discount", value=f"{price_overview['discount_percent']}%")

            
            async def watch_sale(interaction):
                user_id = str(interaction.user.id)
                game_id = str(app_id)
                # ID: Int | wishlist: Int[] | notificationMethod: byte 0 = none, 1 = ping, 2 = dm
                if not db_manager.fetch_user(user_id):
                    await interaction.send("user not in database... initliazing !")
                    db_manager.initialize_user(user_id, 0)
                else:
                    await interaction.send("Adding game to your wishlist!")
                    await interaction.send(app_id)
                    db_manager.add_game(user_id, app_id)



            
            backward = Button(label="⬅️", style=nextcord.ButtonStyle.blurple, custom_id="backward")
            forward = Button(label="➡️", style=nextcord.ButtonStyle.blurple, custom_id="forward")
            watch_sale_button = Button(label="Watch Sale", style=nextcord.ButtonStyle.green, custom_id="watch_sale_button")
            
            async def change_picture(interaction):
                if not hasattr(change_picture, "current_image"):
                    change_picture.current_image = 0
                
                screenshots = response[f"{app_id}"]["data"].get("screenshots", [])
                
                if not screenshots:
                    await interaction.response.send_message("No screenshots available.", ephemeral=True)
                    return
                
                if interaction.data["custom_id"] == "forward":
                    # Cycle through images
                    change_picture.current_image = (change_picture.current_image + 1) % len(screenshots)
                    new_image = screenshots[change_picture.current_image]["path_full"]
                elif interaction.data["custom_id"] == "backward":
                    change_picture.current_image = (change_picture.current_image - 1) % len(screenshots)
                    new_image = screenshots[change_picture.current_image]["path_full"]

                embed.set_image(url=new_image)

                await interaction.response.edit_message(embed=embed, view=view)
            forward.callback = change_picture
            backward.callback = change_picture  # Assign the callback
            watch_sale_button.callback = watch_sale
            
            view = View()
            view.add_item(backward)
            view.add_item(forward)
            view.add_item(watch_sale_button)
            await interaction.send(embed=embed, view=view)
        else:
            await interaction.send("Could not find app" if not response[f"{app_id}"]["success"] else "An unknown error has occurred.")

def setup(bot):
    bot.add_cog(saleWatcher(bot))
