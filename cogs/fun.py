import discord
from discord.ext import commands
from json import load, loads
from requests import get
import datetime
import random

def apirequest():
    headers = {
        'Accept': 'application/json',
    }

    response = get("https://meme-api.herokuapp.com/gimme", headers=headers)
    if response.status_code == 200:
        return loads(response.content.decode('utf-8'))
    else:
        return None

class Fun(commands.Cog):

    def __init__(self, client):
        self.client = client
        print("Fun cog well loaded.")

    # random meme
    @commands.command()
    async def meme(self, ctx):
        response = apirequest()
        if response == None:
            meme_e = discord.Embed(
                description="There is a problem with the api. Please retry later.",
                color=0xfe2419
            )
        else:
            meme_e = discord.Embed(
                title="Hi {}, here is your meme :)".format(ctx.message.author.name)
            )
            meme_e.set_image(url=response["url"])

        await ctx.send(embed=meme_e)

    # user's avatar
    @commands.command()
    async def avatar(self, ctx, member:discord.User=None):
        if member is None:
            await ctx.send("Please provid an user. Use the command like that :\n```{}avatar @user```".format(ctx.prefix))
            return

        avatar_e = discord.Embed(
            title="{}'s avatar".format(member.name)
        )
        avatar_e.set_image(url=member.avatar_url)

        await ctx.send(embed=avatar_e)

    # random responses
    @commands.command(aliases=["8ball", "eightball"])
    async def eight_ball(self, ctx, *, question):
        responses = ["It's possible", 
                    "Totally", 
                    "I think yes", 
                    "Absolutely true", 
                    "Not at all", 
                    "I do not know", 
                    "Absolutely wrong",
                    "I do not think so",
                    "I won't give my point of view",
                    "I'm eating french fries",
                    "I do not believe"]
        await ctx.send(random.choice(responses))


def setup(client):
    client.add_cog(Fun(client))