import discord
from discord.ext import commands
import time
import datetime
import asyncio
from main import MAINCOLOR
from core.db import db
from core.db_punishments import db_punishments
from core.others import get_channel_by_id, is_it_moderator

class Mods(commands.Cog):

    def __init__(self, client):
        self.client = client
        print("Mods cog well loaded.")

    # give or remove a role to everyone
    @commands.command(aliases=["mr"])
    @commands.has_permissions(administrator=True)
    async def massrole(self, ctx, action=None, role:discord.Role=None):
        start = time.time()
        if role is None or action is None:
            await ctx.send(f"Use the command like that :\n```{ctx.prefix}massrole <add/remove> <@Role>```")
            return

        message = await ctx.send("Command running. Please wait...")

        # to go faster
        target_remove = len(role.members)
        target_add = ctx.guild.member_count - target_remove

        if action == "add":
            try:
                count = 0
                for member in ctx.guild.members:
                    if not role in member.roles:
                        await member.add_roles(role)
                        count += 1
                    if count == target_add:
                        break
                
                add_e = discord.Embed(
                    title="Massrole complete",
                    description=f"Successfully gave {count} member(s) the {role.mention} role."
                )
                add_e.add_field(name="Time taken", value=f"{round(time.time() - start, 2)} seconds")

                await message.delete()
                await ctx.send(embed=add_e)
                return
            except Exception as e:
                await ctx.send(f"Command failed...\n```{e}```")
                return

        if action == "remove":
            try:
                count = 0
                for member in ctx.guild.members:
                    if role in member.roles:
                        await member.remove_roles(role)
                        count += 1
                    if count == target_remove:
                        break

                remove_e = discord.Embed(
                    title="Massrole complete",
                    description=f"Successfully removed {count} member(s) the {role.mention} role."
                )
                remove_e.add_field(name="Time taken", value=f"{round(time.time() - start, 2)} seconds")
                
                await message.delete()
                await ctx.send(embed=remove_e)
                return
            except Exception as e:
                await ctx.send(f"Command failed...\n```{e}```")
                return
        
        else:
            await message.delete()
            await ctx.send(f"Use the command like that :\n```{ctx.prefix}massrole <add/remove> <@Role>```")

    # change the nick of someone
    @commands.command()
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member:discord.Member=None, *, nick=None):
        if member is None or nick is None:
            await ctx.send(f"Please provid all require parameters :\n```{ctx.prefix}nick @member new_nick```")
            return
        try:
            await member.edit(nick=nick)
            await ctx.send(f"{member.name}'s nick changed")
        except discord.Forbidden:
            await ctx.send("I don't have the permission to do this.")

    # purge some messages
    @commands.command(aliases=["clear"])
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount:int=None):
        if amount is None:
            return await ctx.send("Please provid an amount of messages to delete.")

        purged = await ctx.channel.purge(limit=amount+1)
        purged = await ctx.send(f"Successfully deleted {amount} message(s)!")

        await asyncio.sleep(5)
        await purged.delete()

    # ban command
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member:discord.Member=None, *, reason=None):
        if member is None:
            return await ctx.send("You need to provid an user to ban.")
        
        try:
            await member.ban(reason=reason)
            await ctx.send(f"{member.mention} has been banned!")
            db_punishments.add_punishment(guild_id=ctx.guild.id, member_id=member.id, type="ban", start_timestamp=int(time.time()), moderator_id=ctx.author.id, reason=reason)

            channel_id = db.logs_channel(ctx.guild.id)

            if channel_id == False:
                return

            channel = await get_channel_by_id(ctx.guild, int(channel_id))
            if reason is None:
                description = f"**Member:** {member.name}#{member.discriminator} ({member.id})\n**Action:** Ban"
            else:
                description = f"**Member:** {member.name}#{member.discriminator} ({member.id})\n**Action:** Ban\n**Reason:** {reason}"

            ban_e = discord.Embed(
                description=description,
                color=0xf70000
            )
            ban_e.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)

            await channel.send(embed=ban_e)
        
        except:
            return

    # kick command
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member:discord.Member=None, *, reason=None):
        if member is None:
            return await ctx.send("You need to provid an user to kick.")
        
        try:
            await member.kick(reason=reason)
            await ctx.send(f"{member.mention} has been kicked!")
            db_punishments.add_punishment(guild_id=ctx.guild.id, member_id=member.id, type="kick", start_timestamp=int(time.time()), moderator_id=ctx.author.id, reason=reason)


            channel_id = db.logs_channel(ctx.guild.id)

            if channel_id == False:
                return

            channel = await get_channel_by_id(ctx.guild, int(channel_id))
            if reason is None:
                description = f"**Member:** {member.name}#{member.discriminator} ({member.id})\n**Action:** Kick"
            else:
                description = f"**Member:** {member.name}#{member.discriminator} ({member.id})\n**Action:** Kick\n**Reason:** {reason}"

            kick_e = discord.Embed(
                description=description,
                color=0xf70000
            )
            kick_e.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)

            await channel.send(embed=kick_e)
        
        except:
            return
    
    # warn command
    @commands.command()
    @commands.check(is_it_moderator)
    async def warn(self, ctx, member:discord.Member=None, *, reason=None):
        if member is None:
            return await ctx.send("You need to provid an user to warn.")
        
        try:
            await ctx.send(f"{member.mention} has been warned!")
            db_punishments.add_punishment(guild_id=ctx.guild.id, member_id=member.id, type="warn", start_timestamp=int(time.time()), moderator_id=ctx.author.id, reason=reason)

            channel_id = db.logs_channel(ctx.guild.id)

            if channel_id == False:
                return

            channel = await get_channel_by_id(ctx.guild, int(channel_id))
            if reason is None:
                description = f"**Member:** {member.name}#{member.discriminator} ({member.id})\n**Action:** Warn"
            else:
                description = f"**Member:** {member.name}#{member.discriminator} ({member.id})\n**Action:** Warn\n**Reason:** {reason}"

            warn_e = discord.Embed(
                description=description,
                color=0xf70000
            )
            warn_e.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)

            await channel.send(embed=warn_e)
        
        except:
            return

    # get punishments command
    @commands.command(aliases = ["p", "punish", "infractions"])
    @commands.check(is_it_moderator)
    async def punishments(self, ctx, member:discord.Member=None):
        if member is not None:
            punishments = db_punishments.get_member_punishments(ctx.guild.id, member.id)

            p_description = ""
            if len(punishments) > 0:
                for punishment in punishments:
                    if punishment.reason == "":
                        punishment.reason = "No reason was given"
                    p_description+=f"**Infraction #`{punishment.id}` - {punishment.type}**\n{punishment.reason}\n"
            else:
                p_description+="No infraction"

            p_e = discord.Embed(description = p_description, color = MAINCOLOR)
            p_e.set_author(name = member, icon_url=member.avatar_url)

            await ctx.send(embed = p_e)
        else:
            await ctx.send("Please provid a valid member")
    
    # get punishment command
    @commands.command(aliases = ["infraction"])
    @commands.check(is_it_moderator)
    async def punishment(self, ctx, punishment_id:int=None):
        if punishment_id is not None:
            punishment = db_punishments.get_punishment(ctx.guild.id, punishment_id)

            member_id = punishment.member_id
            member = ctx.guild.get_member(member_id)
            if member is None:
                member = await self.client.fetch_user(member_id)
            member_avatar_url = member.avatar_url

            moderator_id = punishment.moderator_id
            moderator = ctx.guild.get_member(moderator_id)
            if moderator is None:
                moderator = await self.client.fetch_user(moderator_id)
            moderator_avatar_url = moderator.avatar_url

            p_description = ""
            p_description+=f"**Member:** {member} \| {member.id}\n"
            p_description+=f"**Action:** {punishment.type}\n"
            if punishment.end_timestamp is not None:
                duration_timestamp = punishment.end_timestamp - punishment.start_timestamp
                duration = { "years" : 0, "months" : 0, "weeks" : 0, "days" : 0, "hours" : 0, "minutes" : 0, "seconds" : 0}
                while duration_timestamp >= 31536000:
                    duration["years"] +=1
                    duration_timestamp-=31536000
                while duration_timestamp >= 2592000:
                    duration["months"]+=1
                    duration_timestamp-=2592000
                while duration_timestamp >= 604800:
                    duration["weeks"]+=1
                    duration_timestamp-=604800
                while duration_timestamp >= 86400:
                    duration["days"]+=1
                    duration_timestamp-=86400
                while duration_timestamp >= 3600:
                    duration["hours"]+=1
                    duration_timestamp-=3600
                while duration_timestamp >= 60:
                    duration["minutes"]+=1
                    duration_timestamp-=60
                duration["seconds"]=duration_timestamp
            
                p_description+=f"**Duration:** "
                for k,v in duration.items():
                    if v > 0:
                        p_description+=f"{v}{k} "
                p_description+="\n"
            
            if punishment.reason == "":
                punishment.reason = "No reason was given"
            p_description+=f"**Reason:** {punishment.reason}"

            p_e = discord.Embed(description = p_description, color = MAINCOLOR, timestamp = datetime.datetime.fromtimestamp(float(punishment.start_timestamp)))
            p_e.set_author(name = moderator, icon_url=moderator_avatar_url)
            p_e.set_footer(text=f"Infraction #{punishment.id}")

            await ctx.send(embed = p_e)
        else:
            await ctx.send("Please provid a valid punishement id")
            


def setup(client):
    client.add_cog(Mods(client))