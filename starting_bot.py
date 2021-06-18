import discord
from discord.ext import commands
import os
from threading import Thread
import subprocess

client = commands.Bot(command_prefix="1!", help_command=None)
TOKEN = "ODU1MzM5MTI4MDI3MzQ5MDIy.YMxCow.MEFCdBo79ZINsNazXbNoVIIYWXw"

@client.command(name = "start")
async def start(ctx):
    t1 = Thread(target=subprocess.run, args=(["python", "bot2.py"],))
    t1.start()
    
@client.command(name = "test")
async def test(ctx):
    await ctx.send("Test")

client.run(TOKEN)
