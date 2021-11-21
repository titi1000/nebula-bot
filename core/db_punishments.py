import toml
import mysql.connector as mysql
from core.database import Database
import discord
import discord.ext.commands
from main import MAINCOLOR
import datetime


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
    
    # get punishment embed
    async def get_embed(self, ctx:discord.ext.commands.Context):
        member = ctx.guild.get_member(self.member_id)
        if member is None:
            try:
                member = await self.client.fetch_user(self.member_id)
            except:
                member = "member_not_found"

        moderator = ctx.guild.get_member(self.moderator_id)
        if moderator is None:
            try:
                moderator = await self.client.fetch_user(self.moderator_id)
                moderator_avatar_url = moderator.avatar_url
            except:
                moderator = "moderator_not_found"
                moderator_avatar_url = "images/default-avatar.png"
        else: moderator_avatar_url = moderator.avatar_url

        p_description = ""
        p_description+=f"**Member:** {member} \| {self.member_id}\n"
        p_description+=f"**Action:** {self.type}\n"
        if self.end_timestamp is not None:
            duration_timestamp = self.end_timestamp - self.start_timestamp
            duration = { "years" : 0, "months" : 0, "weeks" : 0, "days" : 0, "hours" : 0, "minutes" : 0, "seconds" : 0}
            while duration_timestamp >= 31536000:
                duration["years"] +=1
                duration_timestamp-=31536000
            while duration_timestamp >= 2592000:
                duration["months"]+=1
                duration_timestamp-=2592000
            while duration_timestamp >= 604800:
                duration["weeks"]+=1
                duration_timestamp-=604800
            while duration_timestamp >= 86400:
                duration["days"]+=1
                duration_timestamp-=86400
            while duration_timestamp >= 3600:
                duration["hours"]+=1
                duration_timestamp-=3600
            while duration_timestamp >= 60:
                duration["minutes"]+=1
                duration_timestamp-=60
            duration["seconds"]=duration_timestamp
                
            p_description+=f"**Duration:** "
            for k,v in duration.items():
                if v > 0: p_description+=f"{v}{k} "
            p_description+="\n"
        
        if self.reason == "": self.reason = "No reason was given"
        p_description+=f"**Reason:** {self.reason}"

        p_e = discord.Embed(description = p_description, color = MAINCOLOR, timestamp = datetime.datetime.fromtimestamp(float(self.start_timestamp)))
        p_e.set_author(name = moderator, icon_url=moderator_avatar_url)
        p_e.set_footer(text=f"Infraction #{self.id}")

        return p_e


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
        return self.db_execute(f"DROP TABLE IF EXISTS `{guild_id}`")
    
    # add guilds which are not in db and remove guilds too much
    def update(self):
        guild_ids = [guild.id for guild in self.client.guilds]
        for guild_id in guild_ids:
            self.add_guild(guild_id=guild_id)

        tables_result = self.db_fetchall("SHOW TABLES")
        if tables_result[0] is True:
            for table_name in tables_result[1]:
                if int(table_name[0]) not in guild_ids: self.remove_guild(table_name[0])

    # add a punishment
    def add_punishment(self, guild_id:int, member_id:int, type:str, start_timestamp:int, moderator_id:int=None, reason:str=None, end_timestamp:int=None):
        if type in self.punishments_types:
            if reason is None: reason = ""
            sql = f"INSERT INTO `{guild_id}`(`member_id`, `moderator_id`, `type`, `reason`, `start_timestamp`, `end_timestamp`) VALUES(%s, %s, %s, %s, %s, %s)"
            vars = (member_id, moderator_id, type, reason, start_timestamp, end_timestamp)
            r = self.db_execute(sql, vars)
            return r

    # remove a punishment
    def remove_punishment(self, guild_id, punishment_id):
        return self.db_execute(f"DELETE FROM `{guild_id}` WHERE `punishments_id`=%s", (punishment_id,))

    # get a punishment
    def get_punishment(self, guild_id, punishment_id):
        r = self.db_fetchone(f"SELECT * FROM `{guild_id}` WHERE `punishments_id`=%s", (punishment_id,))
        if r[0] and r[1] is not None: return (r[0], Punishment(guild_id, r[1]), r[2])
        return r


    # get member's punishments
    def get_member_punishments(self, guild_id, member_id):
        r = self.db_fetchall(f"SELECT * FROM `{guild_id}` WHERE `member_id`=%s", (member_id,))
        if r[0]:
            p_list = []
            for punishment in r[1]: p_list.append(Punishment(guild_id, punishment))
            return (r[0], p_list, r[2])
        return r


data = toml.load("config.toml")
db = data["databases"]["punishments"]
db_punishments = DBpunishments(db)