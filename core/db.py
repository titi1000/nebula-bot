import toml
import datetime
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
                autorole_ids TEXT,
                blacklisted TEXT,
                moderator_roles TEXT,
                tickettool_id TEXT,
                tickettool_logs BIGINT UNSIGNED,
                muted_role BIGINT UNSIGNED,
								                 PRIMARY KEY(guild_id)

            )"""
            
        sql2 = """   
                CREATE TABLE IF NOT EXISTS giveaways(
                channel_id BIGINT UNSIGNED,
                message_id BIGINT UNSIGNED,
                prize TEXT,
                winners_number SMALLINT UNSIGNED,
                giveaway_end TIMESTAMP
            )"""
        
        self.db_execute(sql2)
        self.db_execute(sql)
    
    
    # get the prefix
    def get_prefix(self, client, message):
        if not message.guild: return "?"
        self.is_in_database_guild(message.guild.id)
        result = self.db_fetchone("SELECT `prefix` FROM guilds WHERE `guild_id` = %s", (message.guild.id,))
        return result[1][0]

    # check if guild is in data base and add if not
    def is_in_database_guild(self, guild_id):
        result = self.db_fetchone("SELECT `guild_id` FROM guilds WHERE `guild_id` = %s", (guild_id,))
        if result[1] is None: self.db_execute("INSERT INTO guilds(`guild_id`) VALUES (%s)", (guild_id,))
    
    # remove guild from database
    def remove_guild(self, guild_id):
        result = self.db_fetchone("SELECT `guild_id` FROM guilds WHERE `guild_id` = %s", (guild_id,))
        if result[1] is not None: self.db_execute("DELETE FROM guilds WHERE `guild_id` = %s", (guild_id,))
    
    # add guilds which are not in db and remove guilds too much
    def update(self, guilds):
        guild_ids = [guild.id for guild in guilds]
        for guild_id in guild_ids:
            self.is_in_database_guild(guild_id=guild_id)

        guilds_result = self.db_fetchall("SELECT `guild_id` FROM guilds")
        if guilds_result[0] is True:
            for guild_id in guilds_result[1]:
                if int(guild_id[0]) not in guild_ids: self.remove_guild(guild_id[0])

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
    
    # get lang
    def get_lang(self, guild_id):
        self.is_in_database_guild(guild_id)
        result = self.db_fetchone("SELECT `lang` FROM guilds WHERE `guild_id` = %s", (guild_id,))
        return result

    # get blacklisted channel
    def get_blacklisted(self, guild_id):
        self.is_in_database_guild(guild_id)
        result = self.db_fetchone("SELECT `blacklisted` FROM guilds WHERE `guild_id` = %s", (guild_id,))
        if result[1][0] is None: return ""
        return result[1][0]

    # get ticket tool message and channel id
    def get_tickettool(self, guild_id):
        self.is_in_database_guild(guild_id)
        result = self.db_fetchone("SELECT `tickettool_id` FROM guilds WHERE `guild_id` = %s", (guild_id,))
        if result[1][0] is not None: return (result[0], result[1][0].split(" "), result[2])
        return result

    # get ticket tool logs channel
    def get_tickettool_logs(self, guild_id):
        self.is_in_database_guild(guild_id)
        result = self.db_fetchone("SELECT `tickettool_logs` FROM guilds WHERE `guild_id` = %s", (guild_id,))
        return result
            

    # add/remove moderator role
    def manage_moderator_roles(self, guild_id, action:str, role_id:int):
        self.is_in_database_guild(guild_id)
        r_moderator_roles = self.get_moderator_roles(guild_id)
        if r_moderator_roles[0] is False: return r_moderator_roles
        moderator_roles = r_moderator_roles[1]
        moderator_roles_str = map(str, moderator_roles)
        if action == "add":
            if role_id in moderator_roles: return (True, (1, 1))
            
            moderator_roles = moderator_roles.append(role_id)
            roles_str = " ".join(moderator_roles_str)
            self.db_execute("UPDATE guilds SET `moderator_roles` = %s WHERE `guild_id` = %s", (roles_str, guild_id))
            return (True, (0, 1))

        elif action == "rm" or action == "rem" or action == "remove":
            if role_id in moderator_roles:
                moderator_roles = moderator_roles.remove(role_id)
                roles_str = " ".join(moderator_roles_str)
                if roles_str == "": roles_str=None
                self.db_execute("UPDATE guilds SET `moderator_roles` = %s WHERE `guild_id` = %s", (roles_str, guild_id))
                return (True, (1, 0))
            return (True, (0, 0))

    # get moderator roles list
    def get_moderator_roles(self, guild_id):
        self.is_in_database_guild(guild_id)
        r_result_str = self.db_fetchone("SELECT `moderator_roles` FROM guilds WHERE `guild_id`=%s", (guild_id,))
        if r_result_str[0] is False: return r_result_str

        role_list = []
        if r_result_str[1][0] is not None:
            list = r_result_str[1][0].split(" ")
            for role in list:
                if role != "": role_list.append(int(role))
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

    # insert a new giveaway
    def insert_giveaway(self, channel_id, message_id, prize, winners, timestamp):
        r = self.db_execute("INSERT INTO giveaways(`channel_id`, `message_id`, `prize`, `winners_number`, `giveaway_end`) VALUES (%s, %s, %s, %s, %s)", (channel_id, message_id, prize, winners, timestamp))
        return r

    # get all giveaways finished
    def get_giveaways_finished(self):
        result = db.db_fetchall("SELECT `channel_id`, `message_id`, `prize`, `winners_number` FROM giveaways WHERE `giveaway_end` <= %s", (datetime.datetime.now(),))
        return result


data = toml.load("config.toml")
database = data["databases"]["guilds"]
db = DB(database)