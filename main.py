import nextcord
import os
import asyncio

from nextcord.ext import commands
from dotenv import load_dotenv

load_dotenv()
bot = commands.Bot(command_prefix=commands.when_mentioned_or("$"), case_insensitive=True, activity=nextcord.Game(name="aubery | $help"), intents=nextcord.Intents.all())

@bot.event
async def on_ready():
    print(f"successfuly logged in as {bot.user}")

@bot.command(name='load', description='loads cog')
async def load(ctx, extension):
    if ctx.message.author.id == int(os.getenv("hostID")):
        bot.load_extension(f"cogs.{extension}")
        await ctx.send(f"successfuly loaded {extension}", delete_after=3)
    else:
        await ctx.send("seriously? why would you even try.", delete_after=3)

@bot.command(name='unload', description='unloads cog')
async def unload(ctx, extension):
    if ctx.message.author.id == int(os.getenv("hostID")):
        bot.unload_extension(f"cogs.{extension}")
        await ctx.send(f"successfuly unloaded {extension}", delete_after=3)
    else:
        await ctx.send("seriously? why would you even try", delete_after=3)

@bot.command(name='reload', description='reloads cog')
async def reload(ctx, extension):
    if ctx.message.author.id == int(os.getenv("hostID")): 
        bot.reload_extension(f"cogs.{extension}")
        await ctx.send(f"successfuly reloaded {extension}", delete_after=3)
    else:
        await ctx.send("seriously? why would you even try", delete_after=3)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"You do not have the required permissions to execute this command! {ctx.message.author.mention}", delete_after=3)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Please input a required argument", delete_after=3)
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown. Please try again after {round(error.retry_after, 1)} seconds.", delete_after=3)
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send(f"This command does not exist! {ctx.message.author.mention}", delete_after=3)
    elif isinstance(error, commands.ExtensionAlreadyLoaded):
        await ctx.send(f"This extension is already loaded! {ctx.message.author}", delete_after=3)
    else:
        raise error

for fn in os.listdir("./cogs"):
    if fn.endswith(".py"):
        bot.load_extension(f"cogs.{fn[:-3]}")
bot.run(os.getenv("token"))