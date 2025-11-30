"""
Final Project - ADEV-3005
2025-10-29, Tanner Agar
dbcm.py - Context manager for database operations
"""
import sqlite3 as sql
import logging as log


class DBCM():
    """
    Context manager class for handling database connection/cursor lifecycle.
    """

    # Logger for the class
    logger = log.getLogger(__name__)

    def __init__(self, db_name: str):
        """
        Construct the DBCM instance with database name, connection and cursor set to none.
        """
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """
        Entering the context manager: Connect to the database, create a cursor and return the cursor.
        """
        self.conn = sql.connect(self.db_name)
        log.info("Connected to database: %s", self.db_name)
        self.cursor = self.conn.cursor()
        log.info("Database cursor created.")
        return self.cursor

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Exiting the context manager: Close the cursor, and close the connection after comitting changes.
        return False propagates exceptions, if any occurred within the context.
        """
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.commit()
            self.conn.close()
            log.info("Database connection closed.")
        return False