import discord
from discord.ext import commands
import datetime
import random
import asyncio
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

    # create a giveaway
    @commands.command()
    @commands.has_permissions(administrator=True)
    @is_blacklisted_cogs
    async def giveaway(self, ctx, channel:discord.TextChannel=None, duration=None, winners=None, *, prize=None):
        if channel is None or duration is None or winners is None or prize is None:
            return await ctx.send(f"Command usage :\n```{ctx.prefix}giveaway <#channel> <10M or 2H or 1D> <number of winners> <prize>```\nM for minutes / H for hours / D for days")

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

        embed_duration = f"{duration} {text_duration}"

        if text_duration == "minutes":
            duration *= 60
        if text_duration == "hours":
            duration *= 3600
        if text_duration == "days":
            duration *= 86400

        giveaway_e = discord.Embed(
            title=":tada: GIVEAWAY :tada:",
            description=f"{prize}\n**Winners** : {winners}\n**Duration** : {embed_duration}\n**Hosted by** : {ctx.author.mention}",
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
                winners_list += f"{winner.mention} "
                winners -= 1
                users.remove(winner)
            winners_list += f"\n**You won** : {prize}"

        winner_e = discord.Embed(
            title=":tada: GIVEAWAY ENDED :tada:",
            description=f"**Winners** : {winners_list}",
            color=MAINCOLOR,
            timestamp=datetime.datetime.utcnow()
        )
        winner_e.set_footer(text="Giveaway ended")

        await channel.send(f":tada: Congratulations {winners_list} !! :tada:\nhttps://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}")
        await message.edit(embed=winner_e)



def setup(client):
    client.add_cog(Fun(client))