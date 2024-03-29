import discord
from discord.ext import commands
import datetime
from core.db import db
from core.others import get_channel_by_id
from core.nebula_logging import report_error, report_error_with_message, report_error_with_channel

class Logs(commands.Cog):

    def __init__(self, client):
        self.client = client
        print("Logs cog well loaded.")

    # set logs channel
    @commands.group(aliases=["mod-logs", "mod-channel", "ml"], invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def mod_logs(self, ctx, channel:discord.TextChannel=None):
        if channel is None:
            r_channel_id = db.logs_channel(ctx.guild.id)
            if r_channel_id[0] is False: return await report_error(self.client, ctx, r_channel_id)

            channel_id = r_channel_id[1][0]
            if channel_id is None: return await ctx.send(f"No logs channel set in this guild. Use `{ctx.prefix}mod-logs <#channel>` to set one.")
            return await ctx.send(f"Current logs channel on this guild : <#{channel_id}>\nUse `{ctx.prefix}mod-logs remove` to remove the actual  one")

        db.is_in_database_guild(ctx.guild.id)
        r = db.db_execute("UPDATE guilds SET `logs_id` = %s WHERE `guild_id` = %s", (channel.id, ctx.guild.id))
        if r[0]: return await ctx.send(f"New mod channel will be {channel.mention}")
        return await report_error(self.client, ctx, r)

    @mod_logs.command(aliases=["rm"])
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx):
        db.is_in_database_guild(ctx.guild.id)
        r = db.db_execute("UPDATE guilds SET `logs_id` = %s WHERE `guild_id` = %s", (None, ctx.guild.id))
        if r[0]: return await ctx.send(f"No more logs channel set on this guild.")
        return await report_error(self.client, ctx, r)

    ## Logs

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.guild is None or message.author == self.client.user: return
        r_channel_id = db.logs_channel(message.guild.id)
        if r_channel_id[0] is False: return await report_error_with_message(self.client, message, r_channel_id, "on_message_delete")

        channel_id = r_channel_id[1][0]
        if channel_id is None: return
        if message.content == "": return

        try:
            channel = await get_channel_by_id(message.guild, int(channel_id))
            deleted_e = discord.Embed(
                title=f"Message deleted in #{message.channel.name}",
                description=message.content,
                timestamp=datetime.datetime.utcnow(),
                color=0xff0000
            )
            deleted_e.set_author(name=f"{message.author.name}#{message.author.discriminator}", icon_url=message.author.avatar_url)
            deleted_e.set_footer(text=f"ID : {message.id}")

            await channel.send(embed=deleted_e)
        except: return

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.guild is None or before.author == self.client.user: return
        r_channel_id = db.logs_channel(before.guild.id)
        if r_channel_id[0] is False: return await report_error_with_message(self.client, before, r_channel_id, "on_message_edit")

        channel_id = r_channel_id[1][0]
        if channel_id is None: return

        try:
            if before.content == "" or after.content == "": return
            if before.content == after.content: return
            channel = await get_channel_by_id(before.guild, int(channel_id))
            edited_e = discord.Embed(
                title=f"Message edited in #{before.channel.name}",
                description=f"**Before:** {before.content}\n\n**After:** {after.content}",
                timestamp=datetime.datetime.utcnow(),
                color=0xff0000
            )
            edited_e.set_author(name=f"{before.author.name}#{before.author.discriminator}", icon_url=before.author.avatar_url)
            edited_e.set_footer(text=f"ID : {before.id}")

            await channel.send(embed=edited_e)
        except: return

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        r_channel_id = db.logs_channel(channel.guild.id)
        if r_channel_id[0] is False: return await report_error_with_channel(self.client, channel, r_channel_id, "on_guild_channel_create")

        channel_id = r_channel_id[1][0]
        if channel_id is None: return

        try:
            logs_channel = await get_channel_by_id(channel.guild, int(channel_id))

            channel_created_e = discord.Embed(
                title="Channel created",
                color=0x0ef535,
                timestamp=datetime.datetime.utcnow()
            )
            channel_created_e.add_field(name="Name", value=channel.name, inline=False)
            channel_created_e.add_field(name="Mention", value=channel.mention, inline=False)
            channel_created_e.add_field(name="ID", value=channel.id, inline=False)
            
            await logs_channel.send(embed=channel_created_e)

        except: return

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        r_channel_id = db.logs_channel(channel.guild.id)
        if r_channel_id[0] is False: return await report_error_with_channel(self.client, channel, r_channel_id, "on_guild_channel_delete")

        channel_id = r_channel_id[1][0]
        if channel_id is None: return

        try:
            logs_channel = await get_channel_by_id(channel.guild, int(channel_id))

            channel_created_e = discord.Embed(
                title="Channel deleted",
                color=0xff0000,
                timestamp=datetime.datetime.utcnow()
            )
            channel_created_e.add_field(name="Name", value=channel.name, inline=False)
            channel_created_e.add_field(name="ID", value=channel.id, inline=False)

            await logs_channel.send(embed=channel_created_e)

        except: return



def setup(client):
    client.add_cog(Logs(client))