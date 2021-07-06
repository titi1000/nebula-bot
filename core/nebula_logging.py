import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
import glob
import os
import discord
import toml
import json

data = toml.load("config.toml")
ERRORCOLOR = int(data["error_color"], 0)

with open("plugins/plugins.json") as data:
    error_channel_id = json.load(data)["customerrors"]["channel_id"]

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

async def report_error(client, ctx, r):
    error_channel = await client.fetch_channel(error_channel_id)
    await error_channel.send(embed=discord.Embed(
        title="Error report",
        description=f"**Author:** ({ctx.author} | {ctx.author.id})\n**Server:** ({ctx.guild} | {ctx.guild.id})\n**Command:** {ctx.message.content}\n**MySQL request:** ```{r[2]}```\n**Error:** ```{r[1]}```",
        color = ERRORCOLOR
    ))
    await ctx.send("An error was occured, a report has been sent.")

async def report_error_with_member(client, member, r, fonction):
    error_channel = await client.fetch_channel(error_channel_id)
    await error_channel.send(embed=discord.Embed(
        title="Error report",
        description=f"**Author:** ({member} | {member.id})\n**Server:** ({member.guild} | {member.guild.id})\n**Fonction:** {fonction}\n**MySQL request:** ```{r[2]}```\n**Error:** ```{r[1]}```",
        color = ERRORCOLOR
    ))

async def report_error_with_message(client, message, r, fonction):
    error_channel = await client.fetch_channel(error_channel_id)
    await error_channel.send(embed=discord.Embed(
        title="Error report",
        description=f"**Author:** ({message.author} | {message.author.id})\n**Server:** ({message.guild} | {message.guild.id})\n**Fonction:** {fonction}\n**MySQL request:** ```{r[2]}```\n**Error:** ```{r[1]}```",
        color = ERRORCOLOR
    ))

async def report_error_with_channel(client, channel, r, fonction):
    error_channel = await client.fetch_channel(error_channel_id)
    await error_channel.send(embed=discord.Embed(
        title="Error report",
        description=f"**Server:** ({channel.guild} | {channel.guild.id})\n**Fonction:** {fonction}\n**MySQL request:** ```{r[2]}```\n**Error:** ```{r[1]}```",
        color = ERRORCOLOR
    ))


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
        self.good_log_moments = ["latest", "current"]
    
        formatter = logging.Formatter(f"{self.time_separator}%(asctime)s{self.time_separator}{self.name_separator}%(name)s{self.name_separator}{self.level_name_separator}%(levelname)s{self.level_name_separator}{self.message_separator}%(message)s{self.message_separator}{log_separator}")

        mysql_file = f"{paths['mysql']}{str(date.day).zfill(2)}-{str(date.month).zfill(2)}-{str(date.year).zfill(2)}_{str(date.hour).zfill(2)}-{str(date.minute).zfill(2)}.log"
        handler_mysql = TimedRotatingFileHandler(mysql_file, when="midnight", encoding='utf-8')
        handler_mysql.setFormatter(formatter)
        handler_mysql.setLevel(logging.DEBUG)

        self.logger_mysql = logging.getLogger(f"[MySQL]({__name__})")
        self.logger_mysql.setLevel(logging.DEBUG)
        self.logger_mysql.addHandler(handler_mysql)

        bot_file = f"{paths['bot']}{str(date.day).zfill(2)}-{str(date.month).zfill(2)}-{str(date.year).zfill(2)}_{str(date.hour).zfill(2)}-{str(date.minute).zfill(2)}.log"
        handler_bot = TimedRotatingFileHandler(bot_file, when="midnight", encoding='utf-8')
        handler_bot.setFormatter(formatter)
        handler_bot.setLevel(logging.DEBUG)

        self.logger_bot = logging.getLogger(f"[BOT]({__name__})")
        self.logger_bot.setLevel(logging.DEBUG)
        self.logger_bot.addHandler(handler_bot)
    
    def get_logs(self, log_type, log_moment):
        if log_type in self.good_log_types:
            path_file = f"{paths[log_type]}*.log"

            files = glob.glob(path_file)
            files.sort(key=os.path.getmtime)

            if log_moment.lower() == "current":
                logfile = files[-1]
            elif log_moment.lower() == "latest":
                logfile = files[-2]
            else:
                return

            with open(logfile, "r") as file:
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