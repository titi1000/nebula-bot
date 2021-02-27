import discord
from discord.ext import commands
import time

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

                await ctx.send(embed=remove_e)
                return
            except Exception as e:
                await ctx.send("Command failed...\n```{}```".format(e))
                return
        
        else:
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
        

def setup(client):
    client.add_cog(Mods(client))