import discord
from discord.ext import commands
import time
import datetime
import asyncio
from main import MAINCOLOR
from core.db import db
from core.db_punishments import db_punishments
from core.others import get_channel_by_id, is_it_moderator
from core.nebula_logging import report_error

class Mods(commands.Cog):

    def __init__(self, client):
        self.client = client
        print("Mods cog well loaded.")

    # give or remove a role to everyone
    @commands.command(aliases=["mr"])
    @commands.has_permissions(administrator=True)
    async def massrole(self, ctx, action=None, role:discord.Role=None):
        start = time.time()
        if role is None or action is None: return await ctx.send(f"Use the command like that :\n```{ctx.prefix}massrole <add/remove> <@Role>```")
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
                    if count == target_add: break
                
                add_e = discord.Embed(
                    title="Massrole complete",
                    description=f"Successfully gave {count} member(s) the {role.mention} role."
                )
                add_e.add_field(name="Time taken", value=f"{round(time.time() - start, 2)} seconds")

                await message.delete()
                await ctx.send(embed=add_e)
                return
            except Exception as e: return await ctx.send(f"Command failed...\n```{e}```")

        elif action == "remove":
            try:
                count = 0
                for member in ctx.guild.members:
                    if role in member.roles:
                        await member.remove_roles(role)
                        count += 1
                    if count == target_remove: break

                remove_e = discord.Embed(
                    title="Massrole complete",
                    description=f"Successfully removed {count} member(s) the {role.mention} role."
                )
                remove_e.add_field(name="Time taken", value=f"{round(time.time() - start, 2)} seconds")
                
                await message.delete()
                await ctx.send(embed=remove_e)
                return
            except Exception as e: return await ctx.send(f"Command failed...\n```{e}```")
        
        else:
            await message.delete()
            await ctx.send(f"Use the command like that :\n```{ctx.prefix}massrole <add/remove> <@Role>```")

    # change the nick of someone
    @commands.command()
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member:discord.Member=None, *, nick=None):
        if member is None or nick is None: return await ctx.send(f"Please provid all require parameters :\n```{ctx.prefix}nick @member new_nick```")
        try:
            await member.edit(nick=nick)
            await ctx.send(f"{member.name}'s nick changed")
        except discord.Forbidden: await ctx.send("I don't have the permission to do this.")

    # purge some messages
    @commands.command(aliases=["clear"])
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount:int=None):
        if amount is None: return await ctx.send("Please provid an amount of messages to delete.")

        purged = await ctx.channel.purge(limit=amount+1)
        purged = await ctx.send(f"Successfully deleted {amount} message(s)!")

        await asyncio.sleep(5)
        await purged.delete()

    # ban command
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member:discord.Member=None, *, reason=None):
        if reason is not None and len(reason) > 210: return await ctx.send("The reason can't exceed 210 characters")
        if member is None: return await ctx.send("You need to provid an user to ban.")
        
        try:
            await member.ban(reason=reason)
            await ctx.send(f"{member.mention} has been banned!")
            r = db_punishments.add_punishment(guild_id=ctx.guild.id, member_id=member.id, type="ban", start_timestamp=int(time.time()), moderator_id=ctx.author.id, reason=reason)
            if r[0] is False: return await report_error(self.client, ctx, r)

            r_channel_id = db.logs_channel(ctx.guild.id)
            if r_channel_id[0] is False: return await report_error(self.client, ctx, r_channel_id)

            channel_id = r_channel_id[1][0]
            if channel_id is None: return

            channel = await get_channel_by_id(ctx.guild, int(channel_id))
            if reason is None: description = f"**Member:** {member.name}#{member.discriminator} ({member.id})\n**Action:** Ban"
            else: description = f"**Member:** {member.name}#{member.discriminator} ({member.id})\n**Action:** Ban\n**Reason:** {reason}"

            ban_e = discord.Embed(
                description=description,
                color=0xf70000
            )
            ban_e.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)

            await channel.send(embed=ban_e)
        
        except: return

    # kick command
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member:discord.Member=None, *, reason=None):
        if reason is not None and len(reason) > 210: return await ctx.send("The reason can't exceed 210 characters")
        if member is None: return await ctx.send("You need to provid an user to kick.")
        
        try:
            await member.kick(reason=reason)
            await ctx.send(f"{member.mention} has been kicked!")
            r = db_punishments.add_punishment(guild_id=ctx.guild.id, member_id=member.id, type="kick", start_timestamp=int(time.time()), moderator_id=ctx.author.id, reason=reason)
            if r[0] is False: return await report_error(self.client, ctx, r)

            r_channel_id = db.logs_channel(ctx.guild.id)
            if r_channel_id[0] is False: return await report_error(self.client, ctx, r_channel_id)

            channel_id = r_channel_id[1][0]
            if channel_id is None: return

            channel = await get_channel_by_id(ctx.guild, int(channel_id))
            if reason is None: description = f"**Member:** {member.name}#{member.discriminator} ({member.id})\n**Action:** Kick"
            else: description = f"**Member:** {member.name}#{member.discriminator} ({member.id})\n**Action:** Kick\n**Reason:** {reason}"

            kick_e = discord.Embed(
                description=description,
                color=0xf70000
            )
            kick_e.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)

            await channel.send(embed=kick_e)
        
        except: return
    
    # warn command
    @commands.command()
    @commands.check(is_it_moderator)
    async def warn(self, ctx, member:discord.Member=None, *, reason=None):
        if reason is not None and len(reason) > 210: return await ctx.send("The reason can't exceed 210 characters")
        if member is None: return await ctx.send("You need to provid an user to warn.")
        
        try:
            await ctx.send(f"{member.mention} has been warned!")
            r = db_punishments.add_punishment(guild_id=ctx.guild.id, member_id=member.id, type="warn", start_timestamp=int(time.time()), moderator_id=ctx.author.id, reason=reason)
            if r[0] is False: return await report_error(self.client, ctx, r)
                    
            r_channel_id = db.logs_channel(ctx.guild.id)
            if r_channel_id[0] is False: return await report_error(self.client, ctx, r_channel_id)

            channel_id = r_channel_id[1]
            if channel_id is None: return

            channel = await get_channel_by_id(ctx.guild, int(channel_id))
            if reason is None: description = f"**Member:** {member.name}#{member.discriminator} ({member.id})\n**Action:** Warn"
            else: description = f"**Member:** {member.name}#{member.discriminator} ({member.id})\n**Action:** Warn\n**Reason:** {reason}"

            warn_e = discord.Embed(
                description=description,
                color=0xf70000
            )
            warn_e.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)

            await channel.send(embed=warn_e)

        except: return

    # get punishments command
    @commands.command(aliases = ["p", "punish", "infractions"])
    @commands.check(is_it_moderator)
    async def punishments(self, ctx, member:discord.Member=None, page:int=1):
        if member is None: return await ctx.send("Please provid a valid member")
        r_punishments = db_punishments.get_member_punishments(ctx.guild.id, member.id)
        if r_punishments[0] is False: return await report_error(self.client, ctx, r_punishments)
        
        punishments = r_punishments[1]
        embeds = []
        count=0
        page_count=0
        p_description = ""
        if len(punishments) > 0:
            for punishment in punishments:
                if punishment.reason == "":
                    punishment.reason = "No reason was given"
                p_description+=f"**Infraction #`{punishment.id}` - {punishment.type}**\n{punishment.reason}\n"
                count+=1
                if count % 8 == 0 or len(punishments) == count:
                    p_e = discord.Embed(description = p_description, color = MAINCOLOR)
                    p_e.set_author(name = member, icon_url=member.avatar_url)
                    page_count+=1
                    embeds.append(p_e)
                    p_description = ""
        else:
            p_description+="No infraction"
            p_e = discord.Embed(description = p_description, color = MAINCOLOR)
            p_e.set_author(name = member, icon_url=member.avatar_url)
            embeds.append(p_e)
            
        if page <= len(embeds) and page > 0:
            embed = embeds[page-1]
            if page_count != 0: embed.set_footer(text=f"Page {page}/{page_count}")
            await ctx.send(embed = embed)
        else: await ctx.send("This page doesn't exist")
        
    # get punishment command
    @commands.command(aliases = ["infraction"])
    @commands.check(is_it_moderator)
    async def punishment(self, ctx, punishment_id:int=None):
        if punishment_id is None: await ctx.send("Please provid a valid punishement id")
        r_punishment = db_punishments.get_punishment(ctx.guild.id, punishment_id)
        if r_punishment[0] is False: return await report_error(self.client, ctx, r_punishment)

        punishment = r_punishment[1]
        if punishment is None: return await ctx.send("This punishment id doesn't exist")

        await ctx.send(embed = punishment.get_embed(ctx=ctx))
            
    @commands.command(aliases = ["delete-infraction", "del-infraction", "del-i", "delete_infraction", "del_infraction", "del_i", "delete-punishment", "del-punishment", "del-p", "del_punishment", "del_p"])
    async def delete_punishment(self, ctx, punishment_id:int=None):
        def check(message: discord.Message):
            return message.channel == ctx.channel and message.author != self.client.user
        if punishment_id is None: return await ctx.send("Please provid a valid punishement id")
        r = db_punishments.get_punishment(ctx.guild.id, punishment_id)
        if r[0] is False: return await report_error(self.client, ctx, r)
            
        punishment = r[1]
        if punishment is None: return await ctx.send("This punishment is doesn't exist")
        
        question = f"Do you want to delete the infraction #{punishment.id} ? [y/n]"
        await ctx.send(content=question, embed=punishment.get_embed(ctx=ctx))
        
        message = await self.client.wait_for('message', check=check, timeout=60)
        if message.content.lower() in ["y", "yes"]:
            r = db_punishments.remove_punishment(ctx.guild.id, punishment_id)
            if r[0] is False: return await report_error(self.client, ctx, r)
            await ctx.send("This punishment has been deleted")

def setup(client):
    client.add_cog(Mods(client))