import sqlite3

DB_FILE = "./db/odi_cricsheet.db"


def get_db_connection(db_file: str = DB_FILE):
    """
    create a database connection to the SQLite
    database specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except:
        print("ERROR: Unable to connect to sqlite")

    return conn
