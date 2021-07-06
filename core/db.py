import toml
import mysql.connector as mysql
from core.database import Database

class DB(Database):

    def __init__(self, db):
        Database.__init__(self, db)

    # initialise the database
    def init(self):
        sql = """
            CREATE TABLE IF NOT EXISTS guilds(
                guild_id BIGINT UNSIGNED NOT NULL UNIQUE,
                prefix VARCHAR(10) DEFAULT '?',
                language VARCHAR(50) DEFAULT 'english',
                logs_id BIGINT UNSIGNED,
                welcome_id BIGINT UNSIGNED,
                welcome_message TEXT,
                leave_id BIGINT UNSIGNED,
                leave_message TEXT,
                autorole_id BIGINT UNSIGNED,
                blacklisted TEXT,
                moderator_roles TEXT,
                tickettool_id BIGINT UNSIGNED,
                tickettool_logs BIGINT UNSIGNED,
                muted_role BIGINT UNSIGNED,
				PRIMARY KEY(guild_id)
            )"""
        
        self.db_execute(sql)
    
    
    # get the prefix
    def get_prefix(self, client, message):
        if not message.guild:
            return "?"
        self.is_in_database_guild(message.guild.id)
        result = self.db_fetchone("SELECT `prefix` FROM guilds WHERE `guild_id` = %s", (message.guild.id,))
        if result[1][0] is None:
            return "?"
        return result[1][0]

    # check if guild is in data base
    def is_in_database_guild(self, guild_id):
        result = self.db_fetchone("SELECT `guild_id` FROM guilds WHERE `guild_id` = %s", (guild_id,))
        if result[1] is None:
            self.db_execute("INSERT INTO guilds(`guild_id`) VALUES (%s)", (guild_id,))

    # check if user is in data base
    def is_in_database_user(self, user_id):
        result = self.db_fetchone("SELECT `user_id` FROM users WHERE `user_id` = %s", (user_id,))
        if result[1] is None:
            self.db_execute("INSERT INTO users(`user_id`) VALUES (%s)", (user_id,))

    # find the logs channel
    def logs_channel(self, guild_id):
        self.is_in_database_guild(guild_id)
        result = self.db_fetchone("SELECT `logs_id` FROM guilds WHERE `guild_id` = %s", (guild_id,))
        return result

    # find the welcome channel
    def welcome_channel(self, guild_id):
        self.is_in_database_guild(guild_id)
        result = self.db_fetchone("SELECT `welcome_id` FROM guilds WHERE `guild_id` = %s", (guild_id,))
        return result

    # get welcome message
    def welcome_message(self, guild_id):
        self.is_in_database_guild(guild_id)
        result = self.db_fetchone("SELECT `welcome_message` FROM guilds WHERE `guild_id` = %s", (guild_id,))
        return result

    # find the leave channel
    def leave_channel(self, guild_id):
        self.is_in_database_guild(guild_id)
        result = self.db_fetchone("SELECT `leave_id` FROM guilds WHERE `guild_id` = %s", (guild_id,))
        return result

    # get leave message
    def leave_message(self, guild_id):
        self.is_in_database_guild(guild_id)
        result = self.db_fetchone("SELECT `leave_message` FROM guilds WHERE `guild_id` = %s", (guild_id,))
        return result

    # get autorole
    def get_autorole(self, guild_id):
        self.is_in_database_guild(guild_id)
        result = self.db_fetchone("SELECT `autorole_ids` FROM guilds WHERE `guild_id` = %s", (guild_id,))
        return result

    # get blacklisted channel
    def get_blacklisted(self, guild_id):
        self.is_in_database_guild(guild_id)
        result = self.db_fetchone("SELECT `blacklisted` FROM guilds WHERE `guild_id` = %s", (guild_id,))
        if result[1][0] is None:
            return ""
        else:
            return result[1][0]

    # get ticket tool message and channel id
    def get_tickettool(self, guild_id):
        self.is_in_database_guild(guild_id)
        result = self.db_fetchone("SELECT `tickettool_id` FROM guilds WHERE `guild_id` = %s", (guild_id,))
        if result[1][0] is None:
            return False
        else:
            return result[1][0].split(" ")

    # get ticket tool logs channel
    def get_tickettool_logs(self, guild_id):
        self.is_in_database_guild(guild_id)
        self.cursor.execute("SELECT tickettool_logs FROM guilds WHERE guild_id = ?", (guild_id,))
        result = self.cursor.fetchone()

        if result[1][0] is None:
            return False
        else:
            return result[1][0]
            

    # add/remove moderator role
    def manage_moderator_roles(self, guild_id, action:str, role_id:int):
        self.is_in_database_guild(guild_id)
        r_moderator_roles = self.get_moderator_roles(guild_id)
        if r_moderator_roles[0] is False:
            return r_moderator_roles
        moderator_roles = r_moderator_roles[1]
        moderator_roles_str = map(str, moderator_roles)
        if action == "add":
            if role_id in moderator_roles:
                return (True, (1, 1))
            else:
                moderator_roles = moderator_roles.append(role_id)
                roles_str = " ".join(moderator_roles_str)
                self.db_execute("UPDATE guilds SET `moderator_roles` = %s WHERE `guild_id` = %s", (roles_str, guild_id))
                return (True, (0, 1))

        elif action == "rm" or action == "rem" or action == "remove":
            if role_id in moderator_roles:
                moderator_roles = moderator_roles.remove(role_id)
                roles_str = " ".join(moderator_roles_str)
                if roles_str == "":
                    roles_str=None
                self.db_execute("UPDATE guilds SET `moderator_roles` = %s WHERE `guild_id` = %s", (roles_str, guild_id))
                return (True, (1, 0))
            else:
                return (True, (0, 0))

    # get moderator roles list
    def get_moderator_roles(self, guild_id):
        self.is_in_database_guild(guild_id)
        r_result_str = self.db_fetchone("SELECT `moderator_roles` FROM guilds WHERE `guild_id`=%s", (guild_id,))
        if r_result_str[0] is False:
            return r_result_str

        role_list = []
        if r_result_str[1][0] is not None:
            list = r_result_str[1][0].split(" ")
            for role in list:
                if role != "":
                    role_list.append(int(role))
        return (r_result_str[0], role_list, r_result_str[2])

    # set the muted role
    def set_muted_role(self, guild_id, muted_role_id):
        self.is_in_database_guild(guild_id)
        self.db_execute("INSERT INTO guilds(`muted_role`) VALUES(%s) WHERE `guild_id` = %s", (muted_role_id, guild_id))

    # get the muted role
    def get_muted_role(self, guild_id):
        self.is_in_database_guild(guild_id)
        result = self.db_fetchone("SELECT `muted_role` FROM guilds WHERE `guild_id` = %s", (guild_id,))
        return result[1][0]
        
        

data = toml.load("config.toml")
database = data["databases"]["guilds"]
db = DB(database)