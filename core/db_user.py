from core.database import Database
import toml
import mysql.connector as mysql
from core.database import Database

class DBuser(Database):

    def __init__(self, db):
        Database.__init__(self, db)
        self.tables = ["stats", "grades", "others"]

    # initialise the database
    def init(self):

        sql = """CREATE TABLE IF NOT EXISTS stats (
            user_id	BIGINT UNSIGNED NOT NULL UNIQUE,
            command_count MEDIUMINT UNSIGNED NOT NULL DEFAULT 0,
            suggest_count SMALLINT UNSIGNED NOT NULL DEFAULT 0,
            report_count SMALLINT UNSIGNED NOT NULL DEFAULT 0,
            PRIMARY KEY(user_id)
        );"""
        self.db_execute(sql)
        sql = """CREATE TABLE IF NOT EXISTS grades (
            user_id BIGINT UNSIGNED NOT NULL UNIQUE,
            vip	TINYINT NOT NULL DEFAULT 0,
            blacklisted	TINYINT NOT NULL DEFAULT 0,
            staff TINYINT NOT NULL DEFAULT 0,
            contributor TINYINT NOT NULL DEFAULT 0,
            PRIMARY KEY(user_id)
        );"""
        self.db_execute(sql)
        sql = """CREATE TABLE IF NOT EXISTS others (
            user_id	BIGINT UNSIGNED NOT NULL UNIQUE,
            bs_tag VARCHAR(20),
            coc_tag	VARCHAR(20),
            PRIMARY KEY(user_id)
        );"""
        self.db_execute(sql)

    # check if user is in data base and add them
    def is_in_database_user(self, user_id):
        for table in self.tables:
            result = self.db_fetchone(f"SELECT `user_id` FROM {table} WHERE `user_id` = %s", (user_id,))

            if result[0] == True and result[1] is None:
                self.db_execute(f"INSERT INTO {table}(`user_id`) VALUES (%s)", (user_id,))
                
    # get command count
    def get_command_count(self, user_id):
        result = self.db_fetchone("SELECT `command_count` FROM stats WHERE `user_id` = %s", (user_id,))
        if result[0]:
            return result[1][0]

    # get suggest count
    def get_suggest_count(self, user_id):
        result = self.db_fetchone("SELECT `suggest_count` FROM stats WHERE `user_id` = %s", (user_id,))
        if result[0]:
            return result[1][0]

    # get report count
    def get_report_count(self, user_id):
        result = self.db_fetchone("SELECT `suggest_count` FROM stats WHERE `user_id` = %s", (user_id,))
        if result[0]:
            return result[1][0]

    # add report/suggest/command count
    def add_to_counter(self, user_id, counter:str, n:int=1):
        counters = {
            "report":self.get_report_count,
            "suggest":self.get_suggest_count,
            "command":self.get_command_count
        }
        if counter in counters:
            last_count = counters[counter](user_id)
            new_count = last_count + n
            self.set_counter(user_id, counter, new_count)
            return (last_count, new_count)

        else:
            print("Counter not valid")

    # set report/suggest/command count
    def set_counter(self, user_id, counter:str, new_count:int):
        counters = {
            "report":self.get_report_count,
            "suggest":self.get_suggest_count,
            "command":self.get_command_count
        }
        if counter in counters:
            last_count = counters[counter](user_id)
            self.db_execute(f"UPDATE stats SET `{counter}_count`=%s WHERE `user_id`=%s", (new_count, user_id))
            return (last_count, new_count)
    
        else:
            print("Counter not valid")

    # check if the user is vip
    def is_vip(self, user_id):
        result = self.db_fetchone("SELECT `vip` FROM grades WHERE `user_id` = %s", (user_id,))
        if result[0]:
            return bool(result[1][0])

    # check if the user is a staff
    def is_staff(self, user_id):
        result = self.db_fetchone("SELECT `staff` FROM grades WHERE `user_id` = %s", (user_id,))
        if result[0]:
            return bool(result[1][0])

    # check if the user is a contributor
    def is_contributor(self, user_id):
        result = self.db_fetchone("SELECT `contributor` FROM grades WHERE `user_id` = %s", (user_id,))
        if result[0]:
            return bool(result[1][0])

    # check if the user is blacklisted
    def is_blacklisted(self, user_id):
        result = self.db_fetchone("SELECT `blacklisted` FROM grades WHERE `user_id` = %s", (user_id,))
        if result[0]:
            return bool(result[1][0])

    # set grade to a user
    def set_grade(self, user_id, grade:str, action:str):
        grades = {
            "vip":self.is_vip,
            "staff":self.is_staff,
            "contributor":self.is_contributor,
            "blacklisted":self.is_blacklisted
        }
        
        last_grade = grades[grade](user_id)
        if action=="add":
            new_grade = 1
            if new_grade != last_grade:
                self.db_execute(f"UPDATE grades SET `{grade}`=%s WHERE `user_id`=%s", (new_grade, user_id))
            return (last_grade, new_grade)

        elif action == "rem" or action == "remove":
            new_grade = 0
            if new_grade != last_grade:
                self.db_execute(f"UPDATE grades SET `{grade}`=%s WHERE `user_id`=%s", (new_grade, user_id))
            return (last_grade, new_grade)

        else:
            print("grade not valid")

    # get bs tag of a user
    def get_bs_tag(self, user_id):
        result = self.db_fetchone("SELECT `bs_tag` FROM others WHERE `user_id` = %s", (user_id,))
        if result[0]:
            return result[1][0]
    
    # set bs tag of a user
    def set_bs_tag(self, user_id, bs_tag):
        result = self.db_execute(f"UPDATE others SET `bs_tag`='{bs_tag}' WHERE `user_id`=%s", (user_id,))
        return result[0]

    # get coc tag of a user
    def get_coc_tag(self, user_id):
        result = self.db_fetchone("SELECT `coc_tag` FROM others WHERE `user_id` = %s", (user_id,))
        if result[0]:
            return result[1][0]

    # set coc tag of a user
    def set_coc_tag(self, user_id, coc_tag):
        result = self.db_execute(f"UPDATE others SET `coc_tag`='{coc_tag}' WHERE `user_id`=%s", (user_id,))
        return result[0]

data = toml.load("config.toml")
db = data["databases"]["users"]
db_users = DBuser(db)