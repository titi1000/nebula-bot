import discord
from discord.ext import commands
import json
import toml
import os
import datetime
import sys
from core.db import db
from core.others import is_it_owner, write_plugins_json, is_blacklisted

### Init

# import commands file
with open("commands.json") as commands_json:
    commands_infos = json.load(commands_json)

# import config
data = toml.load("config.toml")

TOKEN = data["token"]
MAINCOLOR = int(data["main_color"], 0)
ERRORCOLOR = int(data["error_color"], 0)
owner_id = data["owner_id"]

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix=db.get_prefix, help_command=None, case_insensitive=True, intents=intents, owner_id=owner_id)
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
            description=f"Hi! My prefix is `{prefix}` but you can change it by using the `prefix` command.\nUse `{prefix}help` to see all my commands",
            color=MAINCOLOR
        )

        await message.channel.send(embed=pinged_e)

# uptime
@client.command(aliases=["up"])
@client.is_blacklisted
async def uptime(ctx):
    delta_uptime = datetime.datetime.utcnow() - client.launch_time
    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    await ctx.send(f"Bot up since {days}d, {hours}h, {minutes}m, {seconds}s")

# bot infos
@client.command(aliases=["info"])
@client.is_blacklisted
async def infos(ctx):
    infos_e = discord.Embed(
        title="Nebula Bot",
        description=f"Created by [titi#1000](https://github.com/titi1000)\nUsing python version {sys.version[:5]}\nUsing discord.py version {discord.__version__}\nCurrently in {len(client.guilds)} guild(s)\n",
        color=MAINCOLOR
    )
    infos_e.set_thumbnail(url=client.user.avatar_url)

    await ctx.send(embed=infos_e)

# create bot invite
@client.command()
@client.is_blacklisted
async def invite(ctx):
    invite = discord.utils.oauth_url(client.user.id, permissions=discord.Permissions(3963616455))
    invite_e = discord.Embed(
        title=f"{client.user.name}'s invite",
        description=f"[Click here]({invite}) to invite the bot!",
        color=MAINCOLOR
    )
    invite_e.set_thumbnail(url=client.user.avatar_url)

    await ctx.send(embed=invite_e)

# show prefix
@client.command()
@client.is_blacklisted
async def prefix(ctx, prefix=None):
    if prefix is None:
        prefix_e = discord.Embed(
                description=f"Hi, my prefix is `{ctx.prefix}`, but you can change it by using the `{ctx.prefix}prefix <new-prefix>` command.\nUse `{ctx.prefix}help` to see all my commands",
                color=MAINCOLOR
            )
        
        return await ctx.send(embed=prefix_e)
    
    if len(prefix) > 2:
        return await ctx.send("The new prefix may not be longer than 2 characters!")

    db.is_in_database_guild(ctx.guild.id)
    db.cursor.execute("UPDATE guilds SET prefix = ? WHERE guild_id = ?", (prefix, ctx.guild.id))
    db.commit()
    await ctx.send(f"New prefix will now be `{prefix}`")

# help command
@client.command()
@client.is_blacklisted
async def help(ctx, command=None):
    if command is None:
        description = f"""Use `{ctx.prefix}<command>` to run a command or `{ctx.prefix}help <command>` to have more details, or to see how to use a specific command.\n
        **Infos**\n`help`, `infos`, `prefix`, `support`, `website`, `documentation`\n
        **Utils**\n`emojiinfo`, `cloneemoji`, `profile`, `guild`, `emojis`, `membercount`, `quote`, `color`, `role`, `ping`, `announce`, `search`, `discrim`\n
        **Fun**\n`meme`, `cat`, `dog`, `8ball`, `avatar`, `reverse`, `say`\n
        **Mods only**\n`massrole`, `nick`, `ban`, `kick`, `purge`\n
        **Admin only**\n`mod-logs`, `blacklist`, `welcome`, `welcome-channel`, `welcome-message`, `leave`, `leave-channel`, `leave-message`, `autorole`\n
        **Logs** (These aren't commands)\n`on message delete`, `on message edit`, `on channel create/remove`"""

        help_e = discord.Embed(
            title=f"All {client.user.name}'s commands",
            color=MAINCOLOR,
            description=description
        )
        help_e.set_thumbnail(url=client.user.avatar_url)
        help_e.set_footer(text=f"{client.user.name}'s help command")

        await ctx.send(embed=help_e)
    
    else:
        try:
            command_description = commands_infos[command]
            help_e = discord.Embed(
            title=f"{command}'s usage",
            color=MAINCOLOR,
            description=command_description.format(ctx.prefix)
            )

            await ctx.send(embed=help_e)

        except:
            return await ctx.send(f"No command named `{command}`. Please retry!")


# show bot guilds (need to be owner of the bot to run the command)
@client.group(invoke_without_command=True)
@commands.check(is_it_owner)
async def guilds(ctx):
    guilds_list = ""
    client.fetch_guilds(limit=100)
    n = 1
    for guild in client.guilds:
        guilds_list += f"{n}. {guild.name}\n"
        n += 1

    await ctx.send(guilds_list)

# leave a guild (need to be owner of the bot to run the command)
@guilds.command()
@commands.check(is_it_owner)
async def leave(ctx, *, name):
    guild = discord.utils.get(client.guilds, name=name)
    if guild:
        await guild.leave()
        return await ctx.send(f"Guild \"{name}\" left!")
    else:
        return await ctx.send(f"Guild \"{name}\" not found... Please retry")

# error if not owner of the bot
@guilds.error
@leave.error
async def guilds_error(ctx, error):
    return

# restrict the bot usage
@client.group(aliases=["bl", "black-list"], invoke_without_command=True)
@commands.has_permissions(administrator=True)
async def blacklist(ctx):
    await ctx.send(f"Use `{ctx.prefix}blacklist add/remove #channel-1 #channel-2` to add or remove some channels from the blacklist (you can provid how many channels you want).\n\nUse `{ctx.prefix}blacklist view` to see which channels are blacklisted on your server.")

# add a channel to the blacklist
@blacklist.command()
@commands.has_permissions(administrator=True)
async def add(ctx):
    if len(ctx.message.channel_mentions) == 0:
        return await ctx.send(f"Please provid all channels you want to blacklist. Usage :\n```{ctx.prefix}blacklist add #channel-1 #channel-2 #channel...```(You can provid how many channels you want)\n\nUse `{ctx.prefix}blacklist view` to see what are the blacklisted channels in the server.")
    
    blacklisted = db.get_blacklisted(ctx.guild.id)
    blacklisted = blacklisted.split(" ")
    for channel in ctx.message.channel_mentions:
        if str(channel.id) in blacklisted:
            continue
        blacklisted.append(str(channel.id))

    blacklisted = " ".join(blacklisted)
    db.cursor.execute("UPDATE guilds SET blacklisted = ? WHERE guild_id = ?", (blacklisted,ctx.guild.id))
    db.commit()

    channels = ""
    for channel in ctx.message.channel_mentions:
        channels += f"{channel.mention} "
    await ctx.send(f"{channels} added to the channels blacklist!")

# remove a channel from the blacklist
@blacklist.command(aliases=["rm"])
@commands.has_permissions(administrator=True)
async def remove(ctx):
    if len(ctx.message.channel_mentions) == 0:
        return await ctx.send(f"Please provid all channels you want to remove from the blacklist. Usage :\n```{ctx.prefix}blacklist remove #channel-1 #channel-2 #channel...```(You can provid how many channels you want)\n\nUse `{ctx.prefix}blacklist view` to see what are the blacklisted channels in the server.")
    
    blacklisted = db.get_blacklisted(ctx.guild.id)
    blacklisted = blacklisted.split(" ")
    for channel in ctx.message.channel_mentions:
        if str(channel.id) in blacklisted:
            blacklisted.remove(str(channel.id))

    blacklisted = " ".join(blacklisted)
    db.cursor.execute("UPDATE guilds SET blacklisted = ? WHERE guild_id = ?", (blacklisted,ctx.guild.id))
    db.commit()

    channels = ""
    for channel in ctx.message.channel_mentions:
        channels += f"{channel.mention} "
    await ctx.send(f"{channels} removed from the channels blacklist!")

# view which channels are blacklisted
@blacklist.command()
@commands.has_permissions(administrator=True)
async def view(ctx):
    blacklisted = db.get_blacklisted(ctx.guild.id)
    blacklisted = blacklisted.split(" ")
    description = ""
    for channel in blacklisted:
        if channel == "":
            continue
        description += f"<#{channel}> "
    if description == "":
        description = "No channel blacklisted..."

    blacklist_e = discord.Embed(
        title=f"{ctx.guild.name} blacklisted channels",
        description=description
    )
    await ctx.send(embed=blacklist_e)


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

# run the bot
client.run(TOKEN)