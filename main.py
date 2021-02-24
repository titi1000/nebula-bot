import discord
from discord.ext import commands
import json
import os

### Init

with open("config.json") as config:
    data = json.load(config)

TOKEN = data["token"]
PREFIX = data["prefix"]

client = commands.Bot(command_prefix=PREFIX, help_command=None, case_insensitive=True)

@client.event
async def on_ready():
    print("Bot is ready.")
    print("Logged in as :")
    print("{}#{}".format(client.user.name, client.user.discriminator))
    print(client.user.id)
    print("------------------")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="la doc discord.py"))

### Commands

@client.event
async def on_message(message):
    await client.process_commands(message)
    if message.content == "<@!{}>".format(client.user.id):
        pinged_e = discord.Embed(
        description="Hi, my prefix is `{}`\nUse `{}help` to see all my commands".format(PREFIX, PREFIX),
        color=0xaefe19
        )

        await message.channel.send(embed=pinged_e)

@client.command()
async def infos(ctx):
    infos_e = discord.Embed(
        title="Nebula Bot",
        description="Created by [titi#1000](https://github.com/titi1000)\nUsing discord.py version {}\nCurrently in {} guilds\n".format(discord.__version__, len(client.guilds)),
        color=0xaefe19
    )
    infos_e.set_thumbnail(url=client.user.avatar_url)

    await ctx.send(embed=infos_e)

@client.command()
async def help(ctx):
    await ctx.send("help command")

### Cogs

"""
@client.command()
@commands.has_permissions(administrator=True)
async def load(ctx, extension):
    client.load_extension("cogs.{}".format(extension))

@client.command()
@commands.has_permissions(administrator=True)
async def unload(ctx, extension):
    client.unload_extension("cogs.{}".format(extension))
"""

for filename in os.listdir("./Cogs"):
    if filename.endswith(".py"):
        client.load_extension("Cogs.{}".format(filename[:-3]))


### Error

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    
    if isinstance(error, commands.BadArgument):
        badargument_e = discord.Embed(
            description="{}\nPlease provid a valid argument.".format(str(error)),
            color=0xfe2419
        )
        await ctx.send(embed=badargument_e)

    if isinstance(error, commands.CheckFailure):
        nodm_e = discord.Embed(
            description="Command failed.",
            color=0xfe2419
        )
        await ctx.send(embed=nodm_e)


# run the bot
client.run(TOKEN)