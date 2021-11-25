import discord
from core.db import db
from core.nebula_logging import report_error, report_error_with_member
from core.others import get_channel_by_id
from discord.ext import commands
from main import MAINCOLOR


class Admin(commands.Cog):

    def __init__(self, client):
        self.client = client
        print("Admin cog well loaded.")

    ### join

    # welcome channel commands
    # group command
    @commands.group(aliases=["wc", "welcome-channel"])
    @commands.has_permissions(administrator=True)
    async def welcome_channel(self, ctx):
        db.is_in_database_guild(ctx.guild.id) # check if the guild is in database and add them if not
        if ctx.invoked_subcommand is None: ctx.send(f"Please provid a valid subcommand : `add` or `remove`") # if no subcommand was given

    # 'add' welcome_channel subcommand
    @welcome_channel.command(name="add")
    async def welcome_channel_add(self, ctx, channel:discord.TextChannel):
        db.is_in_database_guild(ctx.guild.id) # check if the guild is in database and add them if not
        r = db.db_execute("UPDATE guilds SET `welcome_id` = %s WHERE `guild_id` = %s", (channel.id, ctx.guild.id)) # send a request to set welcome channel for this guild
        if r[0]: return await ctx.send(f"Welcome channel {channel.mention} successfully set.") # if the request has worked
        return await report_error(self.client, ctx, r) # if the request has not worked

    # 'remove' welcome_channel subcommand
    @welcome_channel.command(name="remove")
    async def welcome_channel_remove(self, ctx):
        db.is_in_database_guild(ctx.guild.id) # check if the guild is in database and add them if not
        r = db.db_execute("UPDATE guilds SET `welcome_id` = %s WHERE `guild_id` = %s", (None, ctx.guild.id)) # send a request to remove welcome channel for this guild
        if r[0]: return await ctx.send("You don't have a welcome channel anymore.") # if the request has worked
        return await report_error(self.client, ctx, r) # if the request has not worked


    # welcome message commands
    # group command
    @commands.group(aliases=["wm", "welcome-message"])
    @commands.has_permissions(administrator=True)
    async def welcome_message(self, ctx):
        db.is_in_database_guild(ctx.guild.id) # check if the guild is in database and add them if not
        if ctx.invoked_subcommand is None: ctx.send(f"Please provid a valid subcommand : `add` or `remove`") # if no subcommand was given

    # 'add' welcome_message subcommand
    @welcome_message.command(name="add")
    async def welcome_message_add(self, ctx, *, message:str):
        db.is_in_database_guild(ctx.guild.id) # check if the guild is in database and add them if not
        r = db.db_execute("UPDATE guilds SET `welcome_message` = %s WHERE `guild_id` = %s", (message, ctx.guild.id)) # send a request to set welcome message for this guild
        if r[0]: return await ctx.send(f"Welcome message : \"{message}\" successfully set.") # if the request has worked
        return await report_error(self.client, ctx, r) # if the request has not worked

    # 'remove' welcome_message subcommand
    @welcome_message.command(name="remove")
    async def welcome_message_remove(self, ctx):
        db.is_in_database_guild(ctx.guild.id) # check if the guild is in database and add them if not
        r = db.db_execute("UPDATE guilds SET `welcome_message` = %s WHERE `guild_id` = %s", (None, ctx.guild.id)) # send a request to remove welcome message for this guild
        if r[0]: return await ctx.send("You don't have a welcome message anymore.") # if the request has worked
        return await report_error(self.client, ctx, r) # if the request has not worked


    # welcome message infos and simulation commands
    # group command
    @commands.group(aliases=["w", "welcome"], invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def welcome(self, ctx):
        db.is_in_database_guild(ctx.guild.id) # check if the guild is in database and add them if not
        r_channel = db.welcome_channel(ctx.guild.id) # send a request to get welcome channel
        r_message = db.welcome_message(ctx.guild.id) # send a request to get welcome message
        if r_channel[0] is False: return await report_error(self.client, ctx, r_channel) # if the request for welcome channel has not worked report error
        if r_message[0] is False:  return await report_error(self.client, ctx, r_message) # if the request for welcome message has not worked report error
        if r_channel[1][0] is None or r_message[1][0] is None: # if welcome message system is not set in this guild
            return await ctx.send(f"Automatic welcome message isn't set in this guild.\n Use `{ctx.prefix}help` to know how to set it.")
        
        # if the welcome message system is set in this guild
        welcome_e = discord.Embed(
            title=f"{ctx.guild.name}'s welcome message",
            color=MAINCOLOR
        )
        welcome_e.add_field(name="Channel", value=f"<#{r_channel[1][0]}>", inline=True)
        welcome_e.add_field(name="Message", value=f"{r_message[1][0]}", inline=True)

        await ctx.send(embed=welcome_e)
    
    # 'simulate' welcome subcommand
    @welcome.command(name="simulate")
    async def welcome_simulate(self, ctx):
        db.is_in_database_guild(ctx.guild.id) # check if the guild is in database and add them if not
        r_channel = db.welcome_channel(ctx.guild.id) # send a request to get welcome channel
        r_message = db.welcome_message(ctx.guild.id) # send a request to get welcome message
        if r_channel[0] is False: return await report_error(self.client, ctx, r_channel) # if the request for welcome channel has not worked report error
        if r_message[0] is False: return await report_error(self.client, ctx, r_message) # if the request for welcome message has not worked report error
        if r_channel[1][0] is None or r_message[1][0] is None: # if welcome message system is not set in this guild
            return await ctx.send("You don't have any automatic welcome message set.")

        # if the welcome message system is set in this guild
        try:
            result_channel = await get_channel_by_id(ctx.guild, int(r_channel[1][0])) # get welcome channel with his id
            await result_channel.send(r_message[1][0].format(server=ctx.guild, member=ctx.author)) # send a simulation of welcome message
        except: return await ctx.send("There is a problem...")


    # will be call when a member join
    async def member_joined_message(self, member):
        r_channel = db.welcome_channel(member.guild.id) # send a request to get welcome channel
        r_message = db.welcome_message(member.guild.id) # send a request to get welcome message
        if r_channel[0] is False: return await report_error_with_member(self.client, member, r_channel, "member_joined_message") # if the request for welcome channel has not worked report error
        if r_message[0] is False: return await report_error_with_member(self.client, member, r_message, "member_joined_message") # if the request for welcome message has not worked report error
        if r_channel[1][0] is None or r_message[1][0] is None: return # if welcome message system is not set in this guild

        # if the welcome message system is set in this guild
        try:
            result_channel = await get_channel_by_id(member.guild, int(r_channel[1][0])) # get welcome channel with his id
            await result_channel.send(r_message[1][0].format(server=member.guild, member=member)) # send the welcome message
        except: return



    ### leave

    # leave channel commands
    # group command
    @commands.group(aliases=["lc", "leave-channel"])
    @commands.has_permissions(administrator=True)
    async def leave_channel(self, ctx):
        db.is_in_database_guild(ctx.guild.id) # check if the guild is in database and add them if not
        if ctx.invoked_subcommand is None: ctx.send(f"Please provid a valid subcommand : `add` or `remove`") # if no subcommand was given
    
    # 'add' leave_channel subcommand
    @leave_channel.command(name="add")
    async def leave_channel_add(self, ctx, channel:discord.TextChannel):
        db.is_in_database_guild(ctx.guild.id) # check if the guild is in database and add them if not
        r = db.db_execute("UPDATE guilds SET `leave_id` = %s WHERE `guild_id` = %s", (channel.id, ctx.guild.id)) # send a request to set welcome channel for this guild
        if r[0]: return await ctx.send(f"Leave channel {channel.mention} successfully set.") # if the request has worked
        return await report_error(self.client, ctx, r) # if the request has not worked

    # 'remove' leave_channel subcommand
    @leave_channel.command(name="remove")
    async def leave_channel_remove(self, ctx):
        db.is_in_database_guild(ctx.guild.id) # check if the guild is in database and add them if not
        r = db.db_execute("UPDATE guilds SET `leave_id` = %s WHERE `guild_id` = %s", (None, ctx.guild.id)) # send a request to remove welcome channel for this guild
        if r[0]: return await ctx.send("You don't have a leave channel anymore.") # if the request has worked
        return await report_error(self.client, ctx, r) # if the request has not worked


    # leave message commands
    # group command
    @commands.group(aliases=["lm", "leave-message"])
    @commands.has_permissions(administrator=True)
    async def leave_message(self, ctx):
        db.is_in_database_guild(ctx.guild.id) # check if the guild is in database and add them if not
        if ctx.invoked_subcommand is None: ctx.send(f"Please provid a valid subcommand : `add` or `remove`") # if no subcommand was given

    # 'add' leave_message subcommand
    @leave_message.command(name="add")
    async def leave_message_add(self, ctx, *, message:str):
        db.is_in_database_guild(ctx.guild.id) # check if the guild is in database and add them if not
        r = db.db_execute("UPDATE guilds SET `leave_message` = %s WHERE `guild_id` = %s", (message, ctx.guild.id)) # send a request to set leave message for this guild
        if r[0]: return await ctx.send(f"leave message : \"{message}\" successfully set.") # if the request has worked
        return await report_error(self.client, ctx, r) # if the request has not worked

    # 'remove' leave_message subcommand
    @leave_message.command(name="remove")
    async def leave_message_remove(self, ctx):
        db.is_in_database_guild(ctx.guild.id) # check if the guild is in database and add them if not
        r = db.db_execute("UPDATE guilds SET `leave_message` = %s WHERE `guild_id` = %s", (None, ctx.guild.id)) # send a request to remove leave message for this guild
        if r[0]: return await ctx.send("You don't have a leave message anymore.") # if the request has worked
        return await report_error(self.client, ctx, r) # if the request has not worked


    # leave message infos and simulation commands
    # group command
    @commands.group(aliases=["l", "leave"], invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def leave(self, ctx):
        db.is_in_database_guild(ctx.guild.id) # check if the guild is in database and add them if not
        r_channel = db.leave_channel(ctx.guild.id) # send a request to get leave channel
        r_message = db.leave_message(ctx.guild.id) # send a request to get leave message
        if r_channel[0] is False: return await report_error(self.client, ctx, r_channel) # if the request for leave channel has not worked report error
        if r_message[0] is False:  return await report_error(self.client, ctx, r_message) # if the request for leave message has not worked report error
        if r_channel[1][0] is None or r_message[1][0] is None: # if leave message system is not set in this guild
            return await ctx.send(f"Automatic leave message isn't set in this guild.\n Use `{ctx.prefix}help` to know how to set it.")
        
        # if the leave message system is set in this guild
        leave_e = discord.Embed(
            title=f"{ctx.guild.name}'s leave message",
            color=MAINCOLOR
        )
        leave_e.add_field(name="Channel", value=f"<#{r_channel[1][0]}>", inline=True)
        leave_e.add_field(name="Message", value=f"{r_message[1][0]}", inline=True)

        await ctx.send(embed=leave_e)
    
    # 'simulate' leave subcommand
    @leave.command(name="simulate")
    async def leave_simulate(self, ctx):
        db.is_in_database_guild(ctx.guild.id) # check if the guild is in database and add them if not
        r_channel = db.leave_channel(ctx.guild.id) # send a request to get leave channel
        r_message = db.leave_message(ctx.guild.id) # send a request to get leave message
        if r_channel[0] is False: return await report_error(self.client, ctx, r_channel) # if the request for leave channel has not worked report error
        if r_message[0] is False: return await report_error(self.client, ctx, r_message) # if the request for leave message has not worked report error
        if r_channel[1][0] is None or r_message[1][0] is None: # if leave message system is not set in this guild
            return await ctx.send("You don't have any automatic leave message set.")

        # if the leave message system is set in this guild
        try:
            result_channel = await get_channel_by_id(ctx.guild, int(r_channel[1][0])) # get leave channel with his id
            await result_channel.send(r_message[1][0].format(server=ctx.guild, member=ctx.author)) # send a simulation of leave message
        except: return await ctx.send("There is a problem...")


    # call when a member leave a guild
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        db.is_in_database_guild(member.guild.id) # check if the guild is in database and add them if not
        r_channel = db.leave_channel(member.guild.id) # send a request to get leave channel
        r_message = db.leave_message(member.guild.id) # send a request to get leave message
        if r_channel[0] is False: return await report_error_with_member(self.client, member, r_channel, "on_member_remove") # if the request for leave channel has not worked report error
        if r_message[0] is False: return report_error_with_member(self.client, member, r_message, "on_member_remove") # if the request for leave message has not worked report error
        if r_channel[1][0] is None or r_message[1][0] is None: return # if leave message system is not set in this guild

        # if the leave message system is set in this guild
        try:
            result_channel = await get_channel_by_id(member.guild, int(r_channel[1][0])) # get leave channel with his id
            await result_channel.send(r_message[1][0].format(server=member.guild, member=member)) # send the leave message
        except: return



    ### autorole

    # autorole commands
    # group command
    @commands.group(aliases=["autoroles", "auto-roles", "auto-role"], invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def autorole(self, ctx):
        db.is_in_database_guild(member.guild.id) # check if the guild is in database and add them if not
        
        r_role_id = db.get_autorole(ctx.guild.id) # send a request to get autoroles
        if r_role_id[0] is False: return await report_error(self.client, ctx, r_role_id) # if request has not worked report
        if r_role_id[1][0] is None: return await ctx.send("You don't have any autorole set in this guild.") # if guild not have autorole
        roles_id = r_role_id[1][0] # string of autorole list

        try:
            await ctx.guild.fetch_roles()
            autorole_e = discord.Embed(
                title=f"{ctx.guild.name}'s autorole(s)",
                color=MAINCOLOR
            )

            autoroles = ""
            for role in roles_id.split(" "): # for each role id in the role list
                if role == "": continue # prevent from bug
                try:
                    autorole = ctx.guild.get_role(int(role)) # get guild's role
                    autoroles += f"{autorole.mention} "
                except:
                    autoroles += f"@deleted_role " ### It will be necessary to remove the roles deleted from the db

            autorole_e.description = f"All the new members will get the following role(s) when joining:\n\n{autoroles}"
            return await ctx.send(embed=autorole_e) # send the list of autoroles

        except Exception as e:
            return await ctx.send("There is a problem...") # if there is a problem

    # 'add' autorole subcommand
    @autorole.commands(name="add")
    async def autorole_add(self, ctx, autorole:discord.Role):
        db.is_in_database_guild(member.guild.id) # check if the guild is in database and add them if not

        role_list = db.get_autorole(ctx.guild.id) # send request to get guild's autoroles
        if role_list[0] is False: return await report_error(self.client, ctx, role_list) # if request has not worked

        role_list = role_list[1] # get the role_list string from tuple request
        if role_list is None: # create role_list if it's empty and add new autorole
            role_list = str(autorole.id)
        else:
            role_list += f"{autorole.id}" # add new autorole in autorole list

        r = db.db_execute("UPDATE guilds SET `autorole_ids` = %s WHERE `guild_id` = %s", (role_list, ctx.guild.id)) # send request to set autorole list in db
        if r[0] is False: return await report_error(self.client, ctx, r) # if request has not worked
        return await ctx.send(f"Autorole: '{autorole.name}' successfully set.") # send reply

    # 'remove' autorole subcommand
    @autorole.commands(aliases=["remove", "rm", "rem"])
    async def autorole_remove(self, ctx, autorole:discord.Role):
        db.is_in_database_guild(member.guild.id) # check if the guild is in database and add them if not

        role_list = db.get_autorole(ctx.guild.id) # send request to get guild's autoroles
        if role_list[0] is False: return await report_error(self.client, ctx, role_list) # if request has not worked
        if role_list[1] is None: return await ctx.send("You don't have any autoroles set.") # if guild has not setted autorole

        role_list = role_list[1] # get the role_list string from tuple request
        role_list = role_list.split(" ") # split autoroles's id in string
        
        # if autorole is not in setted autoroles
        if str(autorole.id) not in role_list: return await ctx.send("None of the roles you gave match with your actual auto-roles...")

        role_list.remove(str(autorole.id)) # remove autorole from autorole list

        r = db.db_execute("UPDATE guilds SET `autorole_ids` = %s WHERE `guild_id` = %s", (role.id, ctx.guild.id)) # send request to set autorole list in db
        if r[0] is False: return await report_error(self.client, ctx, r) # if request has not worked
        return await ctx.send(f"Autorole: '{autorole.name}' successfully removed.") # send reply

    # 'clear' autorole subcommand
    @autorole.commands(name="clear")
    async def autorole_clear(self, ctx):
        db.is_in_database_guild(member.guild.id) # check if the guild is in database and add them if not

        r = db.db_execute("UPDATE guilds SET `autorole_ids` = %s WHERE `guild_id` = %s", (None, ctx.guild.id)) # send request to clear autorole list
        if r[0] is False: return await report_error(self.client, ctx, r) # if request has not worked
        return await ctx.send("Autorole list has been cleared") # send reply
    

    # call when a member join a guild
    @commands.Cog.listener()
    async def on_member_join(self, member):
        db.is_in_database_guild(member.guild.id) # check if the guild is in database and add them if not
        await self.member_joined_message(member) # to send a join message (if set)
        
        r_roles_id = db.get_autorole(member.guild.id) # send request to get autorole list
        if r_roles_id[0] is False: return await report_error_with_member(self.client, member, r_roles_id, "on_member_joined") # if request has not worked
        if r_roles_id[1][0] is None: return # if guild not have autorole
        
        await member.guild.fetch_roles() # fetch roles from API to cache

        roles_id = r_roles_id[1][0] # get the role_list string from tuple request
        for role_id in roles_id.split(" "): # for each role_id in autoroles list
            try:
                role = discord.utils.get(member.guild.roles, id=int(role_id)) # get role with id
                await member.add_roles(role, reason="Autorole system") # add role to member
            except: continue


    ### Moderators

    # moderator command
    # moderator group
    @commands.group(aliases=["moderator", "moderators"])
    @commands.has_permissions(administrator = True)
    async def moderators(self, ctx):
        guild_id = ctx.guild.id 
        db.is_in_database_guild(guild_id) # check if the guild is in database and add them if not

        r_moderator_roles = db.get_moderator_roles(guild_id) # send request to get moderator's roles list
        if r_moderator_roles[0] is False: return await report_error(self.client, ctx, r_moderator_roles) # if request has not worked
            
        moderator_roles_id_str = r_moderator_roles[1] # get moderators string list from tuple
        await ctx.guild.fetch_roles() # fetch roles from API to cache

        moderator_roles_id = moderator_roles_id_str.split(" ") # get list of str(id) from string
        moderator_roles = [] # create list for Role objects
        for moderator_role_id in moderator_roles_id: # for each str(role_id)
            try:
                moderator_roles.append(ctx.guild.get_role(int(moderator_role_id))) # get role and append in role list
            except: pass

        description = "" # create a string description
        for role in moderator_roles: description += f"{ctx.guild.get_role(role).mention} " # add roles mentions to description
        if description == "": return await ctx.send("You are not select moderator roles") # if guild has not moderator roles
        await ctx.send(embed=discord.Embed(description=description, color=MAINCOLOR)) # send reply with moderators's roles's mention

    # 'add' moderators subcommand 
    @moderators.command(name="add")
    async def moderators_add(self, ctx, role:discord.Role):
        guild_id = ctx.guild.id
        db.is_in_database_guild(guild_id) # check if the guild is in database and add them if not
        
        r = db.add_moderator_role(guild_id, str(role.id)) # send request to add role to moderators's roles list
        if r[0] is False: return await report_error(self.client, ctx, r) # if request has not worked

        await ctx.send(f"Role '{role.name}' has been added to moderators's roles's list.") # send reply

    # 'remove' moderators subcommand
    @moderators.command(aliases=["remove", "rem", "pop", "delete"])
    async def moderators_remove(self, ctx, role:discord.Role):
        guild_id = ctx.guild.id
        db.is_in_database_guild(guild_id) # check if the guild is in database and remove them if not
        
        r = db.remove_moderator_role(guild_id, str(role.id)) # send request to remove role from moderators's roles list
        if r[0] is False: return await report_error(self.client, ctx, r) # if request has not worked

        await ctx.send(f"Role '{role.name}' has been removed from moderators's roles's list.") # send reply

    # 'clear' moderators subcommand
    @moderators.command(name="clear")
    async def moderators_clear(self, ctx, role:discord.Role):
        guild_id = ctx.guild.id
        db.is_in_database_guild(guild_id) # check if the guild is in database and clear them if not
        
        r = db.clear_moderator_role(guild_id, str(role.id)) # send request to clear role moderators's roles list
        if r[0] is False: return await report_error(self.client, ctx, r) # if request has not worked

        await ctx.send(f"Moderators's roles has been cleared") # send reply



def setup(client):
    client.add_cog(Admin(client))
