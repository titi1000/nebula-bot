import discord
import sqlite3
import toml
from discord.ext import commands

class DB:

    def __init__(self, db_name):
        self.db_name = db_name
        self.db = sqlite3.connect(self.db_name)
        self.cursor = self.db.cursor()

    # initialise the database
    def init(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS guilds(
                guild_id INTEGER NOT NULL UNIQUE,
                prefix TEXT DEFAULT '?',
                language TEXT DEFAULT 'en',
                logs_id INTEGER,
                welcome_id INTEGER,
                welcome_message INTEGER,
                leave_id INTEGER,
                leave_message TEXT,
                autorole_id INTEGER,
                blacklisted TEXT,
                moderator_roles TEXT,
                tickettool_id INTEGER
            )""")
        
        self.commit()

    def get_prefix(self, client, message):
        if not message.guild:
            return "?"
        self.is_in_database_guild(message.guild.id)
        self.cursor.execute("SELECT prefix FROM guilds WHERE guild_id = ?", (message.guild.id,))
        result = self.cursor.fetchone()[0]
        if result is None:
            return "?"
        return result

    # commit in database
    def commit(self):
        self.db.commit()

    # check if guild is in data base
    def is_in_database_guild(self, guild_id):
        self.cursor.execute("SELECT guild_id FROM guilds WHERE guild_id = ?", (guild_id,))
        result = self.cursor.fetchone()
        if result is None:
            self.cursor.execute("INSERT INTO guilds(guild_id) VALUES (?)", (guild_id,))
            self.db.commit()

    # check if user is in data base
    def is_in_database_user(self, user_id):
        self.cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        if result is None:
            self.cursor.execute("INSERT INTO users(user_id) VALUES (?)", (user_id,))
            self.db.commit()

    # find the logs channel
    def logs_channel(self, guild_id):
        self.is_in_database_guild(guild_id)
        self.cursor.execute("SELECT logs_id FROM guilds WHERE guild_id = ?", (guild_id,))
        result = self.cursor.fetchone()

        if result[0] is None:
            return False
        else:
            return result[0]

    # find the welcome channel
    def welcome_channel(self, guild_id):
        self.is_in_database_guild(guild_id)
        self.cursor.execute("SELECT welcome_id FROM guilds WHERE guild_id = ?", (guild_id,))
        result = self.cursor.fetchone()

        if result[0] is None:
            return False
        else:
            return result[0]

    # get welcome message
    def welcome_message(self, guild_id):
        self.is_in_database_guild(guild_id)
        self.cursor.execute("SELECT welcome_message FROM guilds WHERE guild_id = ?", (guild_id,))
        result = self.cursor.fetchone()

        if result[0] is None:
            return False
        else:
            return result[0]

    # find the leave channel
    def leave_channel(self, guild_id):
        self.is_in_database_guild(guild_id)
        self.cursor.execute("SELECT leave_id FROM guilds WHERE guild_id = ?", (guild_id,))
        result = self.cursor.fetchone()

        if result[0] is None:
            return False
        else:
            return result[0]

    # get leave message
    def leave_message(self, guild_id):
        self.is_in_database_guild(guild_id)
        self.cursor.execute("SELECT leave_message FROM guilds WHERE guild_id = ?", (guild_id,))
        result = self.cursor.fetchone()

        if result[0] is None:
            return False
        else:
            return result[0]

    # get autorole
    def get_autorole(self, guild_id):
        self.is_in_database_guild(guild_id)
        self.cursor.execute("SELECT autorole_id FROM guilds WHERE guild_id = ?", (guild_id,))
        result = self.cursor.fetchone()

        if result[0] is None:
            return False
        else:
            return result[0]

    def get_blacklisted(self, guild_id):
        self.is_in_database_guild(guild_id)
        self.cursor.execute("SELECT blacklisted FROM guilds WHERE guild_id = ?", (guild_id,))
        result = self.cursor.fetchone()

        if result[0] is None:
            return ""
        else:
            return result[0]

    def get_tickettool(self, guild_id):
        self.is_in_database_guild(guild_id)
        self.cursor.execute("SELECT tickettool_id FROM guilds WHERE guild_id = ?", (guild_id,))
        result = self.cursor.fetchone()

        if result[0] is None:
            return False
        else:
            return result[0]


data = toml.load("config.toml")
database = data["database"]
db = DB(database)