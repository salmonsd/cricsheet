from utils.config import TABLE_CONFIG
from utils.db_utils import get_db_connection

import logging

def setup_db():
    """
    Gets a db connectios and then iterates 
    through table DDLs to create db tables
    """
    con = get_db_connection()

    with con:

        for table, ddl in TABLE_CONFIG.items():
            logging.info(f"{__name__}: creating table - {table}")
            con.execute(ddl)

if __name__ == "__main__":
    setup_db()