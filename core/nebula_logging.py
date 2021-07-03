import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
import glob
import os

date = datetime.datetime.today()
log_separator=" <<<+ separator +>>> "
time_separator=" <<<+ time +>>> "
name_separator=" <<<+ name +>>> "
level_name_separator=" <<<+ levelname +>>> "
message_separator=" <<<+ message +>>> "

logspath = "logs/"
paths = {
    "mysql" : f"{logspath}mysql/",
    "bot" : f"{logspath}bot/"
        }

class NebulaLogging:

    def __init__(self):

        if not os.path.isdir(logspath):
            os.mkdir(logspath)
        if not os.path.isdir(paths["mysql"]):
            os.mkdir(paths["mysql"])
        if not os.path.isdir(paths["bot"]):
            os.mkdir(paths["bot"])
    
        self.time_separator=time_separator
        self.name_separator=name_separator
        self.level_name_separator=level_name_separator
        self.message_separator=message_separator

        self.good_log_types = ["bot", "mysql"]
    
        formatter = logging.Formatter(f"{self.time_separator}%(asctime)s{self.time_separator}{self.name_separator}%(name)s{self.name_separator}{self.level_name_separator}%(levelname)s{self.level_name_separator}{self.message_separator}%(message)s{self.message_separator}{log_separator}")

        mysql_file = f"{paths['mysql']}{str(date.day).zfill(2)}-{str(date.month).zfill(2)}-{str(date.year).zfill(2)}_{str(date.hour).zfill(2)}-{str(date.minute).zfill(2)}"
        handler_mysql = TimedRotatingFileHandler(mysql_file, when="midnight", encoding='utf-8')
        handler_mysql.setFormatter(formatter)
        handler_mysql.setLevel(logging.DEBUG)

        self.logger_mysql = logging.getLogger(f"[MySQL]({__name__})")
        self.logger_mysql.setLevel(logging.DEBUG)
        self.logger_mysql.addHandler(handler_mysql)

        bot_file = f"{paths['bot']}{str(date.day).zfill(2)}-{str(date.month).zfill(2)}-{str(date.year).zfill(2)}_{str(date.hour).zfill(2)}-{str(date.minute).zfill(2)}"
        handler_bot = TimedRotatingFileHandler(bot_file, when="midnight", encoding='utf-8')
        handler_bot.setFormatter(formatter)
        handler_bot.setLevel(logging.DEBUG)

        self.logger_bot = logging.getLogger(f"[BOT]({__name__})")
        self.logger_bot.setLevel(logging.DEBUG)
        self.logger_bot.addHandler(handler_bot)
    
    def get_latest_logs(self, log_type):
        if log_type in self.good_log_types:
            path_file = f"{paths[log_type]}*"
            latest = max(glob.glob(path_file), key=os.path.getctime)
            with open(latest, "r") as file:
                file_content = file.read()

            logs_list = file_content.split(log_separator)
            del logs_list[-1]
            logs = []
            for log in logs_list:
                logs.append(Log(log))
            file.close()

            return logs

class Log:

    def __init__(self, log_string):
        self.time=log_string.split(time_separator)[1]
        self.name=log_string.split(name_separator)[1]
        self.level_name=log_string.split(level_name_separator)[1]
        self.message=log_string.split(message_separator)[1]

nebula_logging = NebulaLogging()