import sqlite3 as sql

"""
Final Project - ADEV-3005
2025-10-29, Tanner Agar
dbcm.py - Context manager for database operations
"""



"""
Context manager class for handling database connection/cursor lifecycle.
"""
class DBCM():

    def __init__(self, db_name: str):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sql.connect(self.db_name)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.commit()
            self.conn.close()
        return False

