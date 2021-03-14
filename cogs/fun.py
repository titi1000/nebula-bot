import discord
from discord.ext import commands
import json
import requests
import datetime
import random
from main import MAINCOLOR
import asyncio

def apirequest(link:str):
    headers = {
        "Accept": "application/json",
    }

    response = requests.get(link, headers=headers)
    if response.status_code == 200:
        return json.loads(response.content.decode("utf-8"))
    else:
        return None

class Fun(commands.Cog):

    def __init__(self, client):
        self.client = client
        print("Fun cog well loaded.")

    # random meme
    @commands.command()
    async def meme(self, ctx):
        response = apirequest("https://meme-api.herokuapp.com/gimme")
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
            avatar_e = discord.Embed(
            title="{}'s avatar".format(ctx.author.name)
            )
            avatar_e.set_image(url=ctx.author.avatar_url)

        else:
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

    # create a giveaway
    @commands.command()
    async def giveaway(self, ctx, channel:discord.TextChannel=None, duration=None, winners=None, *, prize=None):
        if channel is None or duration is None or winners is None or prize is None:
            await ctx.send("Command usage :\n```{}giveaway <#channel> <2H or 10M or 1D> <number of winners> <prize>```\nS for seconds / M for minutes / D for days".format(ctx.prefix))

        try:
            winners = abs(int(winners))
        except:
            await ctx.send("Winners must be a number.")
            return

        if duration[-1] in ["M", "m"]:
            text_duration = "minutes"
        elif duration[-1] in ["H", "h"]:
            text_duration = "hours"
        elif duration[-1] in ["D", "d"]:
            text_duration = "days"
        else:
            await ctx.send("Duration must be like that :\n```2D (2 days) or 1M (1 minute) or 12H (12 hours)```")
            return
        
        duration = duration[:-1]
        try:
            duration = int(duration)
        except:
            await ctx.send("Duration must be like that :\n```2D (2 days) or 1M (1 minute) or 12H (12 hours)```")
            return

        embed_duration = "{} {}".format(duration, text_duration)

        if text_duration == "minutes":
            duration *= 60
        if text_duration == "hours":
            duration *= 3600
        if text_duration == "days":
            duration *= 86400

        giveaway_e = discord.Embed(
            title=":tada: GIVEAWAY :tada:",
            description="{}\n**Winners** : {}\n**Duration** : {}\n**Hosted by** : {}".format(prize, winners, embed_duration, ctx.author.mention),
            color=MAINCOLOR, 
            timestamp=datetime.datetime.utcnow() + datetime.timedelta(0, duration)
        )
        giveaway_e.set_footer(text="Ends at :")

        message = await channel.send(embed=giveaway_e)
        await message.add_reaction("🎉")

        await asyncio.sleep(duration)
        # now we edit the message with the winner

        message = await channel.fetch_message(message.id)
        for reaction in message.reactions:
            if reaction.emoji == "🎉":
                users = await reaction.users().flatten()

        winners_list = ""
        if len(users) <= 1:
            winners_list = "No winner :("
        else:
            users.remove(self.client.user)
            while winners != 0 and len(users) != 0:
                winner = random.choice(users)
                winners_list += "{} ".format(winner.mention)
                winners -= 1
                users.remove(winner)
            winners_list += "\n**You won** : {}".format(prize)

        winner_e = discord.Embed(
            title=":tada: GIVEAWAY ENDED :tada:",
            description="**Winners** : {}".format(winners_list),
            color=MAINCOLOR,
            timestamp=datetime.datetime.utcnow()
        )
        winner_e.set_footer(text="Giveaway ended")

        await channel.send(":tada: Congratulations {} !! :tada:\nhttps://discord.com/channels/{}/{}/{}".format(winners_list, message.guild.id, message.channel.id, message.id))
        await message.edit(embed=winner_e)



def setup(client):
    client.add_cog(Fun(client))