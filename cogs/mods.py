import discord
from discord.ext import commands
import time
import sqlite3
from others import is_in_database_guild
from others import logs_channel


class Mods(commands.Cog):

    def __init__(self, client):
        self.client = client
        print("Mods cog well loaded.")

    # give or remove a role to everyone
    @commands.command(aliases=["mr"])
    @commands.has_permissions(manage_roles=True)
    async def massrole(self, ctx, action=None, role:discord.Role=None):
        start = time.time()
        if role is None or action is None:
            await ctx.send("Use the command like that :\n```{}massrole <add/remove> <@Role>```".format(ctx.prefix))
            return

        message = await ctx.send("Command running. Please wait...")

        # to go faster
        for r in ctx.guild.roles:
            if r == role:
                target_remove = len(r.members)
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
                    description="Successfully gave {} member(s) the {} role.".format(count, role.mention)
                )
                add_e.add_field(name="Time taken", value="{} seconds".format(round(time.time() - start, 2)))

                await message.delete()
                await ctx.send(embed=add_e)
                return
            except Exception as e:
                await ctx.send("Command failed...\n```{}```".format(e))
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
                    description="Successfully removed {} member(s) the {} role.".format(count, role.mention)
                )
                remove_e.add_field(name="Time taken", value="{} seconds".format(round(time.time() - start, 2)))
                
                await message.delete()
                await ctx.send(embed=remove_e)
                return
            except Exception as e:
                await ctx.send("Command failed...\n```{}```".format(e))
                return
        
        else:
            await message.delete()
            await ctx.send("Use the command like that :\n```{}massrole <add/remove> <@Role>```".format(ctx.prefix))

    # change the nick of someone
    @commands.command()
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member:discord.Member=None, *, nick=None):
        if member is None or nick is None:
            await ctx.send("Please provid all require parameters :\n```{}nick @member new_nick```".format(ctx.prefix))
            return
        try:
            await member.edit(nick=nick)
            await ctx.send("{}'s nick changed".format(member.name))
        except discord.Forbidden:
            await ctx.send("I don't have the permission to do this.")

    # set logs channel
    @commands.command(aliases=["mod-logs", "mod-channel", "ml"])
    @commands.has_permissions(administrator=True)
    async def mod_logs(self, ctx, channel:discord.TextChannel=None):
        if channel is None:
            await ctx.send("Please provid a channel. Usage : \n```{}mod-logs <#channel>```".format(ctx.prefix))
            return

        is_in_database_guild(ctx.guild.id)
        db = sqlite3.connect("main.sqlite")
        cursor = db.cursor()
        cursor.execute("SELECT logs_id FROM guilds WHERE guild_id = ?", (ctx.guild.id,))
        result = cursor.fetchone()

        if result[0] is None:
            cursor.execute("INSERT INTO guilds(logs_id) VALUES(?) WHERE guild_id = ?", (channel.id, ctx.guild.id))

        else:
            print("test")
            cursor.execute("UPDATE guilds SET logs_id = ? WHERE guild_id = ?", (channel.id, ctx.guild.id))
        db.commit()
        cursor.close()

    # logs
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        channel_id = logs_channel(message.guild.id)
        if channel_id == False:
            return
        else:
            channel = discord.utils.get(message.guild.channels, id=int(channel_id))
            await channel.send("Message deleted in {} :\n{}".format(message.channel.mention, message.content))
        

def setup(client):
    client.add_cog(Mods(client))