import sqlite3

class DB_lang:

    def __init__(self):
        lang_connection = sqlite3.connect('lang.sqlite3')
        ram_connection = sqlite3.connect(':memory:')
        lang_connection.backup(ram_connection)
        self.connection = ram_connection

    def getText(self, lang, key):
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT {lang} FROM langs WHERE key = ?", (key,))
        fetch = cursor.fetchone()
        if fetch is None: return "Error text"
        return fetch[0]

db_lang = DB_lang()