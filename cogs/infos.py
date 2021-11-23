import discord
import datetime
import sys
import json
from discord.ext import commands
from main import MAINCOLOR
from core.others import is_blacklisted_cogs, is_it_owner
from core.db import db
from core.nebula_logging import report_error
from core.db_langs import db_lang

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
        lang = db.get_lang(ctx.guild.id)
        delta_uptime = datetime.datetime.utcnow() - self.client.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        await ctx.send(db_lang.getText(lang=lang, key="UPTIME").format(days=days, hours=hours, minutes=minutes, seconds=seconds))

    # bot infos
    @commands.command(aliases=["info"])
    @is_blacklisted_cogs
    async def infos(self, ctx):
        lang = db.get_lang(ctx.guild.id)
        infos_e = discord.Embed(
            title="Nebula Bot",
            description=db_lang.getText(lang=lang, key="INFO").format(system_version=sys.version[:5], discord_version=discord.__version__, guilds_count=len(self.client.guilds)),
            color=MAINCOLOR
        )
        infos_e.set_thumbnail(url=self.client.user.avatar_url)

        await ctx.send(embed=infos_e)

    # create bot invite
    @commands.command()
    @is_blacklisted_cogs
    async def invite(self, ctx):
        lang = db.get_lang(ctx.guild.id)
        invite = discord.utils.oauth_url(self.client.user.id, permissions=discord.Permissions(4227853527))
        invite_e = discord.Embed(
            title=f"{self.client.user.name}'s invite",
            description=db_lang.getText(lang=lang, key="INVITE").format(invite=invite),
            color=MAINCOLOR
        )
        invite_e.set_thumbnail(url=self.client.user.avatar_url)

        await ctx.send(embed=invite_e)

    # show prefix
    @commands.command()
    @is_blacklisted_cogs
    async def prefix(self, ctx, prefix=None):
        lang = db.get_lang(ctx.guild.id)
        if prefix is None:
            prefix_e = discord.Embed(
                    description=db_lang.getText(lang=lang, key="PREFIX").format(prefix=ctx.prefix),
                    color=MAINCOLOR
                )
            
            return await ctx.send(embed=prefix_e)
        
        if len(prefix) > 2: return await ctx.send(description=db_lang.getText(lang=lang, key="PREFIX_TOO_LONGER"))

        db.is_in_database_guild(ctx.guild.id)
        r = db.db_execute("UPDATE guilds SET `prefix` = %s WHERE `guild_id` = %s", (prefix, ctx.guild.id))
        if r[0] is False: return await report_error(self.client, ctx, r)
            
        await ctx.send(description=db_lang.getText(lang=lang, key="PREFIX_UPDATED").format(prefix=ctx.prefix))

    # help command
    @commands.command()
    @is_blacklisted_cogs
    async def help(self, ctx, command=None):
        lang = db.get_lang(ctx.guild.id)
        prefix = db.get_prefix(client=self.client, message=ctx.message)
        if command is None:
            description = f"""{db_lang.getText(lang=lang, key='HELP_DESCRIPTION').format(prefix=prefix)}\n
            **{self.emojis_dict['blurple_link']} Infos**\n`help`, `infos`, `prefix`, `support`, `website`, `documentation`\n
            **{self.emojis_dict['blurple_employee']} Utils**\n`emojiinfo`, `cloneemoji`, `profile`, `guild`, `emojis`, `membercount`, `quote`, `color`, `role`, `ping`, `announce`, `search`, `discrim`, `suggest`, `report`\n
            **{self.emojis_dict['blurple_star']} Fun**\n`giveaway`, `meme`, `cat`, `dog`, `8ball`, `avatar`, `reverse`, `say`\n
            **{self.emojis_dict['blurple_certifiedmoderator']} Mods only**\n`massrole`, `nick`, `ban`, `kick`, `warn`, `purge`, `punishments`, `delete-punishments`\n
            **{self.emojis_dict['blurple_settings']} Admin only**\n`tickettool`, `mod-logs`, `blacklist`, `welcome`, `welcome-channel`, `welcome-message`, `leave`, `leave-channel`, `leave-message`, `autorole`, `moderators`, `set-moderators`\n
            **{self.emojis_dict['blurple_search']} Logs** (These aren't commands)\n`on message delete`, `on message edit`, `on channel create/remove`"""

            help_e = discord.Embed(
                title=db_lang.getText(lang=lang, key='HELP_TITLE').format(bot_name=self.client.user.name),
                color=MAINCOLOR,
                description=description
            )
            help_e.add_field(name=f"{self.emojis_dict['plurple_link']} **Infos**", value="`help`, `infos`, `prefix`, `support`, `website`, `documentation`", inline=False)
            help_e.add_field(name=f"{self.emojis_dict['blurple_employee']} **Utils**", value="`emojiinfo`, `cloneemoji`, `profile`, `guild`, `emojis`, `membercount`, `quote`, `color`, `role`, `ping`, `announce`, `search`, `discrim`, `suggest`, `report`", inline=False)           
            help_e.add_field(name=f"{self.emojis_dict['blurple_star']} **Fun**", value="`giveaway`, `meme`, `cat`, `dog`, `8ball`, `avatar`, `reverse`, `say`", inline=False)
            help_e.add_field(name=f"{self.emojis_dict['blurple_certifiedmoderator']} **Mods only**", value="`massrole`, `nick`, `ban`, `kick`, `warn`, `purge`, `punishments`, `delete-punishments`", inline=False)
            help_e.add_field(name=f"{self.emojis_dict['blurple_settings']} **Admin only**", value="`tickettool`, `mod-logs`, `blacklist`, `welcome`, `welcome-channel`, `welcome-message`, `leave`, `leave-channel`, `leave-message`, `autorole`, `moderators`, `set-moderators`", inline=False)
            help_e.add_field(name=f"{self.emojis_dict['blurple_search']} **Logs** (These aren't commands)", value="`on message delete`, `on message edit`, `on channel create/remove`", inline=False)

            help_e.set_thumbnail(url=self.client.user.avatar_url)
            help_e.set_footer(text=getText(lang=lang, key='HELP_FOOTER').format(bot_name=self.client.user.name))

            return await ctx.send(embed=help_e)
        
        else:
            if command not in self.commands_infos: return await ctx.send(getText(lang=lang, key='HELP_NO_COMMAND_NAMED').format(command=command))
            command_infos = self.commands_infos["english"][command]
            description = f"{command_infos['description']}\nUsage:{command_infos['usage']}".format(ctx.prefix)
            for arg, desc in command_infos["args"].items(): description+=f"{arg} : {desc}"

            help_e = discord.Embed(
            title=getText(lang=lang, key='HELP_COMMAND_TITLE'),
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
    async def leave_guild(self, ctx, *, name):
        lang = db.get_lang(ctx.guild.id)
        guild = discord.utils.get(self.client.guilds, name=name)
        if guild:
            await guild.leave()
            return await ctx.send(getText(lang=lang, key='GUILD_LEFT').format(guild_name=name))
        
        return await ctx.send(getText(lang=lang, key='GUILD_NOT_FOUND').format(guild_name=name))

    # error if not owner of the bot
    @guilds.error
    @leave_guild.error
    async def guilds_error(self, ctx, error):
        return

    # restrict the bot usage
    @commands.group(aliases=["bl", "black-list"], invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def blacklist(self, ctx):
        lang = db.get_lang(ctx.guild.id)
        await ctx.send(getText(lang=lang, key='BLACKLIST').format(prefix=ctx.prefix))

    # add a channel to the blacklist
    @blacklist.command()
    @commands.has_permissions(administrator=True)
    async def add(self, ctx):
        lang = db.get_lang(ctx.guild.id)
        if len(ctx.message.channel_mentions) == 0: return await ctx.send(getText(lang=lang, key='BLACKLIST_ADD_PROVID_CHANNELS').format(prefix=ctx.prefix))
        
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
        await ctx.send(getText(lang=lang, key='BLACKLIST_ADD_PROVID_CHANNELS').format(channels=channels))

    # remove a channel from the blacklist
    @blacklist.command(aliases=["rm"])
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx):
        lang = db.get_lang(ctx.guild.id)
        if len(ctx.message.channel_mentions) == 0: return await ctx.send(getText(lang=lang, key='BLACKLIST_REMOVE_PROVID_CHANNELS'))
        
        blacklisted = db.get_blacklisted(ctx.guild.id)
        blacklisted = blacklisted.split(" ")
        for channel in ctx.message.channel_mentions:
            if str(channel.id) in blacklisted: blacklisted.remove(str(channel.id))

        blacklisted = " ".join(blacklisted)
        r = db.db_execute("UPDATE guilds SET `blacklisted` = %s WHERE `guild_id` = %s", (blacklisted,ctx.guild.id))
        if r[0] is False: return await report_error(self.client, ctx, r)
        channels = ""
        for channel in ctx.message.channel_mentions: channels += f"{channel.mention} "
        await ctx.send(getText(lang=lang, key='BLACKLIST_CHANNELS_REMOVED'))

    # view which channels are blacklisted
    @blacklist.command()
    @commands.has_permissions(administrator=True)
    async def view(self, ctx):
        lang = db.get_lang(ctx.guild.id)
        blacklisted = db.get_blacklisted(ctx.guild.id)
        blacklisted = blacklisted.split(" ")
        description = ""
        for channel in blacklisted:
            if channel == "": continue
            description += f"<#{channel}> "
        if description == "": description = getText(lang=lang, key='NO_CHANNEL_BLACKLISTED')

        blacklist_e = discord.Embed(
            title=getText(lang=lang, key='BLACKLISTED_CHANNELS'),
            description=description
        )
        await ctx.send(embed=blacklist_e)


def setup(client):
    client.add_cog(Infos(client))