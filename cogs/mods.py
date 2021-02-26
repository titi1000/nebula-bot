import discord
from discord.ext import commands

class Mods(commands.Cog):

    def __init__(self, client):
        self.client = client

    # give a role to everyone
    @commands.command(aliases=["mr"])
    @commands.has_permissions(administrator=True)
    async def massrole(self, ctx, role:discord.Role):
        try:
            count = 0
            for member in ctx.guild.members:
                await member.add_roles(role)
                count += 1
                print(member)

            await ctx.send("Successfully gave {} member(s) the {} role.".format(count, role.mention))
        except:
            await ctx.send("Command failed...")

def setup(client):
    client.add_cog(Mods(client))