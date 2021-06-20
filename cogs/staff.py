from core.others import is_it_owner
import discord
from discord.ext import commands
import sqlite3
import datetime
from core.db_user import db_users
from core.others import is_it_owner
from main import MAINCOLOR

class Staff(commands.Cog):

    def __init__(self, client):
        self.client = client
        print("Staff cog well loaded.")

    @commands.command(name = "staff")
    @commands.check(is_it_owner)
    async def staff(self, ctx, action:str, user:discord.User):
        db_users.is_in_database_user(user.id)
        action = action.lower()

        if action == "add":
            r = db_users.set_grade(user_id=user.id, grade="staff", action=action)
            if r[0] != r[1]:
                await ctx.send(f"**{user}** became a staff")
            else:
                await ctx.send(f"**{user}** was already a staff")

        elif action == "rem" or action == "remove":
            r = db_users.set_grade(user_id=user.id, grade="staff", action=action)
            if r[0] != r[1]:
                await ctx.send(f"**{user}** is not anymore a staff")
            else:
                await ctx.send(f"**{user}** doesn't be a staff")
        
        else:
            await ctx.send(f"The action **{action}** doesn't recognized, please use `rem`/`remove` or `add`")


def setup(client):
    client.add_cog(Staff(client))