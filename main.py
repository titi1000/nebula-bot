import discord
from discord.ext import commands, ipc
import json
import toml
import os
import datetime
from core.db import db
from core.db_user import db_users
from core.db_punishments import db_punishments
from core.myjson import lang_json
from core.others import is_it_owner, write_plugins_json

### Init

# import config
data = toml.load("config.toml")

TOKEN = data["token"]
MAINCOLOR = int(data["main_color"], 0)
ERRORCOLOR = int(data["error_color"], 0)
owner_id = data["owner_id"]

# the bot itself
class Bot(commands.Bot):

    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix=db.get_prefix, help_command=None, case_insensitive=True, intents=intents, owner_id=owner_id)
        #self.ipc = ipc.Server(self, secret_key=TOKEN)
        self.launch_time = datetime.datetime.utcnow()
        self.language = "en"

        with open("plugins/plugins.json") as plugins_json:
            self.data_plugins = json.load(plugins_json)

        self.load_cogs()
        self.load_plugins()
        self.add_commands()


    # cogs loader
    def load_cogs(self):
        for filename in os.listdir("./cogs"):
            if filename[:-3] == "__init__":
                continue
            if filename.endswith(".py"):
                self.load_extension(f"cogs.{filename[:-3]}")

    # Plugin loader
    def load_plugins(self):
        for plugin in self.data_plugins:
            if self.data_plugins[plugin]["activate"] is True:
                self.load_extension(self.data_plugins[plugin]["path"])

    async def on_ready(self):
        db.init()
        db_users.init()

        print("Bot is ready.")
        print("Logged in as :")
        print(f"{self.user.name}#{self.user.discriminator}")
        print(self.user.id)
        print("--------- poweron ---------")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="?help to see all my commands"))
    
    # bot get pinged
    async def on_message(self, message):
        await self.process_commands(message)
        prefix = db.get_prefix(self, message)
        if message.content == f"<@!{self.user.id}>":
            pinged_e = discord.Embed(
                description=lang_json.open_json()[self.language]["BOT_PINGED"].format(prefix, prefix),
                color=MAINCOLOR
            )

            await message.channel.send(embed=pinged_e)

    def add_commands(self):
        ### Cogs

        @self.command()
        @commands.check(is_it_owner)
        async def load(ctx, extension=None):
            if extension is None:
                cogs_str = "Here is the list of all cogs:\n"
                for filename in os.listdir("./cogs"):
                    if filename[:-3] == "__init__":
                        continue
                    if filename.endswith(".py"):
                        cogs_str += f"- {filename[:-3].title()}\n"
                cogs_str += f"\nUse `{ctx.prefix}load <cogs name>` to load one."
                return await ctx.send(cogs_str)
            
            try:
                self.load_extension(f"cogs.{extension.lower()}")
                await ctx.send(f"{extension.title()} cog well loaded!")
            except commands.ExtensionAlreadyLoaded:
                await ctx.send(f"Cog \"{extension}\" already loaded.")
            except commands.ExtensionNotFound:
                await ctx.send(f"Cog \"{extension}\" not found.")

        @self.command()
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
                self.unload_extension(f"cogs.{extension.lower()}")
                await ctx.send(f"{extension.title()} cog well unloaded!")
            except commands.ExtensionNotLoaded:
                await ctx.send(f"Cog \"{extension}\" already unloaded.")
            except commands.ExtensionNotFound:
                await ctx.send(f"Cog \"{extension}\" not found.")


        ### Plugins
            
        @self.group(invoke_without_command=True, aliases=["plugin"])
        @commands.check(is_it_owner)
        async def plugins(ctx, *, plugin=None):
            if plugin is None:
                plugins_list = "Here is the list of all plugins:\n"
                for plugin in self.data_plugins:
                    plugins_list += f"- {plugin.title()}\n"
                plugins_list += f"Use `{ctx.prefix}plugin <plugin-name>` to see a plugin description!"
                return await ctx.send(plugins_list)

            try:
                plugin_e = discord.Embed(
                    title=f"{plugin.title()} plugin description",
                    description=self.data_plugins[plugin.lower()]["description"]
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
                    self.load_extension(self.data_plugins[plugin]["path"])
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
                    self.unload_extension(self.data_plugins[plugin]["path"])
                    return await ctx.send(f"{plugin.title()} plugin well unloaded!")
                except commands.ExtensionNotLoaded:
                    return await ctx.send(f"{plugin.title()} already unloaded!")
            
            await ctx.send(f"Plugin \"{plugin}\" cannot be unloaded... Maybe he doesn't exist.")


    ### Error

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.BadArgument):
            badargument_e = discord.Embed(
                description=f"{str(error)}\nPlease provid a valid argument.",
                color=ERRORCOLOR
            )
            await ctx.send(embed=badargument_e)

        if isinstance(error, commands.MissingPermissions):
            noperm_e = discord.Embed(
                description="You don't have the permissions to do this.",
                color=ERRORCOLOR
            )
            await ctx.send(embed=noperm_e)
        

    ### client join or leave a guild

    async def on_guild_join(self, guild):
        db_punishments.add_guild(guild.id)
        result = db.db_fetchone("SELECT `guild_id` FROM guilds WHERE `guild_id` = %s", (guild.id,))
        if result[1] is None:
            db.db_execute("INSERT INTO guilds(`guild_id`) VALUES (%s)", (guild.id,))

        join_e = discord.Embed(
            title=f"Thanks for adding {self.user.name}!",
            color=MAINCOLOR,
            description=f"Hi! You just add me in `{guild.name}`.\n\nYou can visit the online documentation [here](https://docs.nebulabot.info/) or use the `?help` command.\n\nThe default prefix is `?` but you can change it using `?prefix <new-prefix>`."
        )

        await guild.owner.send(embed=join_e)

    async def on_guild_remove(self, guild):
        db_punishments.remove_guild(guild.id)
        result = db.db_fetchone("SELECT `guild_id` FROM guilds WHERE `guild_id` = %s", (guild.id,))
        if result[1] is not None:
            db.db_execute("DELETE FROM guilds WHERE `guild_id` = %s", (guild.id,))

# main function
def main():

    client = Bot()
    client.run(TOKEN)


### WEB SERVER
"""
@client.event
async def on_ipc_error(endpoint, error):
        print(endpoint, "raised", error)


@client.ipc.route()
async def get_member_count(data):
    guild = await client.fetch_guild(data.guild_id)

    return len(await guild.fetch_members(limit=1000).flatten()), guild.name"""
        
# run the bot
if __name__ == "__main__":
    #client.ipc.start()
    main()
