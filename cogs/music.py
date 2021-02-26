import discord
from discord.ext import commands

class Music(commands.Cog):

    def __init__(self, client):
        self.client = client
        print("Music cog well loaded.")

    @commands.command()
    async def connect(self, ctx):
        if ctx.author.voice and ctx.author.voice.channel:
            voice_channel = ctx.author.voice.channel
            await voice_channel.connect()
        else:
            await ctx.send("You need to be in a voice channel to use this command.")

    @commands.command()
    async def play(self, ctx, link):
        pass


def setup(client):
    client.add_cog(Music(client))