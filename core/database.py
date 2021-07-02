import mysql.connector as mysql

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
            r = (True,)

        except Exception as e:
            print(f"[ERROR ({self.__class__}.db_execute)]: {e}")
            connection.rollback()
            r = (False, e)

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
            r = (True, result)

        except Exception as e:
            print(f"[ERROR ({self.__class__}.db_fetchone)]: {e}")
            r = (False, e)

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
            r = (True, result)

        except Exception as e:
            print(f"[ERROR ({self.__class__}.db_fetchall)]: {e}")
            r = (False, e)

        finally:
            connection.close()
            return r