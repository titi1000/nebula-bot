import discord
from discord.ext import commands, ipc
import json
import toml
import os
import datetime
from core.db import db
from core.myjson import lang_json
from core.others import is_it_owner, write_plugins_json, is_blacklisted

### Init

# import commands file
with open("commands.json") as commands_json:
    commands_infos = json.load(commands_json)
    
# temporaire en attendant le choix de la langue 
language = "en" 

# import config
data = toml.load("config.toml")

TOKEN = data["token"]
MAINCOLOR = int(data["main_color"], 0)
ERRORCOLOR = int(data["error_color"], 0)
owner_id = data["owner_id"]

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix=db.get_prefix, help_command=None, case_insensitive=True, intents=intents, owner_id=owner_id)
client.ipc = ipc.Server(client, secret_key=TOKEN)
client.launch_time = datetime.datetime.utcnow()
client.is_blacklisted = is_blacklisted # decorator for commands blacklist

@client.event
async def on_ready():
    db.init()

    print("Bot is ready.")
    print("Logged in as :")
    print(f"{client.user.name}#{client.user.discriminator}")
    print(client.user.id)
    print("------------------")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="?help to see all my commands"))

### Commands

# bot get pinged
@client.event
async def on_message(message):
    await client.process_commands(message)
    prefix = db.get_prefix(client, message)
    if message.content == f"<@!{client.user.id}>":
        pinged_e = discord.Embed(
            description=lang_json.open_json()[language]["BOT_PINGED"].format(prefix, prefix),
            color=MAINCOLOR
        )

        await message.channel.send(embed=pinged_e)

### Cogs

@client.command()
@commands.check(is_it_owner)
async def load(ctx, extension=None):
    if extension is None:
        cogs_str = "Here is the list of all cogs:\n"
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                cogs_str += f"- {filename[:-3].title()}\n"
        cogs_str += f"\nUse `{ctx.prefix}load <cogs name>` to load one."
        return await ctx.send(cogs_str)
    
    try:
        client.load_extension(f"cogs.{extension.lower()}")
        await ctx.send(f"{extension.title()} cog well loaded!")
    except commands.ExtensionAlreadyLoaded:
        await ctx.send(f"Cog \"{extension}\" already loaded.")
    except commands.ExtensionNotFound:
        await ctx.send(f"Cog \"{extension}\" not found.")

@client.command()
@commands.check(is_it_owner)
async def unload(ctx, extension=None):
    if extension is None:
        cogs_str = "Here is the list of all cogs:\n"
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                cogs_str += f"- {filename[:-3].title()}\n"
        cogs_str += f"\nUse `{ctx.prefix}unload <cogs name>` to unload one."
        return await ctx.send(cogs_str)

    try:
        client.unload_extension(f"cogs.{extension.lower()}")
        await ctx.send(f"{extension.title()} cog well unloaded!")
    except commands.ExtensionNotLoaded:
        await ctx.send(f"Cog \"{extension}\" already unloaded.")
    except commands.ExtensionNotFound:
        await ctx.send(f"Cog \"{extension}\" not found.")


# cogs loader
for filename in os.listdir("./cogs"):
    if filename[:-3] == "__init__":
        continue
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")


### Plugins

with open("plugins/plugins.json") as plugins_json:
    data_plugins = json.load(plugins_json)
    
@client.group(invoke_without_command=True, aliases=["plugin"])
@commands.check(is_it_owner)
async def plugins(ctx, *, plugin=None):
    if plugin is None:
        plugins_list = "Here is the list of all plugins:\n"
        for plugin in data_plugins:
            plugins_list += f"- {plugin.title()}\n"
        plugins_list += f"Use `{ctx.prefix}plugin <plugin-name>` to see a plugin description!"
        return await ctx.send(plugins_list)

    try:
        plugin_e = discord.Embed(
            title=f"{plugin.title()} plugin description",
            description=data_plugins[plugin.lower()]["description"]
        )
        await ctx.send(embed=plugin_e)
    except:
        await ctx.send(f"Plugin \"{plugin}\" not found...")


@plugins.command()
@commands.check(is_it_owner)
async def enable(ctx, *, plugin=None):
    if plugin is None:
        return await ctx.send(f"Please provid the plugin you want to enable. You can see a list of all plugins by using the command `{ctx.prefix}plugin <plugin-name>`!")

    if write_plugins_json("enable", plugin) is True:
        try:
            client.load_extension(data_plugins[plugin]["path"])
            return await ctx.send(f"{plugin.title()} plugin well loaded!")
        except commands.ExtensionAlreadyLoaded:
            return await ctx.send(f"{plugin.title()} already loaded!")
    
    await ctx.send(f"Plugin \"{plugin}\" cannot be loaded... Maybe he doesn't exist.")


@plugins.command()
@commands.check(is_it_owner)
async def disable(ctx, *, plugin=None):
    if plugin is None:
        return await ctx.send(f"Please provid the plugin you want to disable. You can see a list of all plugins by using the command `{ctx.prefix}plugin <plugin-name>`!")

    if write_plugins_json("disable", plugin) is True:
        try:
            client.unload_extension(data_plugins[plugin]["path"])
            return await ctx.send(f"{plugin.title()} plugin well unloaded!")
        except commands.ExtensionNotLoaded:
            return await ctx.send(f"{plugin.title()} already unloaded!")
    
    await ctx.send(f"Plugin \"{plugin}\" cannot be unloaded... Maybe he doesn't exist.")


# Plugin loader
for plugin in data_plugins:
    if data_plugins[plugin]["activate"] is True:
        client.load_extension(data_plugins[plugin]["path"])


### Error

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    
    if isinstance(error, commands.BadArgument):
        badargument_e = discord.Embed(
            description=f"{str(error)}\nPlease provid a valid argument.",
            color=ERRORCOLOR
        )
        await ctx.send(embed=badargument_e)

    """if isinstance(error, commands.CheckFailure):
        nodm_e = discord.Embed(
            description="Command failed.",
            color=ERRORCOLOR
        )
        await ctx.send(embed=nodm_e)"""

    if isinstance(error, commands.MissingPermissions):
        noperm_e = discord.Embed(
            description="You don't have the permissions to do this.",
            color=ERRORCOLOR
        )
        await ctx.send(embed=noperm_e)
    

### client join or leave a guild

@client.event
async def on_guild_join(guild):
    db.cursor.execute("SELECT guild_id FROM guilds WHERE guild_id = ?", (guild.id,))
    result = db.cursor.fetchone()
    if result is None:
        db.cursor.execute("INSERT INTO guilds(guild_id) VALUES (?)", (guild.id,))
        db.commit()

    join_e = discord.Embed(
        title=f"Thanks for adding {client.user.name}!",
        color=MAINCOLOR,
        description=f"Hi! You just add me in `{guild.name}`.\n\nYou can visit the online documentation [here](https://docs.nebulabot.info/) or use the `?help` command.\n\nThe default prefix is `?` but you can change it using `?prefix <new-prefix>`."
    )

    await guild.owner.send(embed=join_e)

@client.event
async def on_guild_remove(guild):
    db.cursor.execute("SELECT guild_id FROM guilds WHERE guild_id = ?", (guild.id,))
    result = db.cursor.fetchone()
    if result is not None:
        db.cursor.execute("DELETE FROM guilds WHERE guild_id = ?", (guild.id,))
        db.commit()

### WEB SERVER

@client.event
async def on_ipc_error(endpoint, error):
        print(endpoint, "raised", error)


@client.ipc.route()
async def get_member_count(data):
    guild = await client.fetch_guild(data.guild_id)

    return len(await guild.fetch_members(limit=1000).flatten()), guild.name

# stop the bot
@commands.check(is_it_owner)
@client.command(name = "stop")
async def stop(ctx):
    await ctx.bot.logout()
        
# run the bot
if __name__ == "__main__":
    client.ipc.start()
    client.run(TOKEN)
