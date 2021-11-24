import discord
from core.db import db
from core.db_user import db_users
from core.nebula_logging import nebula_logging, report_error
from core.others import is_blacklisted_cogs, is_it_owner
from discord.ext import commands, tasks
from main import MAINCOLOR


class BotOwner(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name = "staff")
    @commands.check(is_it_owner)
    async def staff(self, ctx, action:str=None, user:discord.User=None):
        if action is None: return await ctx.send("Please provid an action (`rm`/`rem`/`remove` or `add`)")
        if user is None: return await ctx.send("Please provid a valid user")
        db_users.is_in_database_user(user.id)
        action = action.lower()

        if action == "add":
            r = db_users.set_grade(user_id=user.id, grade="staff", action=action)
            if r[0] != r[1]: return await ctx.send(f"**{user}** became a staff")
            return await ctx.send(f"**{user}** was already a staff")

        elif action == "rm" or action == "rem" or action == "remove":
            r = db_users.set_grade(user_id=user.id, grade="staff", action=action)
            if r[0] != r[1]: return await ctx.send(f"**{user}** is not anymore a staff")
            return await ctx.send(f"**{user}** doesn't be a staff")
                
        await ctx.send(f"The action **{action}** doesn't recognized, please use `rm`/`rem`/`remove` or `add`")

    @commands.command(name = "vip")
    @commands.check(is_it_owner)
    async def vip(self, ctx, action:str, user:discord.User):
        if action is None: return await ctx.send("Please provid an action (`rm`/`rem`/`remove` or `add`)")
        if user is None: return await ctx.send("Please provid a valid user")
        db_users.is_in_database_user(user.id)
        action = action.lower()

        if action == "add":
            r = db_users.set_grade(user_id=user.id, grade="vip", action=action)
            if r[0] != r[1]: return await ctx.send(f"**{user}** became a vip")
            return await ctx.send(f"**{user}** was already a vip")

        elif action == "rm" or action == "rem" or action == "remove":
            r = db_users.set_grade(user_id=user.id, grade="vip", action=action)
            if r[0] != r[1]: return await ctx.send(f"**{user}** is not anymore a vip")
            return await ctx.send(f"**{user}** doesn't be a vip")
                
        return await ctx.send(f"The action **{action}** doesn't recognized, please use `rm`/`rem`/`remove` or `add`")

    @commands.command(name = "contributor")
    @commands.check(is_it_owner)
    async def contributor(self, ctx, action:str, user:discord.User):
        if action is None: return await ctx.send("Please provid an action (`rm`/`rem`/`remove` or `add`)")
        if user is None: return await ctx.send("Please provid a valid user")
        db_users.is_in_database_user(user.id)
        action = action.lower()

        if action == "add":
            r = db_users.set_grade(user_id=user.id, grade="contributor", action=action)
            if r[0] != r[1]: return await ctx.send(f"**{user}** became a contributor")
            return await ctx.send(f"**{user}** was already a contributor")

        elif action == "rm" or action == "rem" or action == "remove":
            r = db_users.set_grade(user_id=user.id, grade="contributor", action=action)
            if r[0] != r[1]: return await ctx.send(f"**{user}** is not anymore a contributor")
            return await ctx.send(f"**{user}** doesn't be a contributor")
                
        return await ctx.send(f"The action **{action}** doesn't recognized, please use `rm`/`rem`/`remove` or `add`")

    @commands.command(aliases = ["get-logs", "get_logs"])
    @commands.check(is_it_owner)
    async def getlogs(self, ctx, log_type:str=None, log_moment:str=None):
        if log_type not in nebula_logging.good_log_types: return await ctx.send(f"Please give a valid log type\nLog types : `{'`, `'.join(nebula_logging.good_log_types)}`")
        if log_moment not in nebula_logging.good_log_moments: return await ctx.send(f"Please give a valid log moment\nLog moments : `{'`, `'.join(nebula_logging.good_log_moments)}`")
        logs = nebula_logging.get_logs(log_type, log_moment)
        if len(logs) > 0:
            for log in logs:
                e = discord.Embed(description = f"**TIME:** `{log.time}`\n**NAME:** `{log.name}`\n**LEVEL:** `{log.level_name}`\n**MESSAGE:** ```{log.message}```", color = MAINCOLOR)
                await ctx.send(embed=e)
            return
        await ctx.send(f"There are no {log_moment} {log_type} logs")


def setup(client):
    client.add_cog(BotOwner(client))
