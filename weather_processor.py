"""
Final Project - ADEV-3005
2025-10-29, Tanner Agar
weather_processor.py - Menu to launch and manage weather data processing and tasks
"""
import datetime
import logging as log
import menu
import scrape_weather as scrape
import plot_operations as plot_ops
import db_operations as db_ops


class WeatherProcessor():
    """
    Inject an instance of DBOperations on start, therefore non-decorated instance methods will be used.
    """
    def __init__(self):
        self.db_op = db_ops.DBOperations("weather.sqlite")

    def build_main_menu(self):
        """
        Build the main menu options.
        """
        try:
            main_options = []

            # After select decide between download or update.
            main_options.append(("Download/Update/Purge Weather Data", self.setup_download_menu))
            # After select enter year range of interest, two values.
            main_options.append(("Box Plot", self.select_box_plot))
            # After select enter a year and a month
            main_options.append(("Line Plot", self.select_line_plot))
            main_options.append(("Exit", menu.Menu.CLOSE))

            return main_options
        except Exception as e:
            print(f"Error building main menu: {e}")
            log.error("Error building main menu: %s", e)
            return []

    def setup_main_menu(self):
        """
        Setup and open the main menu.
        """
        try:
            main_menu = menu.Menu(
                title="Weather Data Processor: Main Menu",
                options=self.build_main_menu(),
                prompt=">",
                auto_clear=False
            )
            main_menu.open()
        except Exception as e:
            print(f"Error setting up main menu: {e}")
            log.error("Error setting up main menu: %s", e)

    def build_download_menu(self):
        """
        Build the download/update menu options.
        """
        try:
            # Store download options
            download_options = []

            # Append options for download menu
            download_options.append(("Download data set from the beginning", self.db_op.download_database))
            download_options.append(("Update existing data set", self.update_database))
            download_options.append(("Purge the database (delete all records)", self.db_op.purge_data))
            download_options.append(("Back to Main Menu", menu.Menu.CLOSE))

            return download_options
        except Exception as e:
            print(f"Error building download menu: {e}")
            log.error("Error building download menu: %s", e)
            return []

    def setup_download_menu(self):
        """
        Setup and open the download/update menu.
        """
        try:
            # Header title & build download menu
            download_menu = menu.Menu(
                title="Download or Update Weather Data",
                options=self.build_download_menu(),
                prompt=">",
                auto_clear=False
            )

            # Open the download menu
            download_menu.open()

        except Exception as e:
            print(f"Error setting up download menu: {e}")
            log.error("Error setting up download menu: %s", e)

    def update_database(self):
        """
        Update the database with latest weather data.
        """
        try:
            log.info("Updating database with latest weather data...")

            # Call the database operations to get latest date
            # assign recent datetime object from now call
            latest_date = self.db_op.get_latest_date()
            log.info("Latest date is: %s", latest_date)
            recent_date = datetime.datetime.now()
            log.info("Today's date is: %s", recent_date)

            scraper = scrape.WeatherScraper()

            log.info("Scraping weather data from %s to %s...", latest_date, recent_date)

            # Pass the datetime objects to scraper and receive new data dict
            update = scraper.scrape_weather(latest_date, recent_date)

            if update:
                log.info("Saving %s new records to the database.", len(update))

                # Save data unpacks the dictionary and commits to the database
                self.db_op.save_data(update)

        except Exception as e:
            log.error("Error updating database: %s", e)

    def select_box_plot(self):
        """
        Render a box plot for input year range.
        """
        try:
            # User Input:
                # start year must be four digits
                # end year must be four digits
                # While loops to enforce valid input
                # Single line syntax for While loop and inline if to print error message if invalid input
            while not (start_year := input("Enter ranges: start year range to plot: ")).isdigit() or len(start_year) != 4: print("Invalid input. Please enter a 4-digit year.")
            while not (end_year := input("Enter ranges: end year to plot: ")).isdigit() or len(end_year) != 4: print("Invalid input. Please enter a 4-digit year.")
            log.info(f"User input for box plot: start year {start_year}, end year {end_year}.")

            beginning_date = f"{start_year}-01-01"
            ending_date = f"{end_year}-12-31"

            data = self.db_op.fetch_data(beginning_date, ending_date, location="WINNIPEG A CS")

            if not data:
                raise ValueError(f"No weather data found between for {start_year} and {end_year}.")
            # 1. Processing: Create a list of dictionaries to hold month as key, value list of mean temps
                # K: month
                # V: list of mean temps per month for a year
            plot_data = {}
            for row in data:
                # A row is a tuple which represents a record from database
                month = int(row[1].split("-")[1])
                mean_temp = row[5]
                if month not in plot_data:
                    # Create empty list for month if it doesn't exist
                    plot_data[month] = []
                # Append mean temp to the list for that month
                plot_data[month].append(mean_temp)

            # Return keys for month labels sorted by ASC
            sorted_months = sorted(plot_data.keys())

            # 2. Processing: Conversion to plot data: a list of lists for box plot to accept the input
                # If no conversion here to list, then there is no guarantee the order of the months/data
            list_plot_data = [plot_data[month] for month in sorted_months]

            # Assign month labels (otherwise just numbers)
            month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "July", "Aug", "Sept", "Oct", "Nov", "Dec"]

            # instantiate plot operations
            plot = plot_ops.PlotOperations()
            log.info("Calling box plot method...")
            # call box plot method with plot data sent to a list of values from dict
            plot.box_plot(list_plot_data, month_labels, start_year, end_year)
        except Exception as e:
            print(f"Error generating box plot: {e}")
            log.error("Error generating box plot: %s", e)

    def select_line_plot(self):
        """
        Render a line plot for input year and month.
        """
        try:
            # User Input:
            while True:
                year = input("Enter ranges: start year range to plot: ")
                if year.isdigit() and len(year) == 4:
                    break
                print("Invalid input. Please enter a 4-digit year.")

            # Force MM input by user by prompting until valid input is given
            while True:
                month = input("Enter a chosen month (MM): ")
                if month.isdigit() and len(month) == 2:
                    break
                print("Invalid input. Please enter a 2-digit month.")

            log.info("User input for box plot: start year %s, month %s.", year, month)

            fetch_data = self.db_op.fetch_data(f"{year}-{month}-01", f"{year}-{month}-31", location="WINNIPEG A CS")

            if not fetch_data:
                raise ValueError(f"No weather data found between for {year} and {month}.")

            plot_data = {}
            for row in fetch_data:

                # A row is a tuple which represents a record from database
                month = row[1].split("-")[1]
                day = row[1].split("-")[2]
                mean_temp = row[5]
                if day not in plot_data:
                    # Create empty list for day if it doesn't exist
                    plot_data[day] = []
                # Append mean temp to the list for that day
                plot_data[day].append(mean_temp)

                labels = [int(day) for day in plot_data.keys()]
            # Return keys for month labels sorted by ASC
            sorted_days = sorted(plot_data.keys())

            # 2. Processing: Conversion to plot data: a list of lists for box plot to accept the input
            # If no conversion here to list, then there is no guarantee the order of the months/data
            list_plot_data = [plot_data[day] for day in sorted_days]

            # Labels in the format year-month-day for each day
            labels = [f"{year}-{month}-{day}" for day in sorted_days]

            # instantiate plot operations
            plot = plot_ops.PlotOperations()

            # call line plot method with plot data sent to a list of values from dict
            log.info("Calling line plot method...")
            plot.line_plot(list_plot_data, labels, year, month)
        except Exception as e:
            print(f"Error generating line plot: {e}")
            log.error("Error generating line plot: %s", e)


if __name__ == "__main__":

    # Singleton logging configuration
        # Singleton offers a single point of config for logging across an entire application.
        # i.e. each call as `log.info(...)` uses this config.
    log.basicConfig(
        filename='weather_app.log',
        level=(log.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    wp = WeatherProcessor()
    wp.setup_main_menu()