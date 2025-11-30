"""
Final Project - ADEV-3005
2025-10-29, Tanner Agar
db_operations.py - Database operations for weather data
"""
import logging as log
import datetime
import sqlite3 as sql
import scrape_weather as scrape
import dbcm



class DBOperations():
    """
    Class: handles database operations for weather data
    Initalization, saving, purging, and fetching of data
    """

    # Logger for the class
    logger = log.getLogger(__name__)

    def __init__(self, db_name):
        """
        Construct the DBOperations instance:
        Setup the db_manager dbcm instance, scraper instance, and table name.
        Initialize the database, creating the table if it does not already exist.
        """

        # db link
        self.db_manager = dbcm.DBCM(db_name)

        # scraper
        self.scraper = scrape.WeatherScraper()

        # table name
        self.table_name = "weather_db"

        # instantiate the db if not exists
        self.initialize_db()



    def initialize_db(self):
        """
        Initialize the database by creating the weather_db table if it does not exist.
        """
        table = self.table_name

        try:
            with self.db_manager as cursor:
                # Check if table exists using a query on the sqlite_master table
                cursor.execute("""SELECT name FROM sqlite_master
                            WHERE type='table' AND name=?;""", (table,))
                # Use cursor to fetch one result from the executed query
                check_table_exists = cursor.fetchone()

                if check_table_exists:
                    print(f"Table '{table}' already exists.")
                    log.info("Table '%s' already exists in database.", table)
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
                    log.info("Table '%s' created in database.", table)
        except Exception as e:
            print(f"Error initalizing database: {e}")
            log.error("Error initalizing database: %s", e)

    def fetch_data(self, start_date: str, end_date: str, location: str, month: str = None):
        """
        Fetches data by building a query with optional month parameter.
        Returns a tuple of rows from the database matching the query.
        """
        try:
            # Base query
            query = f"""
                    SELECT * from {self.table_name}
                    WHERE sample_date BETWEEN ? AND ?
                    AND location = ?
                    """
            # Parameters list
            params = [start_date, end_date, location]

            # Optional month provided? Append to base query and append to parameters list
            if month is not None:
                query += " AND strftime('%m', sample_date) = ?"
                params.append(month)

            # Append clause to order by sample_date
            query += " ORDER BY sample_date;"

            with self.db_manager as cursor:
                # Execute the query with parameters
                cursor.execute(query, params)

                # Tuple of rows returned from fetchall
                tuple_result = cursor.fetchall()
                print(tuple_result)
                log.info("Fetched %s records from database.", len(tuple_result))
                return tuple_result
        except Exception as e:
            print(f"Error fetching data from database: {e}")
            log.error("Error fetching data from database: %s", e)
            return None

    def purge_data(self):
        """
        Purge all the data, does not drop the table itself.
        """
        try:
            with self.db_manager as cursor:
                cursor.execute(f"DELETE FROM {self.table_name};")
                log.info("Purged all data from %s database.", self.table_name)
                print(f"All data purged from {self.table_name} database.")
        except Exception as e:
            print(f"Error purging data from database: {e}")
            log.error("Error purging data from database: %s", e)

    def save_data(self, new_data):
        """
        Save new data to the database from a dictionary of dictionaries.
        The outer dictionary key is the date string, the values are the inner dictionary with keys:
        Location, Min, Max, Mean.
        Invoked in WeatherProcessor update_database method, after scraping new data which returns
        a dictionary of dictionaries.
        """
        try:
            with self.db_manager as cursor:

                # Dictionary of dictionaries requires you to unpack key and value pairs
                    # For outer dictionary: date_key
                    # For inner dictionary: data_values
                    # within the items of new_data
                for date_key, data_values in new_data.items():
                    # Assign shape to params for insert statement
                    params = (date_key,
                        data_values["Location"],
                        data_values["Min"],
                        data_values["Max"],
                        data_values["Mean"]
                    )
                    # INSERT OR IGNORE
                    # prevent duplicates based on UNIQUE contraints between location and date
                    cursor.execute(
                    """
                    INSERT OR IGNORE INTO weather_db
                    (sample_date, location, min_temp, max_temp, mean_temp)
                    VALUES (?, ?, ?, ?, ?)
                    """, params
                    )
            log.info("Saved %s new records to the database.", len(new_data))
        except Exception as e:
            print(f"Error saving data to database: {e}")
            log.error("Error saving data to database: %s", e)
    
    def execute_query(self, query, params=None):
        """
        Execute a query with optional parameters.
        """
        try:
            with self.db_manager as cursor:
                if params is None:
                    cursor.execute(query)
                else:
                    cursor.execute(query, params)
                cursor.connection.commit()
        except Exception as e:
            print(f"Error executing query: {e}")
            log.error("Error executing query: %s", e)

    def download_database(self):
        """
        Download the database from the very start date to the current date using the
        WeatherScraper class method scrape_weather.
        """
        try:
            # Initialize the scraper
                # assign start and end date arguments using datetime objects
                # assign new data to the returned dict from scrape_weather method
            scraper = scrape.WeatherScraper()
            start_date = datetime.datetime(2020, 1, 1)
            end_date = datetime.datetime.now()
            new_data = scraper.scrape_weather(start_date, end_date)

            if new_data:
                print(f"Saving {len(new_data)} new records to the database...")
                self.save_data(new_data)
                log.info("Downloaded database from %s to %s.", start_date, end_date)
        except Exception as e:
            print(f"Error downloading database: {e}")
            log.error("Error downloading database: %s", e)

    def get_latest_date(self):
        """
        Get the latest date from the database as a datetime object, to be able to update
        the database.
        """
        try:
            with self.db_manager as cursor:

                # Select the MAX date from table
                cursor.execute(
                    f"""
                    SELECT MAX(sample_date) FROM {self.table_name};
                    """
                )
                # 2. Pull the first value from the fetched tuple
                    # this is the latest date string
                latest_date = cursor.fetchone()

                # if latest date is truthy and contains a value
                if latest_date:

                    # Return a datetime object parsed from latest date string; a tuple's first element
                    log.info("Returning the latest date as %s.", latest_date)
                    return datetime.datetime.strptime(latest_date[0], "%Y-%m-%d")


                # No data in database
                log.info("No data found in database, returning None.")
                return None

        except Exception as e:
            print(f"Error getting latest date from database: {e}")
            log.error("Error getting latest date from database: %s", e)
            return None

    def print_database(self, table_name: str):
        """
        Helper method to print all rows in database table for debugging.
        """
        try:
            with self.db_manager as cursor:
                cursor.execute(f"SELECT * FROM {table_name};")
                tuple_rows = cursor.fetchall()
                for row in tuple_rows:
                    print(row)
        except Exception as e:
            print(f"Error printing database: {e}")
            log.error("Error printing database: %s", e)


        
