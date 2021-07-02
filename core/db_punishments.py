import sqlite3
import toml
from discord.ext import commands


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

class DBpunishments:

    def __init__(self, db_name):
        self.db_name = db_name
        self.db = sqlite3.connect(self.db_name)
        self.cursor = self.db.cursor()
        self.punishments_types = ["warn", "kick", "ban", "tempban"]
        self.temp_punishments = ["tempban"]        

    # execute sql request
    def db_execute(self, sql, vars:tuple=None):
        try:
            if vars is not None:
                self.cursor.execute(sql, vars)
            else:
                self.cursor.execute(sql)
            self.db.commit()
            r = (True,)

        except Exception as e:
            print(f"[ERROR (DBuser.db_execute)]: {e}")
            self.db.rollback()
            r = (False, e)

        finally:
            return r

    # fetchone the result of sql script
    def db_fetchone(self, sql, vars:tuple=None):
        try:
            if vars is not None:
                self.cursor.execute(sql, vars)
            else:
                self.cursor.execute(sql)
            result = self.cursor.fetchone()
            r = (True, result)

        except Exception as e:
            print(f"[ERROR (DBuser.db_fetchone)]: {e}")
            r = (False, e)

        finally:
            return r
    
    # fetchall the result of sql script
    def db_fetchall(self, sql, vars:tuple=None):
        try:
            if vars is not None:
                self.cursor.execute(sql, vars)
            else:
                self.cursor.execute(sql)
            result = self.cursor.fetchall()
            r = (True, result)

        except Exception as e:
            print(f"[ERROR (DBuser.db_fetchall)]: {e}")
            r = (False, e)

        finally:
            return r
    

    # add a table db for guild's punishments
    def add_guild(self, guild_id):
        sql = f"""CREATE TABLE IF NOT EXISTS "{guild_id}" (
                "punishments_id"	INTEGER NOT NULL UNIQUE,
                "member_id"	INTEGER NOT NULL,
                "moderator_id"	INTEGER,
                "type"	TEXT NOT NULL,
                "reason"	TEXT,
                "start_timestamp"	INTEGER NOT NULL,
                "end_timestamp"	INTEGER,
                PRIMARY KEY("punishments_id")
            );"""
        self.db_execute(sql)

    # remove the table db for guild's punishments
    def remove_guild(self, guild_id):
        return self.db_execute(f"DROP TABLE {guild_id}")

    # add a punishment
    def add_punishment(self, guild_id:int, member_id:int, type:str, start_timestamp:int, moderator_id:int=None, reason:str=None, end_timestamp:int=None):
        if type in self.punishments_types:
            sql = f"INSERT INTO '{guild_id}'(member_id, moderator_id, type, reason, start_timestamp, end_timestamp) VALUES(?, ?, ?, ?, ?, ?)"
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
        return self.db_execute(f"DELETE FROM `{guild_id}` WHERE punishment_id=?", (punishment_id,))

    # get a punishment
    def get_punishment(self, guild_id, punishment_id):
        r = self.db_fetchone(f"SELECT * FROM '{guild_id}' WHERE punishments_id=?", (punishment_id,))
        if r[1] is not None and r[0]:
            return Punishment(guild_id, r[1])
        elif r[1] is None and r[0]:
            return None
        else:
            return r

    # get member's punishments
    def get_member_punishments(self, guild_id, member_id):
        r = self.db_fetchall(f"SELECT * FROM '{guild_id}' WHERE member_id=?", (member_id,))
        if r[1] is not None and r[0]:
            p_list = []
            for punishment in r[1]:
                p_list.append(Punishment(guild_id, punishment))
            return p_list
        else:
            return r



data = toml.load("config.toml")
database = data["database_punishments"]
db_punishments = DBpunishments(database)