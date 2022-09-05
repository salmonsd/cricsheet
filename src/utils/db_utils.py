import sqlite3

DB_NAME = "./db/odi_cricsheet.db"

def get_db_connection(db: str = DB_NAME):
    return sqlite3.connect(db)