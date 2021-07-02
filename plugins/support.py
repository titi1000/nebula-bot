from main import MAINCOLOR, ERRORCOLOR
import discord
import sys
import datetime
import toml
from discord.ext import commands
from core.others import is_it_owner

class Support(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.data = toml.load("config.toml")
        self.suggest_channel = self.data["suggest_channel"]
        self.report_channel = self.data["report_channel"]

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

        channel = await self.client.fetch_channel(self.suggest_channel)
        
        suggest_e = discord.Embed(
            title=f"{ctx.author.name} made a suggestion:",
            color=MAINCOLOR,
            description=suggestion,
            timestamp=datetime.datetime.now()
        )
        suggest_e.set_footer(text=f"User ID:{ctx.author.id}")

        msg = await channel.send(embed=suggest_e)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

    @commands.command()
    async def report(self, ctx, *, report=None):
        if report is None:
            return await ctx.send("Please specify what you want to report!")

        channel = await self.client.fetch_channel(self.report_channel)
        
        report_e = discord.Embed(
            title=f"{ctx.author.name} reported:",
            color=ERRORCOLOR,
            description=report,
            timestamp=datetime.datetime.now()
        )
        report_e.set_footer(text=f"User ID:{ctx.author.id}")
        
        await channel.send(embed=report_e)

    @commands.command()
    @commands.check(is_it_owner)
    async def accept(self, ctx, type=None, id:int=None, *, reason=None):
        if type is None or id is None or reason is None:
            return await ctx.send(f"Command usage:\n```{ctx.prefix}accept <report/suggestion> <message-id> <reason>```")

        if type == "report":
            channel = await self.client.fetch_channel(self.report_channel)
            try:
                message = await channel.fetch_message(id)
            except discord.NotFound:
                return await ctx.send("Report message not found... Please retry!")

            try:
                user_id = int(message.embeds[0].footer.text[8:])
                user = await self.client.fetch_user(user_id)
                await user.send(f"**Your report has been approved by {ctx.author.name}:**\n\n{reason}")
            except:
                pass

            new_embed = discord.Embed(
                title=message.embeds[0].title,
                description=message.embeds[0].description,
                color=0x65fe34
            )
            new_embed.add_field(name=f"Approved by {ctx.author.name}", value=reason)

            await message.edit(embed=new_embed)
            return await ctx.send("Approved")

        if type == "suggestion":
            channel = await self.client.fetch_channel(self.suggest_channel)
            try:
                message = await channel.fetch_message(id)
            except discord.NotFound:
                return await ctx.send("Suggestion message not found... Please retry!")
            
            try:
                user_id = int(message.embeds[0].footer.text[8:])
                user = await self.client.fetch_user(user_id)
                await user.send(f"**Your suggestion has been approved by {ctx.author.name}:**\n\n{reason}")
            except:
                pass

            new_embed = discord.Embed(
                title=message.embeds[0].title,
                description=message.embeds[0].description,
                color=0x65fe34
            )
            new_embed.add_field(name=f"Approved by {ctx.author.name}", value=reason)

            await message.edit(embed=new_embed)
            return await ctx.send("Approved")

        else:
            return await ctx.send(f"Command usage:\n```{ctx.prefix}accept <report/suggestion> <message-id> <reason>```")

    @commands.command()
    @commands.check(is_it_owner)
    async def deny(self, ctx, type=None, id:int=None, *, reason=None):
        if type is None or id is None or reason is None:
            return await ctx.send(f"Command usage:\n```{ctx.prefix}deny <report/suggestion> <message-id> <reason>```")

        if type == "report":
            channel = await self.client.fetch_channel(self.report_channel)
            try:
                message = await channel.fetch_message(id)
            except discord.NotFound:
                return await ctx.send("Report message not found... Please retry!")

            new_embed = discord.Embed(
                title=message.embeds[0].title,
                description=message.embeds[0].description,
                color=ERRORCOLOR
            )
            new_embed.add_field(name=f"Denied by {ctx.author.name}", value=reason)

            await message.edit(embed=new_embed)
            return await ctx.send("Denied")

        if type == "suggestion":
            channel = await self.client.fetch_channel(self.suggest_channel)
            try:
                message = await channel.fetch_message(id)
            except discord.NotFound:
                return await ctx.send("Suggestion message not found... Please retry!")

            new_embed = discord.Embed(
                title=message.embeds[0].title,
                description=message.embeds[0].description,
                color=ERRORCOLOR
            )
            new_embed.add_field(name=f"Denied by {ctx.author.name}", value=reason)

            await message.edit(embed=new_embed)
            return await ctx.send("Denied")

        else:
            return await ctx.send(f"Command usage:\n```{ctx.prefix}deny <report/suggestion> <message-id> <reason>```")

    @commands.command()
    @commands.check(is_it_owner)
    async def maybe(self, ctx, type=None, id:int=None, *, reason=None):
        if type is None or id is None or reason is None:
            return await ctx.send(f"Command usage:\n```{ctx.prefix}maybe suggestion <message-id> <reason>```")

        if type == "suggestion":
            channel = await self.client.fetch_channel(self.suggest_channel)
            try:
                message = await channel.fetch_message(id)
            except discord.NotFound:
                return await ctx.send("Suggestion message not found... Please retry!")

            new_embed = discord.Embed(
                title=message.embeds[0].title,
                description=message.embeds[0].description,
                color=0xefff68
            )
            new_embed.add_field(name=f"Potential suggestion (by {ctx.author.name})", value=reason)

            await message.edit(embed=new_embed)
            return await ctx.send("Potential suggestion made")

        else:
            return await ctx.send(f"Command usage:\n```{ctx.prefix}maybe suggestion <message-id> <reason>```")



def setup(client):
    client.add_cog(Support(client))