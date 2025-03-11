import nextcord
import nextcord
import datetime
import requests
import json
import os
import typing
from nextcord.ext import commands
from nextcord import SlashOption

class PFPView(nextcord.ui.View):
    def __init__(self, pfps, json_path, user_id):
        super().__init__(timeout=180)
        self.pfps = pfps
        self.index = 0
        self.delete_confirm = False
        self.json_path = json_path
        self.user_id = user_id

    @nextcord.ui.button(label="⬅️", style=nextcord.ButtonStyle.green)
    async def previous(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.index > 0:
            self.index -= 1
            await self.update_embed(interaction)

    @nextcord.ui.button(label="➡️", style=nextcord.ButtonStyle.green)
    async def next(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.index < len(self.pfps) - 1:
            self.index += 1
            await self.update_embed(interaction)

    @nextcord.ui.button(label="️❌", style=nextcord.ButtonStyle.red)
    async def delete(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not self.delete_confirm:
            self.delete_confirm = True
            # Add confirm button
            self.confirm_button = nextcord.ui.Button(label="🗑", style=nextcord.ButtonStyle.green)
            async def confirm_callback(i: nextcord.Interaction):
                # Load current data
                with open(self.json_path, 'r') as f:
                    data = json.load(f)
                
                # Find and update user's pfps
                user_data = next((u for u in data["users"] if u["user_id"] == self.user_id), None)
                if user_data:
                    del user_data["pfps"][self.index]
                    # Save changes
                    with open(self.json_path, 'w') as f:
                        json.dump(data, f, indent=4)
                    
                    if len(user_data["pfps"]) == 0:
                        await i.message.delete()
                        await i.response.send_message("Profile picture deleted. No more pictures in history.", ephemeral=True)
                    else:
                        self.pfps = user_data["pfps"]
                        self.index = min(self.index, len(self.pfps) - 1)
                        await self.update_embed(i)
                        await i.response.send_message("Profile picture deleted.", ephemeral=True)

                self.delete_confirm = False
                
            self.confirm_button.callback = confirm_callback
            self.add_item(self.confirm_button)
            await interaction.response.edit_message(view=self)
            self.remove_item(self.confirm_button)
        else:
            await interaction.response.defer()

    async def update_embed(self, interaction):
        pfp = self.pfps[self.index]
        embed = nextcord.Embed(title="Profile Picture History", color=0x2F3136)
        embed.set_image(url=pfp["url"])
        embed.set_footer(text=f"Date: {pfp['date']} • {self.index + 1}/{len(self.pfps)}")
        await interaction.response.edit_message(embed=embed, view=self)

class pfp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.json_path = "f:/Software/projects/python/ARCHIVE/aubery/pfps/pfps.json"

    def load_pfps(self):
        if os.path.exists(self.json_path):
            with open(self.json_path, 'r') as f:
                return json.load(f)
        return {"users": []}

    def save_pfps(self, data):
        with open(self.json_path, 'w') as f:
            json.dump(data, f, indent=4)
    
    def upload_catbox(self, url):
            catbox_url = "https://catbox.moe/user/api.php"
            data = {
                'reqtype': "urlupload",
                'userhash': '',
                'url': url 
            }
            response = requests.post(url=catbox_url, data=data)

            return response


    @nextcord.slash_command(name="pfp", description="pfp related utilities", guild_ids=[970839491700989952])
    async def pfp(self, interaction: nextcord.Interaction):
        pass

    @pfp.subcommand(name="history", description="View your pfp history")
    async def history(self, interaction: nextcord.Interaction):
        data = self.load_pfps()
        user_data = next((u for u in data["users"] if u["user_id"] == str(interaction.user.id)), None)
        
        if not user_data or not user_data["pfps"]:
            await interaction.response.send_message("No profile picture history found!", ephemeral=True)
            return

        pfps = user_data["pfps"]
        view = PFPView(pfps, self.json_path, str(interaction.user.id))
        embed = nextcord.Embed(title="Profile Picture History", color=0x2F3136)
        embed.set_image(url=pfps[0]["url"])
        embed.set_footer(text=f"Date: {pfps[0]['date']} • 1/{len(pfps)}")
        await interaction.response.send_message(embed=embed, view=view)

    @pfp.subcommand(name="log")
    async def log(self, interaction: nextcord.Interaction):
        date = datetime.date.today().isoformat()
        pfp_url = str(interaction.user.avatar.url)
        
        # Upload to catbox
        try:
            response = self.upload_catbox(pfp_url)
            """ data = {
                'reqtype': "urlupload",
                'userhash': '',
                'url': pfp_url
            }
            response = requests.post(url=catbox_url, data=data)"""
            if response.ok:
                permanent_url = str(response.content.decode('ASCII'))
                
                # Save to JSON
                pfps_data = self.load_pfps()
                user_data = next((u for u in pfps_data["users"] if u["user_id"] == str(interaction.user.id)), None)
                
                if user_data:
                    user_data["pfps"].append({"url": permanent_url, "date": date})
                else:
                    pfps_data["users"].append({
                        "user_id": str(interaction.user.id),
                        "pfps": [{"url": permanent_url, "date": date}]
                    })
                
                self.save_pfps(pfps_data)
                await interaction.response.send_message("Profile picture logged successfully!", ephemeral=True)
                
                # Send history embed
                user_data = next((u for u in pfps_data["users"] if u["user_id"] == str(interaction.user.id)), None)
                pfps = user_data["pfps"]
                view = PFPView(pfps, self.json_path, str(interaction.user.id))
                embed = nextcord.Embed(title="Profile Picture History", color=0x2F3136)
                embed.set_image(url=pfps[0]["url"])
                embed.set_footer(text=f"Date: {pfps[0]['date']} • 1/{len(pfps)}")
                await interaction.followup.send(embed=embed, view=view)
            else:
                await interaction.response.send_message("Failed to upload image", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)
    
    @pfp.subcommand(name="upload", description="upload a file to pfp history")
    async def upload(self, interaction: nextcord.Interaction, file: nextcord.Attachment = SlashOption(description="pfp to upload", required=True)):
        date = datetime.date.today().isoformat()
        try:
            if "image" in file.content_type:
                response = self.upload_catbox(file.url) 
                if response.ok:
                    permanent_url = str(response.content.decode('ASCII'))
                    
                    # Save to JSON
                    pfps_data = self.load_pfps()
                    user_data = next((u for u in pfps_data["users"] if u["user_id"] == str(interaction.user.id)), None)
                    
                    if user_data:
                        user_data["pfps"].append({"url": permanent_url, "date": date})
                    else:
                        pfps_data["users"].append({
                            "user_id": str(interaction.user.id),
                            "pfps": [{"url": permanent_url, "date": date}]
                        })
                    
                    self.save_pfps(pfps_data)
                    await interaction.response.send_message("Profile picture logged successfully!", ephemeral=True)
                    
                    # Send history embed
                    user_data = next((u for u in pfps_data["users"] if u["user_id"] == str(interaction.user.id)), None)
                    pfps = user_data["pfps"]
                    view = PFPView(pfps, self.json_path, str(interaction.user.id))
                    embed = nextcord.Embed(title="Profile Picture History", color=0x2F3136)
                    embed.set_image(url=pfps[0]["url"])
                    embed.set_footer(text=f"Date: {pfps[0]['date']} • 1/{len(pfps)}")
                    await interaction.followup.send(embed=embed, view=view)
                else:
                    await interaction.response.send_message("Failed to upload image", ephemeral=True)
            else:
                await interaction.response.send_message("Please upload an image file!")
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)


def setup(bot):
    bot.add_cog(pfp(bot))