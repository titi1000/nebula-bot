import discord
from discord.ext import commands
from json import load, loads
from requests import get

def apirequest():
    headers = {
        'Accept': 'application/json',
    }

    response = get(f"https://meme-api.herokuapp.com/gimme", headers=headers)
    if response.status_code == 200:
        return loads(response.content.decode('utf-8'))
    else:
        return None

class Fun(commands.Cog):

    def __init__(self, client):
        self.client = client

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


def setup(client):
    client.add_cog(Fun(client))