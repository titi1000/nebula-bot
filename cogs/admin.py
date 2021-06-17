import discord
from discord.ext import commands
import sqlite3
import datetime
from core.db import db
from core.others import get_channel_by_id
from main import MAINCOLOR

class Admin(commands.Cog):

    def __init__(self, client):
        self.client = client
        print("Admin cog well loaded.")

    ### join

    # welcome channel
    @commands.command(aliases=["wc", "welcome-channel"])
    @commands.has_permissions(administrator=True)
    async def welcome_channel(self, ctx, action=None, channel:discord.TextChannel=None):
        if action is None and channel is None:
            return await ctx.send(f"Please provid all require parameters :\n```{ctx.prefix}welcome-channel <action> <channel>```\n(Notice that <channel> depends of your action)")

        db.is_in_database_guild(ctx.guild.id)
        if action.lower() == "add": 
            if channel is None:
                return await ctx.send(f"Please provid a valid channel :\n```{ctx.prefix}welcome-channel add <channel>```")

            db.cursor.execute("UPDATE guilds SET welcome_id = ? WHERE guild_id = ?", (channel.id, ctx.guild.id))
            db.commit()
            return await ctx.send(f"Welcome channel {channel.mention} successfully set.")

        elif action.lower() == "remove":
            db.cursor.execute("UPDATE guilds SET welcome_id = ? WHERE guild_id = ?", (None, ctx.guild.id))
            db.commit()
            return await ctx.send("You don't have a welcome channel anymore.")

        else:
            return await ctx.send(f"Please provid a valid action :\n```{ctx.prefix}welcome-channel <action> (<channel>)```")

    # welcome message
    @commands.command(aliases=["wm", "welcome-message"])
    @commands.has_permissions(administrator=True)
    async def welcome_message(self, ctx, action=None, *, message=None):
        if action is None and message is None:
            return await ctx.send(f"Please provid all require parameters :\n```{ctx.prefix}welcome-message <action> <message>```\n(Notice that <message> depends of your action)")

        db.is_in_database_guild(ctx.guild.id)
        if action.lower() == "add":
            if message is None:
                return await ctx.send(f"Please provid a message :\n```{ctx.prefix}welcome-message add <message>```")

            db.cursor.execute("UPDATE guilds SET welcome_message = ? WHERE guild_id = ?", (message, ctx.guild.id))
            db.commit()
            return await ctx.send(f"Welcome message : \"{message}\" successfully set.")

        elif action.lower() == "remove":
            db.cursor.execute("UPDATE guilds SET welcome_message = ? WHERE guild_id = ?", (None, ctx.guild.id))
            db.commit()
            return await ctx.send("You don't have a welcome message anymore.")
        
        else:
            return await ctx.send(f"Please provid a valid action :\n```{ctx.prefix}welcome-message <action> (<message>)```")

    # welcome message infos and simulation
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def welcome(self, ctx, action=None):
        db.is_in_database_guild(ctx.guild.id)
        if action is None:

            channel_id = db.welcome_channel(ctx.guild.id)
            message = db.welcome_message(ctx.guild.id)
            if channel_id is False or message is False:
                return await ctx.send(f"Automatic welcome message isn't set in this guild.\n Use `{ctx.prefix}help` to know how to set it.")

            welcome_e = discord.Embed(
                title=f"{ctx.guild.name}'s welcome message",
                color=MAINCOLOR
            )
            welcome_e.add_field(name="Channel", value=f"<#{channel_id}>", inline=True)
            welcome_e.add_field(name="Message", value=f"{message}", inline=True)

            await ctx.send(embed=welcome_e)

        elif action.lower() == "simulate":
            channel_id = db.welcome_channel(ctx.guild.id)
            message = db.welcome_message(ctx.guild.id)

            if channel_id is False or message is False:
                return await ctx.send("You don't have any automatic welcome message set.")

            try:
                result_channel = await get_channel_by_id(ctx.guild, int(channel_id))
                await result_channel.send(message.format(server=ctx.guild, member=ctx.author))
            except:
                return

    # will be call when a member join
    async def member_joined_message(self, member):
        channel_id = db.welcome_channel(member.guild.id)
        message = db.welcome_message(member.guild.id)

        if channel_id is False or message is False:
            return

        try:
            result_channel = await get_channel_by_id(member.guild, int(channel_id))
            await result_channel.send(message.format(server=member.guild, member=member))
        except:
            return

    ### leave

    # welcome channel
    @commands.command(aliases=["lc", "leave-channel"])
    @commands.has_permissions(administrator=True)
    async def leave_channel(self, ctx, action=None, channel:discord.TextChannel=None):
        if action is None and channel is None:
            return await ctx.send(f"Please provid all require parameters :\n```{ctx.prefix}leave-channel <action> <channel>```\n(Notice that <channel> depends of your action)")

        db.is_in_database_guild(ctx.guild.id)
        if action.lower() == "add": 
            if channel is None:
                return await ctx.send(f"Please provid a valid channel :\n```{ctx.prefix}leave-channel add <channel>```")

            db.cursor.execute("UPDATE guilds SET leave_id = ? WHERE guild_id = ?", (channel.id, ctx.guild.id))
            db.commit()
            return await ctx.send(f"Leave channel {channel.mention} successfully set.")

        elif action.lower() == "remove":
            db.cursor.execute("UPDATE guilds SET leave_id = ? WHERE guild_id = ?", (None, ctx.guild.id))
            db.commit()
            return await ctx.send("You don't have a leave channel anymore.")

        else:
            return await ctx.send(f"Please provid a valid action :\n```{ctx.prefix}leave-channel <action> (<channel>)```")

    # leave message
    @commands.command(aliases=["lm", "leave-message"])
    @commands.has_permissions(administrator=True)
    async def leave_message(self, ctx, action=None, *, message=None):
        if action is None and message is None:
            return await ctx.send(f"Please provid all require parameters :\n```{ctx.prefix}leave-message <action> <message>```\n(Notice that <message> depends of your action)")

        db.is_in_database_guild(ctx.guild.id)
        if action.lower() == "add":
            if message is None:
                return await ctx.send(f"Please provid a message :\n```{ctx.prefix}leave-message add <message>```")

            db.cursor.execute("UPDATE guilds SET leave_message = ? WHERE guild_id = ?", (message, ctx.guild.id))
            db.commit()
            return await ctx.send(f"Leave message : \"{message}\" successfully set.")

        elif action.lower() == "remove":
            db.cursor.execute("UPDATE guilds SET leave_message = ? WHERE guild_id = ?", (None, ctx.guild.id))
            db.commit()
            return await ctx.send("You don't have a leave message anymore.")
        
        else:
            return await ctx.send(f"Please provid a valid action :\n```{ctx.prefix}leave-message <action> (<message>)```")

    # leave message infos and simulation
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def leave(self, ctx, action=None):
        db.is_in_database_guild(ctx.guild.id)
        if action is None:

            channel_id = db.leave_channel(ctx.guild.id)
            message = db.leave_message(ctx.guild.id)
            if channel_id is False or message is False:
                return await ctx.send(f"Automatic leave message isn't set in this guild.\n Use `{ctx.prefix}help` to know how to set it.")

            leave_e = discord.Embed(
                title=f"{ctx.guild.name}'s leave message",
                color=MAINCOLOR
            )
            leave_e.add_field(name="Channel", value=f"<#{channel_id}>", inline=True)
            leave_e.add_field(name="Message", value=f"{message}", inline=True)

            await ctx.send(embed=leave_e)

        elif action.lower() == "simulate":
            channel_id = db.leave_channel(ctx.guild.id)
            message = db.leave_message(ctx.guild.id)

            if channel_id is False or message is False:
                return await ctx.send("You don't have any automatic welcome message set.")

            try:
                result_channel = await get_channel_by_id(ctx.guild, int(channel_id))
                await result_channel.send(message.format(server=ctx.guild, member=ctx.author))
            except:
                return

    # call when a member leave a guild
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel_id = db.leave_channel(member.guild.id)
        message = db.leave_message(member.guild.id)

        if channel_id is False or message is False:
            return

        try:
            result_channel = await get_channel_by_id(member.guild, int(channel_id))
            await result_channel.send(message.format(server=member.guild, member=member))
        except:
            return

    ### autorole

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def autorole(self, ctx, action=None, role:discord.Role=None):
        if action is None:
            role_id = db.get_autorole(ctx.guild.id)

            if role_id is False:
                return await ctx.send("You don't have any autorole set in this guild.")

            try:
                await ctx.guild.fetch_roles()
                autorole = ctx.guild.get_role(int(role_id))
                autorole_e = discord.Embed(
                    title=f"{ctx.guild.name}'s autorole",
                    description="All the new members will get this role when joining.",
                    color=MAINCOLOR
                )
                autorole_e.add_field(name="Role", value=autorole.mention)
                return await ctx.send(embed=autorole_e)
            except:
                return await ctx.send("There is a problem...")

        if action.lower() == "add":
            if role is None:
                return await ctx.send(f"Please provid a role :\n```{ctx.prefix}autorole add <role>```")

            db.cursor.execute("UPDATE guilds SET autorole_id = ? WHERE guild_id = ?", (role.id, ctx.guild.id))
            db.commit()
            return await ctx.send(f"Autorole : \"{role.name}\" successfully set.")

        elif action.lower() == "remove":
            db.cursor.execute("UPDATE guilds SET autorole_id = ? WHERE guild_id = ?", (None, ctx.guild.id))
            db.commit()
            return await ctx.send("You don't have an autorole anymore.")
        
        else:
            return await ctx.send(f"Please provid a valid action :\n```{ctx.prefix}autorole (<action>) (<message>)```")

    # call when a member join a guild
    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.member_joined_message(member) # to send a join message (if set)

        role_id = db.get_autorole(member.guild.id)

        if role_id is False:
            return
        
        try:
            await member.guild.fetch_roles()
            role = discord.utils.get(member.guild.roles, id=int(role_id))
            await member.add_roles(role)
        except:
            return


def setup(client):
    client.add_cog(Admin(client))