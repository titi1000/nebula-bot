from main import MAINCOLOR, ERRORCOLOR
import discord
import sys
from discord.ext import commands
from core.others import is_it_owner

class Support(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["site", "web"])
    async def website(self, ctx):
        return await ctx.send("https://nebulabot.info/")
    
    @commands.command(aliases=["doc", "docs"])
    async def documentation(self, ctx):
        return await ctx.send("https://docs.nebulabot.info/")

    @commands.command(aliases=["server"])
    async def support(self, ctx):
        return await ctx.send("https://discord.gg/vBFh9HGjy6")

    @commands.command()
    @commands.check(is_it_owner)
    async def exit(self, ctx):
        def yes_no_check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        await ctx.send("Are you sure you want to exit ? [y/n]")
        response = await self.client.wait_for("message", check=yes_no_check)
        if response.content.lower() == "y":
            sys.exit()
        else:
            await ctx.send("Cancelled!")

    @commands.command(aliases=["suggestion"])
    async def suggest(self, ctx, *, suggestion=None):
        if suggestion is None:
            return await ctx.send("Please specify what you want to suggest!")

        channel = await self.client.fetch_channel(840710676082720819)
        
        suggest_e = discord.Embed(
            title=f"{ctx.author.name} made a suggestion:",
            color=MAINCOLOR,
            description=suggestion
        )

        msg = await channel.send(embed=suggest_e)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

    @commands.command()
    async def report(self, ctx, *, report=None):
        if report is None:
            return await ctx.send("Please specify what you want to report!")

        channel = await self.client.fetch_channel(853012999764705350)
        
        suggest_e = discord.Embed(
            title=f"{ctx.author.name} reported:",
            color=ERRORCOLOR,
            description=report
        )
        
        await channel.send(embed=suggest_e)



def setup(client):
    client.add_cog(Support(client))