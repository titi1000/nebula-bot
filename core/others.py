import discord
import toml
import json
import aiohttp
import functools
from discord.ext import commands
from core.db import db
from core.db_user import db_users

data = toml.load("config.toml")

owner_id = data["owner_id"]


# get a channel by his id
async def get_channel_by_id(guild, id):
    try:
        await guild.fetch_channels()
        channel = discord.utils.get(guild.channels, id=id)
        return channel
    except:
        return None

# write the plugins json
def write_plugins_json(action, plugin):
    if action == "enable":
        try:
            with open("plugins/plugins.json", "r") as plugins_json:
                data_plugins = json.load(plugins_json)

            data_plugins[plugin]["activate"] = True

            with open("plugins/plugins.json", "w") as plugins_json:
                json.dump(data_plugins, plugins_json, indent=4)

            return True
        except:
            return False

    elif action == "disable":
        try:
            with open("plugins/plugins.json", "r") as plugins_json:
                data_plugins = json.load(plugins_json)

            data_plugins[plugin]["activate"] = False

            with open("plugins/plugins.json", "w") as plugins_json:
                json.dump(data_plugins, plugins_json, indent=4)

            return True
        except:
            return False

# request to an an api
async def apirequest(link:str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as response:
                return await response.json()
    except:
        return None

# verify if command user is bot owner
def is_it_owner(ctx):
    return ctx.author.id in owner_id

# decorators who check if a channel is blacklist or no
def is_blacklisted(func):

    @functools.wraps(func)
    async def inner(ctx, *args, **kwargs):
        if not ctx.guild:
            return await func(ctx, *args, **kwargs)

        blacklisted = db.get_blacklisted(ctx.guild.id)
        blacklisted = blacklisted.split(" ")

        if str(ctx.channel.id) in blacklisted:
            return

        await func(ctx, *args, **kwargs)

    inner.__name__ = func.__name__
    return inner

def is_blacklisted_cogs(func):

    @functools.wraps(func)
    async def inner(self, ctx, *args, **kwargs):
        if not ctx.guild:
            return await func(self, ctx, *args, **kwargs)

        blacklisted = db.get_blacklisted(ctx.guild.id)
        blacklisted = blacklisted.split(" ")

        if str(ctx.channel.id) in blacklisted:
            return

        await func(self, ctx, *args, **kwargs)

    inner.__name__ = func.__name__
    return inner

# verify if command user is guild moderator (or admin)
def is_it_moderator(ctx):
    moderator_roles = db.get_moderator_roles(ctx.guild.id)
    member_roles_id = []
    for role in ctx.author.roles:
        member_roles_id.append(role.id)
    commons = list(set(moderator_roles).intersection(member_roles_id))
    if len(commons) > 0:
        return True
    else:
        if ctx.author.guild_permissions.administrator:
            return True
        else:
            return False

# add 1 to user's command counter 
async def user_cmd_count_up(ctx): # must place "@client.after_invoke(user_cmd_count_up)" on each command
    user_id = ctx.author.id
    db_users.is_in_database_user(user_id)
    db_users.add_to_counter(user_id, "command", 1)