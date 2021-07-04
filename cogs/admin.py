import discord
from discord.ext import commands
import sqlite3
import datetime
from core.db import db
from core.others import get_channel_by_id
from main import MAINCOLOR
from core.nebula_logging import nebula_logging

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

            r = db.db_execute("UPDATE guilds SET `welcome_id` = %s WHERE `guild_id` = %s", (channel.id, ctx.guild.id))
            if r[0]:
                return await ctx.send(f"Welcome channel {channel.mention} successfully set.")
            elif r[0] is False:
                return await ctx.send("An error was occured, a report has been sent.")

        elif action.lower() == "remove":
            r = db.db_execute("UPDATE guilds SET `welcome_id` = %s WHERE `guild_id` = %s", (None, ctx.guild.id))
            if r[0]:
                return await ctx.send("You don't have a welcome channel anymore.")
            elif r[0] is False:
                return await ctx.send("An error was occured, a report has been sent.")

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

            r = db.db_execute("UPDATE guilds SET `welcome_message` = %s WHERE `guild_id` = %s", (message, ctx.guild.id))
            if r[0]:
                return await ctx.send(f"Welcome message : \"{message}\" successfully set.")
            elif r[0] is False:
                return await ctx.send("An error was occured, a report has been sent.")

        elif action.lower() == "remove":
            r = db.db_execute("UPDATE guilds SET `welcome_message` = %s WHERE `guild_id` = %s", (None, ctx.guild.id))
            if r[0]:
                return await ctx.send("You don't have a welcome message anymore.")
            elif r[0] is False:
                return await ctx.send("An error was occured, a report has been sent.")
        
        else:
            return await ctx.send(f"Please provid a valid action :\n```{ctx.prefix}welcome-message <action> (<message>)```")

    # welcome message infos and simulation
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def welcome(self, ctx, action=None):
        db.is_in_database_guild(ctx.guild.id)
        if action is None:

            r_channel = db.welcome_channel(ctx.guild.id)
            r_message = db.welcome_message(ctx.guild.id)
            if r_channel[0] is False:
                return await ctx.send("An error was occured, a report has been sent.")
            if r_message[0] is False:
                return await ctx.send("An error was occured, a report has been sent.")
            if r_channel[1][0] is None or r_message[1][0] is None:
                return await ctx.send(f"Automatic welcome message isn't set in this guild.\n Use `{ctx.prefix}help` to know how to set it.")

            welcome_e = discord.Embed(
                title=f"{ctx.guild.name}'s welcome message",
                color=MAINCOLOR
            )
            welcome_e.add_field(name="Channel", value=f"<#{r_channel[1]}>", inline=True)
            welcome_e.add_field(name="Message", value=f"{r_message[1]}", inline=True)

            await ctx.send(embed=welcome_e)

        elif action.lower() == "simulate":

            r_channel = db.welcome_channel(ctx.guild.id)
            r_message = db.welcome_message(ctx.guild.id)
            if r_channel[0] is False:
                return await ctx.send("An error was occured, a report has been sent.")
            if r_message[0] is False:
                return await ctx.send("An error was occured, a report has been sent.")

            if r_channel[1][0] is None or r_message[1][0] is None:
                return await ctx.send("You don't have any automatic welcome message set.")

            try:
                result_channel = await get_channel_by_id(ctx.guild, int(r_channel[1][0]))
                await result_channel.send(r_message[1][0].format(server=ctx.guild, member=ctx.author))
            except:
                return await ctx.send("There is a problem...")

    # will be call when a member join
    async def member_joined_message(self, member):
        r_channel = db.welcome_channel(member.guild.id)
        r_message = db.welcome_message(member.guild.id)
        if r_channel[0] is False:
            return
        if r_message[0] is False:
            return

        if r_channel[1][0] is None or r_message[1][0] is None:
            return

        try:
            result_channel = await get_channel_by_id(member.guild, int(r_channel[1][0]))
            await result_channel.send(r_message[1][0].format(server=member.guild, member=member))
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

            r = db.db_execute("UPDATE guilds SET `leave_id` = %s WHERE `guild_id` = %s", (channel.id, ctx.guild.id))
            if r[0]:
                return await ctx.send(f"Leave channel {channel.mention} successfully set.")
            elif r[0] is False:
                return await ctx.send("An error was occured, a report has been sent.")

        elif action.lower() == "remove":
            r = db.db_execute("UPDATE guilds SET `leave_id` = %s WHERE `guild_id` = %s", (None, ctx.guild.id))
            if r[0]:
                return await ctx.send("You don't have a leave channel anymore.")
            elif r[0] is False:
                return await ctx.send("An error was occured, a report has been sent.")

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

            r= db.db_execute("UPDATE guilds SET `leave_message` = %s WHERE `guild_id` = %s", (message, ctx.guild.id))
            if r[0]:
                return await ctx.send(f"Leave message : \"{message}\" successfully set.")
            elif r[0] is False:
                return await ctx.send("An error was occured, a report has been sent.")

        elif action.lower() == "remove":
            r = db.db_execute("UPDATE guilds SET `leave_message` = %s WHERE `guild_id` = %s", (None, ctx.guild.id))
            if r[0]:
                return await ctx.send("You don't have a leave message anymore.")
            elif r[0] is False:
                return await ctx.send("An error was occured, a report has been sent.")
        
        else:
            return await ctx.send(f"Please provid a valid action :\n```{ctx.prefix}leave-message <action> (<message>)```")

    # leave message infos and simulation
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def leave(self, ctx, action=None):
        db.is_in_database_guild(ctx.guild.id)
        if action is None:

            r_channel = db.leave_channel(ctx.guild.id)
            r_message = db.leave_message(ctx.guild.id)
            if r_channel[0] is False:
                return await ctx.send("An error was occured, a report has been sent.")
            if r_message[0] is False:
                return await ctx.send("An error was occured, a report has been sent.")
            if r_channel[1][0] is None or r_message[1][0] is None:
                return await ctx.send(f"Automatic leave message isn't set in this guild.\n Use `{ctx.prefix}help` to know how to set it.")

            leave_e = discord.Embed(
                title=f"{ctx.guild.name}'s leave message",
                color=MAINCOLOR
            )
            leave_e.add_field(name="Channel", value=f"<#{r_channel[1][0]}>", inline=True)
            leave_e.add_field(name="Message", value=f"{r_message[1][0]}", inline=True)

            await ctx.send(embed=leave_e)

        elif action.lower() == "simulate":
            r_channel = db.leave_channel(ctx.guild.id)
            r_message = db.leave_message(ctx.guild.id)
            if r_channel[0] is False:
                return await ctx.send("An error was occured, a report has been sent.")
            if r_message[0] is False:
                return await ctx.send("An error was occured, a report has been sent.")

            if r_channel[1][0] is False or r_message[1][0] is False:
                return await ctx.send("You don't have any automatic welcome message set.")

            try:
                result_channel = await get_channel_by_id(ctx.guild, int(r_channel[1][0]))
                await result_channel.send(r_message[1][0].format(server=ctx.guild, member=ctx.author))
            except:
                return

    # call when a member leave a guild
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        r_channel = db.leave_channel(member.guild.id)
        r_message = db.leave_message(member.guild.id)
        if r_channel[0] is False:
            return
        if r_message[0] is False:
            return

        if r_channel[1][0] is False or r_message[1][0] is False:
            return

        try:
            result_channel = await get_channel_by_id(member.guild, int(r_channel[1][0]))
            await result_channel.send(r_message[1][0].format(server=member.guild, member=member))
        except:
            return

    ### autorole

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def autorole(self, ctx, action=None, role:discord.Role=None):
        if action is None:
            r_role_id = db.get_autorole(ctx.guild.id)
            if r_role_id[0] is False:
                return await ctx.send("An error was occured, a report has been sent.")
            if r_role_id[0] is False:
                return await ctx.send("An error was occured, a report has been sent.")

            if r_role_id[1][0] is None:
                return await ctx.send("You don't have any autorole set in this guild.")

            try:
                await ctx.guild.fetch_roles()
                autorole = ctx.guild.get_role(int(r_role_id[1][0]))
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

            r = db.db_execute("UPDATE guilds SET `autorole_ids` = %s WHERE `guild_id` = %s", (role.id, ctx.guild.id))
            if r[0]:
                return await ctx.send(f"Autorole : \"{role.name}\" successfully set.")
            elif r[0] is False:
                return await ctx.send("An error was occured, a report has been sent.")

        elif action.lower() == "remove":
            r = db.db_execute("UPDATE guilds SET `autorole_ids` = %s WHERE `guild_id` = %s", (None, ctx.guild.id))
            if r[0]:
                return await ctx.send("You don't have an autorole anymore.")
            elif r[0] is False:
                return await ctx.send("An error was occured, a report has been sent.")
        
        else:
            return await ctx.send(f"Please provid a valid action :\n```{ctx.prefix}autorole (<action>) (<message>)```")

    # call when a member join a guild
    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.member_joined_message(member) # to send a join message (if set)

        r_role_id = db.get_autorole(member.guild.id)
        if r_role_id[0] is False:
            return
        if r_role_id[1][0] is None:
            return

        try:
            await member.guild.fetch_roles()
            role = discord.utils.get(member.guild.roles, id=int(r_role_id[1][0]))
            await member.add_roles(role)
        except:
            return

    # send the list of moderator roles
    @commands.command(name = "moderators")
    @commands.has_permissions(administrator = True)
    async def moderators(self, ctx):
        guild_id = ctx.guild.id
        r_moderator_roles = db.get_moderator_roles(guild_id)
        if r_moderator_roles[0] is False:
            return await ctx.send("An error was occured, a report has been sent.")
        moderator_roles = r_moderator_roles[1][0]
        await ctx.guild.fetch_roles()
        string = ""
        for role in moderator_roles:
            string += f"{ctx.guild.get_role(role).mention}\n"
        if string != "":
            await ctx.send(string)
        else:
            await ctx.send("You are not select moderator roles")

    # manage the list of moderator roles
    @commands.command(name = "set-moderators")
    @commands.has_permissions(administrator = True)
    async def setmoderator(self, ctx, action:str=None, *, roles=None):
        actions = ["add", "rm", "rem", "remove"]
        if action in actions:
            if roles is not None:
                guild_id = ctx.guild.id
                resume = "Resume\n\n"
                for role in ctx.message.role_mentions:
                    r = db.manage_moderator_roles(guild_id, action, role.id)
                    if r[0] is False:
                        return await ctx.send("An error was occured, a report has been sent.")

                    if r[1][0] == 0 and r[1][1] == 0:
                        resume+=f"{role.mention} wasn't a moderator role\n"
                    elif r[1][0] == 0 and r[1][1] == 1:
                        resume+=f"{role.mention} is now a moderator role\n"
                    elif r[1][0] == 1 and r[1][1] == 0:
                        resume+=f"{role.mention} was a moderator role\n"
                    elif r[1][0] == 1 and r[1][1] == 1:
                        resume+=f"{role.mention} is already a moderator role\n"
                await ctx.send(resume)

            else:
                await ctx.send("Please provid roles")
        else:
            await ctx.send("Please provid a valid action (`rm`/`rem`/`remove` or `add`)")


def setup(client):
    client.add_cog(Admin(client))