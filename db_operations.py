import sqlite3 as sql
import scrape_weather as scrape
import dbcm
"""
Final Project - ADEV-3005
2025-10-29, Tanner Agar
db_operations.py - Database operations for weather data
"""



class DBOperations():

    # Input is a dictionary from WeatherScraper class: date, min temp, max temp, mean temp.

    def __init__(self, dbcm_instance=dbcm):
        self.dbcm = dbcm_instance


    def initialize_db(self):

        self.dbcm.table_name = "weather_db"

        with self.dbcm.cursor() as cursor:

            # Check if table exists using a query on the sqlite_master table
            cursor.execute("""SELECT name FROM sqlite_master
                         WHERE type='table' AND name=?;""", (dbcm.table_name,))
            
            # Use cursor to fetch one result from the executed query
            check_table_exists = cursor.fetchone()

            if check_table_exists:
                print(f"Table '{dbcm.table_name}' already exists.")
            else:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS weather_db(
                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        sample_date TEXT NOT NULL,
                        location TEXT NOT NULL,
                        min_temp REAL NOT NULL,
                        max_temp REAL NOT NULL,
                        mean_temp REAL NOT NULL,
                        UNIQUE(sample_date, location);
                        """
                )
                cursor.connection.commit()

    @classmethod
    def fetch_data(self, start_date: str, end_date: str, month : str, location: str):

        with dbcm.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM weather_db
                WHERE sample_date BETWEEN ? AND ?,
                AND strftime('%m', sample_date) = ?,
                AND location = ?;
                """,
                (start_date, end_date, month, location)
            )

            # Tuple of rows returned from fetchall
            tuple_result = cursor.fetchall()
            print(tuple_result)
            return tuple_result

    def purge_data(self):
        with dbcm.cursor() as cursor:
            cursor.execute("DELETE FROM weather_db;")

    def save_data(self):
        with dbcm.cursor() as cursor:
            # if data does not already exist insert
                # if 0 then the data does not exist
                # COUNT(*) is a function returning number of rows that match the query/criteria
            cursor.execute(
            """
            SELECT COUNT(*) FROM weather_db
            WHERE sample_date, location = ?, ?
            IF 0 THEN
                INSERT INTO weather_db (sample_date, location, min_temp, max_temp, mean_temp)
                VALUES (?, ?, ?, ?, ?)
            ON CONFLICT DO NOTHING;
            """
            )
            dbcm.conn.commit()
    
    def execute_query(self, query, params=None):
        with dbcm.cursor() as cursor:
            cursor.execute(query) if params is None else self.cursor.execute(query, params)
            cursor.conn.commit()
    
    @classmethod
    def download_database(cls, update=False):

        # Setup scraper and context for database
        scraper = scrape.WeatherScraper()

        weather_database = dbcm.table_name

        with weather_database as db:
            if (not update):
                # If not updating, initialize the database
                weather_database.initialize_db()

                # Scrape the full weather data set
                new_weather_data = scraper.scrape_weather_data()

                # Convert string representation of dictionary to actual dictionary
                    # eval is used to keep things simple
                new_weather_dict = dict(eval(new_weather_data))
            else:
                # If updating, get missing dates from the update database method
                update_weather_dict = weather_database.update_database()

                # Convert string representation of dict -> actual dictionary
                new_weather_dict = dict(eval(update_weather_dict))

                # Iterate over new weather data, and add it to the database
                for date, data in new_weather_dict.items():

                # Assign date as key and data as value in the dictionary
                    weather_dict[date] = data

                    # Iterate over the dictionary items and assign to params tuple
                    params = (date, data["location"], data["min_temp"], data["max_temp"], data["mean_temp"])

                    # Insert SQL using (?) placeholders and the params tuple to insert & prevent SQL injection
                    db.execute_query(
                        f"""INSERT INTO weather
                        (date, location, min_temp, max_temp, mean_temp)
                        values(?, ?, ?, ?, ?);""", params)
                    
                    # sqllite suffix is optional
                    db.print_database("weather_db")

    @classmethod
    def update_database():

        # 0. Get latest date from database
        with dbcm.cursor() as cursor:
            cursor.execute(
                """
                SELECT MAX(sample_date) FROM weather_db;
                """
            )
        # Latest date from database - MAX the date for latest possible date
        latest_date = cursor.fetchone()[0]

        # 1. Check if there are missing dates between latest date and today's date
        missing_dates = scraper.check_missing_dates(latest_date)
        return missing_dates

        # 2. Add the missing dates to the database
        # with dbcm.cursor() as cursor:
        #     params = (date, data["Location"], data["Min"], data["Max"], data["Mean"])
        #     for date, data in missing_dates.items():
        #         cursor.execute(
        #             f"""INSERT INTO weather_db
        #             (sample_date, location, min_temp, max_temp, mean_temp)
        #             VALUES(?, ?, ?, ?, ?);""", params)

    

    
    def print_database(self, table_name: str):
        with dbcm.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {table_name};")
            tuple_rows = cursor.fetchall()
            for row in tuple_rows:
                print(row)


if __name__ == "__main__":
    scraper = scrape.WeatherScraper()
    weather_data = scraper.scrape_weather_data()
    weather_database = DBOperations("weather_db.sqlite")
    with weather_database as db:
        weather_database.initialize_db()

        weather_dict = dict(eval(weather_data))


        

