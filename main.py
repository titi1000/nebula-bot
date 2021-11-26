import datetime
import json
import os

import discord
import toml
from discord.ext import commands, ipc

from core.db import db
from core.db_punishments import db_punishments
from core.db_user import db_users
from core.myjson import lang_json
from core.nebula_logging import nebula_logging
from core.others import is_it_owner, write_plugins_json

### Init

# import config
data = toml.load("config.toml")

TOKEN = data["token"]
MAINCOLOR = int(data["main_color"], 0)
ERRORCOLOR = int(data["error_color"], 0)
owner_id = data["owner_id"]

# import error channel id
with open("plugins/plugins.json") as data:
    error_channel_id = json.load(data)["customerrors"]["channel_id"]

# the bot itself
class Bot(commands.Bot):

    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix=db.get_prefix, help_command=None, case_insensitive=True, intents=intents, owner_id=owner_id)
        self.ipc = ipc.Server(self, secret_key=TOKEN)
        self.launch_time = datetime.datetime.utcnow()
        self.language = "en"

        with open("plugins/plugins.json") as plugins_json:
            self.data_plugins = json.load(plugins_json)

        self.load_cogs()
        self.load_plugins()
        self.add_commands()

        #self.ipc.start() -> we'll start it when the webserver will be up !


    # cogs loader
    def load_cogs(self):
        for filename in os.listdir("./cogs"):
            if filename[:-3] == "__init__":
                continue
            elif filename.endswith(".py"):
                self.load_extension(f"cogs.{filename[:-3]}")

    # Plugin loader
    def load_plugins(self):
        for plugin in self.data_plugins:
            if self.data_plugins[plugin]["activate"]:
                self.load_extension(self.data_plugins[plugin]["path"])

    async def on_ready(self):
        # init databases and update them
        db.init()
        db.update(self.guilds)
        db_users.init()
        db_punishments.update(self.guilds)

        print("Bot is ready.")
        print("Logged in as :")
        print(f"{self.user.name}#{self.user.discriminator}")
        print(self.user.id)
        print("--------- poweron ---------")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="?help to see all my commands"))
        nebula_logging.logger_bot.info(f"Bot logged as {self.user} | {self.user.id}")
    
    # bot get pinged
    async def on_message(self, message):
        await self.process_commands(message)
        prefix = db.get_prefix(self, message)
        if message.content in [f"<@{self.user.id}>", f"<@!{self.user.id}>"]:
            pinged_e = discord.Embed(
                description=lang_json.open_json()[self.language]["BOT_PINGED"].format(prefix, prefix),
                color=MAINCOLOR
            )

            await message.channel.send(embed=pinged_e)

    def add_commands(self):

        ### Cogs

        @self.group(invoke_without_command=True, aliases=["cog", "cogs"])
        @commands.check(is_it_owner)
        async def cog(self, ctx):
            cogs_str = "Here is the list of all cogs:\n"
            for filename in os.listdir("./cogs"):
                if filename[:-3] == "__init__":
                    continue
                elif filename.endswith(".py"):
                    cogs_str += f"- {filename[:-3].title()}\n"
            cogs_str += f"\nUse `{ctx.prefix}load <cogs name>` to load one."
            return await ctx.send(cogs_str)

        @cog.command(name="load")
        async def cog_load(self, ctx, cog_name:str):
            cog_name = cog_name.lower()
            try:
                self.load_extension(f"cogs.{cog_name}")
                await ctx.send(f"{cog_name.title()} cog well loaded!")
            except commands.ExtensionAlreadyLoaded:
                await ctx.send(f"Cog \"{cog_name.title()}\" already loaded.")
            except commands.ExtensionNotFound:
                await ctx.send(f"Cog \"{cog_name.title()}\" not found.")

        @cog.command(name="unload")
        async def unload(self, ctx, cog_name:str):
            cog_name = cog_name.lower()
            try:
                self.unload_extension(f"cogs.{cog_name}")
                await ctx.send(f"{cog_name.title()} cog well unloaded!")
            except commands.ExtensionNotLoaded:
                await ctx.send(f"Cog \"{cog_name.title()}\" already unloaded.")
            except commands.ExtensionNotFound:
                await ctx.send(f"Cog \"{cog_name.title()}\" not found.")


        ### Plugins
            
        @self.group(invoke_without_command=True, aliases=["plugin"])
        @commands.check(is_it_owner)
        async def plugins(ctx):
            plugins_list = "Here is the list of all plugins:\n"
            for plugin in self.data_plugins:
                plugins_list += f"- {plugin.title()}\n"
            plugins_list += f"Use `{ctx.prefix}plugin <plugin-name>` to see a plugin description!"
            return await ctx.send(plugins_list)

        @plugins.command()
        @commands.check(is_it_owner)
        async def enable(ctx, plugin:str):
            plugin = plugin.lower()
            if write_plugins_json("enable", plugin):
                try:
                    self.load_extension(self.data_plugins[plugin]["path"])
                    return await ctx.send(f"{plugin.title()} plugin well loaded!")
                except commands.ExtensionAlreadyLoaded: return await ctx.send(f"{plugin.title()} already loaded!")
            
            await ctx.send(f"Plugin \"{plugin}\" cannot be loaded... Maybe he doesn't exist.\nYou can see a list of all plugins by using the command `{ctx.prefix}plugin <plugin-name>`!")

        @plugins.command()
        @commands.check(is_it_owner)
        async def disable(ctx, plugin:str):
            plugin = plugin.lower()
            if plugin is None: return await ctx.send(f"Please provid the plugin you want to disable. You can see a list of all plugins by using the command `{ctx.prefix}plugin <plugin-name>`!")

            if write_plugins_json("disable", plugin):
                try:
                    self.unload_extension(self.data_plugins[plugin]["path"])
                    return await ctx.send(f"{plugin.title()} plugin well unloaded!")
                except commands.ExtensionNotLoaded: return await ctx.send(f"{plugin.title()} already unloaded!")
            
            await ctx.send(f"Plugin \"{plugin}\" cannot be unloaded... Maybe he doesn't exist.\nYou can see a list of all plugins by using the command `{ctx.prefix}plugin <plugin-name>`!")


    ### Error

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound): return
        
        elif isinstance(error, commands.BadArgument):
            badargument_e = discord.Embed(
                description=f"{str(error)}\nPlease provid a valid argument.",
                color=ERRORCOLOR
            )
            await ctx.send(embed=badargument_e)

        elif isinstance(error, commands.MissingPermissions):
            noperm_e = discord.Embed(
                description="You don't have the permissions to do this.",
                color=ERRORCOLOR
            )
            await ctx.send(embed=noperm_e)
        
        elif isinstance(error, commands.BotMissingPermissions):
            noperm_e = discord.Embed(
                description="I don't have the permissions to do this.",
                color=ERRORCOLOR
            )
            await ctx.send(embed=noperm_e)
        

    ### client join or leave a guild

    async def on_guild_join(self, guild):
        db_punishments.add_guild(guild.id)
        db.is_in_database_guild(guild_id=guild.id)

        join_e = discord.Embed(
            title=f"Thanks for adding {self.user.name}!",
            color=MAINCOLOR,
            description=f"Hi! You just add me in `{guild.name}`.\n\nYou can visit the online documentation [here](https://docs.nebulabot.info/) or use the `?help` command.\n\nThe default prefix is `?` but you can change it using `?prefix <new-prefix>`."
        )

        await guild.owner.send(embed=join_e)

    async def on_guild_remove(self, guild):
        db_punishments.remove_guild(guild.id)
        db.remove_guild(guild_id=guild.id)


# main function
def main():
    client = Bot()
    client.run(TOKEN)

        
# run the bot
if __name__ == "__main__": 
    main()
