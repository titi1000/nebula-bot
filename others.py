import sqlite3
import discord

# check if guild is in data base
def is_in_database_guild(guild_id):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute("SELECT guild_id FROM guilds WHERE guild_id = ?", (guild_id,))
    result = cursor.fetchone()
    if result is None:
        cursor.execute("INSERT INTO guilds(guild_id) VALUES (?)", (guild_id,))
        db.commit()
        cursor.close()

# check if user is in data base
def is_in_database_user(user_id):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if result is None:
        cursor.execute("INSERT INTO users(user_id) VALUES (?)", (user_id,))
        db.commit()
        cursor.close()

# find the logs channel
def logs_channel(guild_id):
    is_in_database_guild(guild_id)
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute("SELECT logs_id FROM guilds WHERE guild_id = ?", (guild_id,))
    result = cursor.fetchone()

    if result[0] is None:
        return False
    else:
        return result[0]

# find the welcome channel
def welcome_channel(guild_id):
    is_in_database_guild(guild_id)
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute("SELECT welcome_id FROM guilds WHERE guild_id = ?", (guild_id,))
    result = cursor.fetchone()

    if result[0] is None:
        return False
    else:
        return result[0]

# get welcome message
def welcome_message(guild_id):
    is_in_database_guild(guild_id)
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute("SELECT welcome_message FROM guilds WHERE guild_id = ?", (guild_id,))
    result = cursor.fetchone()

    if result[0] is None:
        return False
    else:
        return result[0]

# get a channel by his id
async def get_channel_by_id(guild, id):
    try:
        await guild.fetch_channels()
        channel = discord.utils.get(guild.channels, id=id)
        return channel
    except:
        return None