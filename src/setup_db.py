import sys
import logging

from utils.config import TABLE_CONFIG
from utils.db_utils import get_db_connection
from utils.logger_utils import get_logger


# setup logging
py_file = __file__.split("/")[-1]
logger = get_logger(name=f"{py_file}:{__name__}")


def setup_db():
    """
    Gets a db connection and then iterates
    through table DDLs to create db tables
    """
    logger.info("Getting DB Connection")
    conn = get_db_connection()

    try:
        with conn:
            logger.info(f"Processing {len(TABLE_CONFIG)} tables for setup")
            for table, ddl in TABLE_CONFIG.items():
                logger.info(f"Creating table - {table}")
                conn.execute(ddl)

            logger.info("Done setting up!")

    except Exception as e:
        logger.error(e)

    finally:
        logger.info("Closing DB Connection")
        conn.close()


if __name__ == "__main__":
    setup_db()
