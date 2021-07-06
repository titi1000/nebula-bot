import discord
from discord.ext import commands
import random
from main import MAINCOLOR, ERRORCOLOR
from core.others import apirequest, is_blacklisted_cogs

class Fun(commands.Cog):

    def __init__(self, client):
        self.client = client
        print("Fun cog well loaded.")

    # random meme
    @commands.command()
    @is_blacklisted_cogs
    async def meme(self, ctx):
        response = await apirequest("https://meme-api.herokuapp.com/gimme")
        if response is None:
            meme_e = discord.Embed(
                description="There is a problem with the api. Please retry later.",
                color=ERRORCOLOR
            )
        else:
            meme_e = discord.Embed(
                title=f"Hi {ctx.author.name}, here is your meme :)"
            )
            meme_e.set_image(url=response["url"])

        await ctx.send(embed=meme_e)
    
    # random cat picture
    @commands.command()
    @is_blacklisted_cogs
    async def cat(self, ctx):
        response = await apirequest("https://api.thecatapi.com/v1/images/search")
        if response is None:
            cat_e = discord.Embed(
                description="There is a problem with the api. Please retry later.",
                color=ERRORCOLOR
            )
        else:
            cat_e = discord.Embed(
                title=f"Hi {ctx.author.name}, here is your cat picture :)"
            )
            cat_e.set_image(url=response[0]["url"])

        await ctx.send(embed=cat_e)

    # random dog picture
    @commands.command()
    @is_blacklisted_cogs
    async def dog(self, ctx):
        response = await apirequest("https://dog.ceo/api/breeds/image/random")
        if response is None:
            dog_e = discord.Embed(
                description="There is a problem with the api. Please retry later.",
                color=ERRORCOLOR
            )
        else:
            dog_e = discord.Embed(
                title=f"Hi {ctx.author.name}, here is your dog picture :)"
            )
            dog_e.set_image(url=response["message"])

        await ctx.send(embed=dog_e)

    # user's avatar
    @commands.command()
    @is_blacklisted_cogs
    async def avatar(self, ctx, member:discord.User=None):
        if member is None:
            avatar_e = discord.Embed(
            title=f"{ctx.author.name}'s avatar"
            )
            avatar_e.set_image(url=ctx.author.avatar_url)

        else:
            avatar_e = discord.Embed(
                title=f"{member.name}'s avatar"
            )
            avatar_e.set_image(url=member.avatar_url)

        await ctx.send(embed=avatar_e)

    # random responses
    @commands.command(aliases=["8ball", "eightball"])
    @is_blacklisted_cogs
    async def eight_ball(self, ctx, *, question=None):
        if question is None:
            return await ctx.send("Please ask a question!")
        responses = ("It's possible", 
                    "Totally", 
                    "I think yes", 
                    "Absolutely true", 
                    "Not at all", 
                    "I do not know", 
                    "Absolutely wrong",
                    "I do not think so",
                    "I won't give my point of view",
                    "I'm eating french fries",
                    "I do not believe")
        await ctx.send(random.choice(responses))

    # reverse some text
    @commands.command()
    @is_blacklisted_cogs
    async def reverse(self, ctx, *, text=None):
        if text is None:
            return await ctx.send("Please provid some text to reverse...")
        await ctx.send(text[::-1])

    # make the bot say something
    @commands.command()
    @is_blacklisted_cogs
    async def say(self, ctx, *, text=None):
        if text is None:
            return await ctx.send("Please provid some text to say...")
        await ctx.send(text)



def setup(client):
    client.add_cog(Fun(client))