from discord import embeds, message
from core.others import is_it_owner
import discord
from discord.ext import commands
import sqlite3
import datetime
from core.db_user import db_users
from main import MAINCOLOR
from core.nebula_logging import nebula_logging

class Staff(commands.Cog):

    def __init__(self, client):
        self.client = client
        print("Staff cog well loaded.")

    @commands.command(aliases = ["pb", "pblacklist", "player-blacklist"])
    @commands.check(is_it_owner)
    async def playerblacklist(self, ctx, action:str, user:discord.User):
        if action is None: return await ctx.send("Please provid an action (`rm`/`rem`/`remove` or `add`)")
        if user is None: return await ctx.send("Please provid a valid user")
        db_users.is_in_database_user(user.id)
        action = action.lower()

        if action == "add":
            r = db_users.set_grade(user_id=user.id, grade="blacklisted", action=action)
            if r[0] != r[1]: return await ctx.send(f"**{user}** is now blacklisted")
            return await ctx.send(f"**{user}** was already blacklisted")

        elif action == "rm" or action == "rem" or action == "remove":
            r = db_users.set_grade(user_id=user.id, grade="blacklisted", action=action)
            if r[0] != r[1]: return await ctx.send(f"**{user}** is not anymore blacklisted")
            return await ctx.send(f"**{user}** doesn't be blacklisted")
                
        return await ctx.send(f"The action **{action}** doesn't recognized, please use `rm`/`rem`/`remove` or `add`")

    @commands.command(aliases=["set-command-count", "scc"])
    @commands.check(is_it_owner)
    async def setcommandcount(self, ctx, user:discord.User=None, n:int=None):
        if n is None: return await ctx.send("Please provid number (integer)")
        if user is None: return await ctx.send("Please provid a valid user")
        db_users.is_in_database_user(user.id)
        r = db_users.set_counter(user.id, "command", n)
        await ctx.send(f"Commands counter of **{user}** was updated\n{r[0]} ---> {r[1]}")

    @commands.command(aliases=["set-suggest-count", "ssc"])
    @commands.check(is_it_owner)
    async def setsuggestcount(self, ctx, user:discord.User, n:int):
        if n is None: return await ctx.send("Please provid number (integer)")
        if user is None: return await ctx.send("Please provid a valid user")
        db_users.is_in_database_user(user.id)
        r = db_users.set_counter(user.id, "suggest", n)
        await ctx.send(f"Suggests counter of **{user}** was updated\n{r[0]} ---> {r[1]}")

    @commands.command(aliases=["set-report-count", "src"])
    @commands.check(is_it_owner)
    async def setreportcount(self, ctx, user:discord.User, n:int):
        if n is None: return await ctx.send("Please provid number (integer)")
        if user is None: return await ctx.send("Please provid a valid user")
        db_users.is_in_database_user(user.id)
        r = db_users.set_counter(user.id, "report", n)
        await ctx.send(f"Reports counter of **{user}** was updated\n{r[0]} ---> {r[1]}")
    

def setup(client):
    client.add_cog(Staff(client))