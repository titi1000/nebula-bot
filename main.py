import discord
from discord.ext import commands
import json
import os

### Init

with open("config.json") as config:
    data = json.load(config)

TOKEN = data["token"]
PREFIX = data["prefix"]
MAINCOLOR = int(data["main_color"], 0)

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix=commands.when_mentioned_or(PREFIX), help_command=None, case_insensitive=True, intents=intents)

@client.event
async def on_ready():
    print("Bot is ready.")
    print("Logged in as :")
    print("{}#{}".format(client.user.name, client.user.discriminator))
    print(client.user.id)
    print("------------------")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="la doc discord.py"))

### Commands

# bot get pinged
@client.event
async def on_message(message):
    await client.process_commands(message)
    if message.content == "<@!{}>".format(client.user.id):
        pinged_e = discord.Embed(
            description="Hi, my prefix is `{}`\nUse `{}help` to see all my commands".format(PREFIX, PREFIX),
            color=MAINCOLOR
        )

        await message.channel.send(embed=pinged_e)

# bot infos
@client.command(aliases=["info"])
async def infos(ctx):
    infos_e = discord.Embed(
        title="Nebula Bot",
        description="Created by [titi#1000](https://github.com/titi1000)\nUsing discord.py version {}\nCurrently in {} guilds\n".format(discord.__version__, len(client.guilds)),
        color=MAINCOLOR
    )
    infos_e.set_thumbnail(url=client.user.avatar_url)

    await ctx.send(embed=infos_e)

# show prefix
@client.command()
async def prefix(ctx):
    prefix_e = discord.Embed(
            description="Hi, my prefix is `{}`, but you can also mention me.\nUse `{}help` or `@{} help` to see all my commands".format(PREFIX, PREFIX, client.user.name),
            color=MAINCOLOR
        )
    
    await ctx.send(embed=prefix_e)

# help command
@client.command()
async def help(ctx):
    description = """Use `{}<command>` to run a command or `{}help <command>` to have more details, or to see how to use a specific command.\n
    **Infos**\n`help`, `infos`, `prefix`, `ping`\n
    **Utils**\n`emojiinfo`, `cloneemoji`, `profile`, `guild`, `emojis`, `membercount`, `quotation`\n
    **Fun**\n`meme`, `8ball`, `avatar`, `giveaway`\n
    **Mods**\n`massrole`, `nick`""".format(PREFIX, PREFIX)

    help_e = discord.Embed(
        title="All {}'s commands".format(client.user.name),
        color=MAINCOLOR,
        description=description
    )
    help_e.set_thumbnail(url=client.user.avatar_url)
    help_e.set_footer(text="{}'s help command".format(client.user.name))

    await ctx.send(embed=help_e)

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

# cogs loader
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension("cogs.{}".format(filename[:-3]))


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

    if isinstance(error, commands.MissingPermissions):
        noperm_e = discord.Embed(
            description="You don't have the permissions to do this.",
            color=0xfe2419
        )
        await ctx.send(embed=noperm_e)


# run the bot
client.run(TOKEN)