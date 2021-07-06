import mysql.connector as mysql
from core.nebula_logging import nebula_logging

class Database:

    def __init__(self, db):
        self.name = db["name"]
        self.host = db["host"]
        self.port = db["port"]
        self.user = db["user"]
        self.password = db["password"]

    # execute sql request
    def db_execute(self, sql, vars:tuple=None):
        try:
            connection = mysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.name
            )
            cursor = connection.cursor()

            if vars is not None:
                cursor.execute(sql, vars)
            else:
                cursor.execute(sql)
            connection.commit()
            r = (True, None, None)

        except Exception as e:
            print(f"[ERROR ({self.__class__}.db_execute)]: {e}")
            connection.rollback()
            r = (False, e, (sql, vars))
            nebula_logging.logger_mysql.error(f"An error was occured during this request : {self.__class__}.db_execute({sql}, {vars})")


        finally:
            connection.close()
            return r

    # fetchone the result of sql script
    def db_fetchone(self, sql, vars:tuple=None):
        try:
            connection = mysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.name
            )
            cursor = connection.cursor()

            if vars is not None:
                cursor.execute(sql, vars)
            else:
                cursor.execute(sql)
            result = cursor.fetchone()
            r = (True, result, None)

        except Exception as e:
            print(f"[ERROR ({self.__class__}.db_fetchone)]: {e}")
            r = (False, e, (sql, vars))
            nebula_logging.logger_mysql.error(f"An error was occured during this request : {self.__class__}.db_fetchone({sql}, {vars})")

        finally:
            connection.close()
            return r

    # fetchall the result of sql script
    def db_fetchall(self, sql, vars:tuple=None):
        try:
            connection = mysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.name
            )
            cursor = connection.cursor()

            if vars is not None:
                cursor.execute(sql, vars)
            else:
                cursor.execute(sql)
            result = cursor.fetchall()
            r = (True, result, None)

        except Exception as e:
            print(f"[ERROR ({self.__class__}.db_fetchall)]: {e}")
            r = (False, e, (sql, vars))
            nebula_logging.logger_mysql.error(f"An error was occured during this request : {self.__class__}.db_fetchall({sql}, {vars})")

        finally:
            connection.close()
            return r