import toml
import mysql.connector as mysql
from core.database import Database


class Punishment:

    def __init__(self, guild_id:int, infos:tuple):
        self.guild_id = guild_id
        self.id = infos[0]
        self.member_id = infos[1]
        self.moderator_id = infos[2]
        self.type = infos[3]
        self.reason = infos[4]
        self.start_timestamp = infos[5]
        self.end_timestamp = infos[6]

class DBpunishments(Database):

    def __init__(self, db):
        Database.__init__(self, db)
        self.punishments_types = ["warn", "kick", "ban", "tempban"]
        self.temp_punishments = ["tempban"]

    # add a table db for guild's punishments
    def add_guild(self, guild_id):
        sql = f"""CREATE TABLE IF NOT EXISTS `{guild_id}` (
                punishments_id SMALLINT UNSIGNED PRIMARY KEY NOT NULL UNIQUE AUTO_INCREMENT,
                member_id BIGINT UNSIGNED NOT NULL,
                moderator_id BIGINT UNSIGNED,
                type VARCHAR(8),
                reason VARCHAR(255),
                start_timestamp	INTEGER UNSIGNED NOT NULL,
                end_timestamp INTEGER UNSIGNED
            );"""
        self.db_execute(sql)

    # remove the table db for guild's punishments
    def remove_guild(self, guild_id):
        return self.db_execute(f"DROP TABLE `{guild_id}`")

    # add a punishment
    def add_punishment(self, guild_id:int, member_id:int, type:str, start_timestamp:int, moderator_id:int=None, reason:str=None, end_timestamp:int=None):
        if type in self.punishments_types:
            if reason is None:
                reason = ""
            sql = f"INSERT INTO `{guild_id}`(`member_id`, `moderator_id`, `type`, `reason`, `start_timestamp`, `end_timestamp`) VALUES(%s, %s, %s, %s, %s, %s)"
            vars = (member_id, moderator_id, type, reason, start_timestamp, end_timestamp)
            
            if type in self.temp_punishments:
                if end_timestamp is not None:
                    r = self.db_execute(sql, vars)
                else:
                    r = (False, "NeedEnd_Timestamp")
            else:
                r = self.db_execute(sql, vars)
        else:
            r = (False, "BadPunishmentsType")

    # remove a punishment
    def remove_punishment(self, guild_id, punishment_id):
        return self.db_execute(f"DELETE FROM `{guild_id}` WHERE `punishment_id`=%s", (punishment_id,))

    # get a punishment
    def get_punishment(self, guild_id, punishment_id):
        r = self.db_fetchone(f"SELECT * FROM `{guild_id}` WHERE `punishments_id`=%s", (punishment_id,))
        if r[1] is not None and r[0]:
            return Punishment(guild_id, r[1])
        elif r[1] is None and r[0]:
            return None
        else:
            return r

    # get member's punishments
    def get_member_punishments(self, guild_id, member_id):
        r = self.db_fetchall(f"SELECT * FROM `{guild_id}` WHERE `member_id`=%s", (member_id,))
        if r[1] is not None and r[0]:
            p_list = []
            for punishment in r[1]:
                p_list.append(Punishment(guild_id, punishment))
            return p_list
        else:
            return r


data = toml.load("config.toml")
db = data["databases"]["punishments"]
db_punishments = DBpunishments(db)