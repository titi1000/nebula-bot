import discord
import datetime
import random
from main import MAINCOLOR
from discord.ext import tasks, commands
from core.others import is_blacklisted_cogs
from core.db import db
from core.nebula_logging import nebula_logging, report_error

class Giveaway(commands.Cog):

    def __init__(self, client):
        self.client = client

        self.check_giveaway_end.start()

    @tasks.loop(seconds=20)
    async def check_giveaway_end(self):
        try:
            result = db.get_giveaways_finished()
            if result[0] is False: return nebula_logging.logger_mysql.error("An error has occured when a get_giveaway_finished()")

            for giveaway in result[1]:
                await self.end_giveaway(giveaway[0], giveaway[1], giveaway[2], giveaway[3])
                r = db.db_execute("DELETE FROM giveaways WHERE `channel_id` = %s AND message_id = %s", (giveaway[0], giveaway[1]))
                if r[0] is False: return nebula_logging.logger_mysql.error("Ah error has occured during a end_giveaway")
        except:
            pass

    # call when a giveaway is finished
    async def end_giveaway(self, channel_id, message_id, prize, winners):
        channel = await self.client.fetch_channel(channel_id)
        message = await channel.fetch_message(message_id)
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

        if winners_list == "No winner :(":
             await channel.send(f"{winners_list}\nhttps://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}")
        else:
            await channel.send(f":tada: Congratulations {winners_list} !! :tada:\nhttps://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}")
        
        await message.edit(embed=winner_e)

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

        r = db.insert_giveaway(channel.id, message.id, prize, winners, datetime.datetime.utcnow() + datetime.timedelta(0, duration))
        if r[0] is False: return await report_error(self.client, ctx, r)


def setup(client):
    client.add_cog(Giveaway(client))