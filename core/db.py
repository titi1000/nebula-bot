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
                muted_role INTEGER
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

    # get blacklisted channel
    def get_blacklisted(self, guild_id):
        self.is_in_database_guild(guild_id)
        self.cursor.execute("SELECT blacklisted FROM guilds WHERE guild_id = ?", (guild_id,))
        result = self.cursor.fetchone()

        if result[0] is None:
            return ""
        else:
            return result[0]

    # add/remove moderator role
    def manage_moderator_roles(self, guild_id, action:str, role_id:int):
        self.is_in_database_guild(guild_id)
        moderator_roles = self.get_moderator_roles(guild_id)
        moderator_roles_str = map(str, moderator_roles)
        if action == "add":
            if role_id in moderator_roles:
                return (1, 1)
            else:
                moderator_roles = moderator_roles.append(role_id)
                roles_str = " ".join(moderator_roles_str)
                self.cursor.execute("UPDATE guilds SET moderator_roles = ? WHERE guild_id = ?", (roles_str, guild_id))
                return (0, 1)

        elif action == "rm" or action == "rem" or action == "remove":
            if role_id in moderator_roles:
                moderator_roles = moderator_roles.remove(role_id)
                roles_str = " ".join(moderator_roles_str)
                if roles_str == "":
                    roles_str=None
                self.cursor.execute("UPDATE guilds SET moderator_roles = ? WHERE guild_id = ?", (roles_str, guild_id))
                return (1, 0)
            else:
                return (0, 0)

    # get moderator roles list
    def get_moderator_roles(self, guild_id):
        self.is_in_database_guild(guild_id)
        self.cursor.execute("SELECT moderator_roles FROM guilds WHERE guild_id=?", (guild_id,))
        result_str = self.cursor.fetchone()

        role_list = []
        if result_str[0] is not None:
            list = result_str[0].split(" ")
            for role in list:
                if role != "":
                    role_list.append(int(role))
        
        return role_list

    # set the muted role
    def set_muted_role(self, guild_id, muted_role_id):
        self.is_in_database_guild(guild_id)
        self.cursor.execute("INSERT INTO guilds(muted_role) VALUES(?) WHERE guild_id = ?", (muted_role_id, guild_id))

    # get the muted role
    def get_muted_role(self, guild_id):
        self.is_in_database_guild(guild_id)
        self.cursor.execute("SELECT muted_role FROM guilds WHERE guild_id = ?", (guild_id,))
        return self.cursor.fetchone()[0]
        


data = toml.load("config.toml")
database = data["database"]
db = DB(database)