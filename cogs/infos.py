import discord
import datetime
import sys
import json
from discord.ext import commands
from main import MAINCOLOR
from core.others import is_blacklisted_cogs, is_it_owner
from core.db import db
from core.nebula_logging import report_error

class Infos(commands.Cog):

    def __init__(self, client):
        self.client = client

        # import commands file
        with open("commands.json") as commands_json:
            self.commands_infos = json.load(commands_json)

        # import emojis file
        with open("others.json") as others_json:
            self.emojis_dict = json.load(others_json)["emojis"]

    # uptime
    @commands.command(aliases=["up"])
    @is_blacklisted_cogs
    async def uptime(self, ctx):
        delta_uptime = datetime.datetime.utcnow() - self.client.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        await ctx.send(f"Bot up since {days}d, {hours}h, {minutes}m, {seconds}s")

    # bot infos
    @commands.command(aliases=["info"])
    @is_blacklisted_cogs
    async def infos(self, ctx):
        infos_e = discord.Embed(
            title="Nebula Bot",
            description=f"Created by [titi#1000](https://github.com/titi1000) and [voXrey#8866](https://github.com/voXrey)\nUsing python version {sys.version[:5]}\nUsing discord.py version {discord.__version__}\nCurrently in {len(self.client.guilds)} guild(s)\n",
            color=MAINCOLOR
        )
        infos_e.set_thumbnail(url=self.client.user.avatar_url)

        await ctx.send(embed=infos_e)

    # create bot invite
    @commands.command()
    @is_blacklisted_cogs
    async def invite(self, ctx):
        invite = discord.utils.oauth_url(self.client.user.id, permissions=discord.Permissions(4227853527))
        invite_e = discord.Embed(
            title=f"{self.client.user.name}'s invite",
            description=f"[Click here]({invite}) to invite the bot!",
            color=MAINCOLOR
        )
        invite_e.set_thumbnail(url=self.client.user.avatar_url)

        await ctx.send(embed=invite_e)

    # show prefix
    @commands.command()
    @is_blacklisted_cogs
    async def prefix(self, ctx, prefix=None):
        if prefix is None:
            prefix_e = discord.Embed(
                    description=f"Hi, my prefix is `{ctx.prefix}`, but you can change it by using the `{ctx.prefix}prefix <new-prefix>` command.\nUse `{ctx.prefix}help` to see all my commands",
                    color=MAINCOLOR
                )
            
            return await ctx.send(embed=prefix_e)
        
        if len(prefix) > 2: return await ctx.send("The new prefix may not be longer than 2 characters!")

        db.is_in_database_guild(ctx.guild.id)
        r = db.db_execute("UPDATE guilds SET `prefix` = %s WHERE `guild_id` = %s", (prefix, ctx.guild.id))
        if r[0] is False: return await report_error(self.client, ctx, r)
            
        await ctx.send(f"New prefix will now be `{prefix}`")

    # help command
    @commands.command()
    @is_blacklisted_cogs
    async def help(self, ctx, command=None):
        if command is None:
            description = f"""Use `{ctx.prefix}<command>` to run a command or `{ctx.prefix}help <command>` to have more details, or to see how to use a specific command.\n
            **{self.emojis_dict['plurple_link']} Infos**\n`help`, `infos`, `prefix`, `support`, `website`, `documentation`\n
            **{self.emojis_dict['blurple_employee']} Utils**\n`emojiinfo`, `cloneemoji`, `profile`, `guild`, `emojis`, `membercount`, `quote`, `color`, `role`, `ping`, `announce`, `search`, `discrim`, `suggest`, `report`\n
            **{self.emojis_dict['blurple_star']} Fun**\n`giveaway`, `meme`, `cat`, `dog`, `8ball`, `avatar`, `reverse`, `say`\n
            **{self.emojis_dict['blurple_certifiedmoderator']} Mods only**\n`massrole`, `nick`, `ban`, `kick`, `warn`, `purge`, `punishments`, `delete-punishments`\n
            **{self.emojis_dict['blurple_settings']} Admin only**\n`tickettool`, `mod-logs`, `blacklist`, `welcome`, `welcome-channel`, `welcome-message`, `leave`, `leave-channel`, `leave-message`, `autorole`, `moderators`, `set-moderators`\n
            **{self.emojis_dict['blurple_search']} Logs** (These aren't commands)\n`on message delete`, `on message edit`, `on channel create/remove`"""

            help_e = discord.Embed(
                title=f"All {self.client.user.name}'s commands",
                color=MAINCOLOR,
                description=description
            )
            help_e.set_thumbnail(url=self.client.user.avatar_url)
            help_e.set_footer(text=f"{self.client.user.name}'s help command")

            return await ctx.send(embed=help_e)
        
        else:
            if command not in self.commands_infos: return await ctx.send(f"No command named `{command}`. Please retry!")
            command_infos = self.commands_infos[command]
            description = f"{command_infos['description']}\n{command_infos['usage']}".format(ctx.prefix)
            for arg, desc in command_infos["args"].items(): description+=f"{arg} : {desc}"

            help_e = discord.Embed(
            title=f"{command}'s usage",
            color=MAINCOLOR,
            description=description
            )
            return await ctx.send(embed=help_e)

    # show bot guilds (need to be owner of the bot to run the command)
    @commands.group(invoke_without_command=True)
    @commands.check(is_it_owner)
    async def guilds(self, ctx):
        guilds_list = ""
        self.client.fetch_guilds(limit=100)
        n = 1
        for guild in self.client.guilds:
            guilds_list += f"{n}. {guild.name}\n"
            n += 1

        await ctx.send(guilds_list)

    # leave a guild (need to be owner of the bot to run the command)
    @guilds.command()
    @commands.check(is_it_owner)
    async def leave(self, ctx, *, name):
        guild = discord.utils.get(self.client.guilds, name=name)
        if guild:
            await guild.leave()
            return await ctx.send(f"Guild \"{name}\" left!")
        
        return await ctx.send(f"Guild \"{name}\" not found... Please retry")

    # error if not owner of the bot
    @guilds.error
    @leave.error
    async def guilds_error(self, ctx, error):
        return

    # restrict the bot usage
    @commands.group(aliases=["bl", "black-list"], invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def blacklist(self, ctx):
        await ctx.send(f"Use `{ctx.prefix}blacklist add/remove #channel-1 #channel-2` to add or remove some channels from the blacklist (you can provid how many channels you want).\n\nUse `{ctx.prefix}blacklist view` to see which channels are blacklisted on your server.")

    # add a channel to the blacklist
    @blacklist.command()
    @commands.has_permissions(administrator=True)
    async def add(self, ctx):
        if len(ctx.message.channel_mentions) == 0: return await ctx.send(f"Please provid all channels you want to blacklist. Usage :\n```{ctx.prefix}blacklist add #channel-1 #channel-2 #channel...```(You can provid how many channels you want)\n\nUse `{ctx.prefix}blacklist view` to see what are the blacklisted channels in the server.")
        
        blacklisted = db.get_blacklisted(ctx.guild.id)
        blacklisted = blacklisted.split(" ")
        for channel in ctx.message.channel_mentions:
            if str(channel.id) in blacklisted: continue
            blacklisted.append(str(channel.id))

        blacklisted = " ".join(blacklisted)
        r = db.db_execute("UPDATE guilds SET `blacklisted` = %s WHERE `guild_id` = %s", (blacklisted,ctx.guild.id))
        if r[0] is False: return await report_error(self.client, ctx, r)
        
        channels = ""
        for channel in ctx.message.channel_mentions: channels += f"{channel.mention} "
        await ctx.send(f"{channels} added to the channels blacklist!")

    # remove a channel from the blacklist
    @blacklist.command(aliases=["rm"])
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx):
        if len(ctx.message.channel_mentions) == 0: return await ctx.send(f"Please provid all channels you want to remove from the blacklist. Usage :\n```{ctx.prefix}blacklist remove #channel-1 #channel-2 #channel...```(You can provid how many channels you want)\n\nUse `{ctx.prefix}blacklist view` to see what are the blacklisted channels in the server.")
        
        blacklisted = db.get_blacklisted(ctx.guild.id)
        blacklisted = blacklisted.split(" ")
        for channel in ctx.message.channel_mentions:
            if str(channel.id) in blacklisted: blacklisted.remove(str(channel.id))

        blacklisted = " ".join(blacklisted)
        r = db.db_execute("UPDATE guilds SET `blacklisted` = %s WHERE `guild_id` = %s", (blacklisted,ctx.guild.id))
        if r[0] is False: return await report_error(self.client, ctx, r)
        channels = ""
        for channel in ctx.message.channel_mentions: channels += f"{channel.mention} "
        await ctx.send(f"{channels} removed from the channels blacklist!")

    # view which channels are blacklisted
    @blacklist.command()
    @commands.has_permissions(administrator=True)
    async def view(self, ctx):
        blacklisted = db.get_blacklisted(ctx.guild.id)
        blacklisted = blacklisted.split(" ")
        description = ""
        for channel in blacklisted:
            if channel == "": continue
            description += f"<#{channel}> "
        if description == "": description = "No channel blacklisted..."

        blacklist_e = discord.Embed(
            title=f"{ctx.guild.name} blacklisted channels",
            description=description
        )
        await ctx.send(embed=blacklist_e)


def setup(client):
    client.add_cog(Infos(client))