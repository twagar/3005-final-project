import datetime as datetime
import sqlite3 as sql
import scrape_weather as scrape
import dbcm
"""
Final Project - ADEV-3005
2025-10-29, Tanner Agar
db_operations.py - Database operations for weather data
"""


# Do not inherit DBCM, composition includes it as an attribue - initialize.
class DBOperations():

    # Input is a dictionary from WeatherScraper class: date, min temp, max temp, mean temp.
    def __init__(self, db_name):

        # db link
        self.db_manager = dbcm.DBCM(db_name)
        # scraper
        self.scraper = scrape.WeatherScraper()
        # table name
        self.table_name = "weather_db"
        self.initialize_db()


    def initialize_db(self):

        table = self.table_name

        with self.db_manager as cursor:

            # Check if table exists using a query on the sqlite_master table
            cursor.execute("""SELECT name FROM sqlite_master
                         WHERE type='table' AND name=?;""", (table,))
            
            # Use cursor to fetch one result from the executed query
            check_table_exists = cursor.fetchone()

            if check_table_exists:
                print(f"Table '{table}' already exists.")
            else:
                cursor.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {table}(
                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        sample_date TEXT NOT NULL,
                        location TEXT NOT NULL,
                        min_temp REAL NOT NULL,
                        max_temp REAL NOT NULL,
                        mean_temp REAL NOT NULL,
                        UNIQUE(sample_date, location));
                    """
                )
                cursor.connection.commit()

    def fetch_data(self, start_date: str, end_date: str, location: str, month: str = None):

        query = f"""
                SELECT * from {self.table_name}
                WHERE sample_date BETWEEN ? AND ?
                AND location = ?
                """
        
        params = [start_date, end_date, location]

        if month is not None:
            query += " AND strftime('%m', sample_date) = ?"
            params.append(month)


        query += " ORDER BY sample_date;"

        with self.db_manager as cursor:
            cursor.execute(query, params)

            # Tuple of rows returned from fetchall
            tuple_result = cursor.fetchall()
            print(tuple_result)
            return tuple_result

    def purge_data(self):
        with self.db_manager as cursor:
            cursor.execute("DELETE FROM weather_db;")

    def save_data(self, new_data):
        with self.db_manager as cursor:

            # Dictionary of dictionaries requires you to unpack key and value pairs
            for date_key, data_values in new_data.items():
                params = (date_key, 
                          data_values["Location"], 
                          data_values["Min"], 
                          data_values["Max"], 
                          data_values["Mean"]
                          )
                
                # INSERT OR IGNORE to avoid duplicates based on UNIQUE contraints between location and date
                cursor.execute(
                """
                INSERT OR IGNORE INTO weather_db
                (sample_date, location, min_temp, max_temp, mean_temp)
                VALUES (?, ?, ?, ?, ?)
                """, params
                )
    
    def execute_query(self, query, params=None):
        with self.db_manager as cursor:
            cursor.execute(query) if params is None else self.cursor.execute(query, params)
            cursor.conn.commit()
    
    # Operate on self, no class method.
        # Recall that WeatherProcessor creates an instance of DBOperations.
    def download_database(self):

        scraper = scrape.WeatherScraper()
        start_date = datetime.datetime(1996, 10, 1)
        end_date = datetime.datetime.now()
        new_data = scraper.scrape_weather(start_date, end_date)

        if new_data:
            print(f"Saving {len(new_data)} new records to the database...")
            self.save_data(new_data)

    def get_latest_date(self):

        # 1. Get latest date from database
        with self.db_manager as cursor:

            # Select the MAX date from table
            cursor.execute(
                f"""
                SELECT MAX(sample_date) FROM {self.table_name};
                """
            )
            # 2. Pull the first value from the fetched tuple
                # This is the latest date string
            latest_date = cursor.fetchone()[0]

            # if latest date is truthy and contains a value
            if latest_date and latest_date[0]:

                # Return a datetime object parsed from latest date string
                return datetime.strptime(latest_date[0], "%Y-%m-%d")
            
            # No data in database
            return None


        # 2. Add the missing dates to the database
        # with self.db_manager.cursor() as cursor:
        #     params = (date, data["Location"], data["Min"], data["Max"], data["Mean"])
        #     for date, data in missing_dates.items():
        #         cursor.execute(
        #             f"""INSERT INTO weather_db
        #             (sample_date, location, min_temp, max_temp, mean_temp)
        #             VALUES(?, ?, ?, ?, ?);""", params)

    

    
    def print_database(self, table_name: str):
        with self.db_manager as cursor:
            cursor.execute(f"SELECT * FROM {table_name};")
            tuple_rows = cursor.fetchall()
            for row in tuple_rows:
                print(row)


        
