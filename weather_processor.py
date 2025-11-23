import colorama as ca
import menu as menu
import scrape_weather as scrape
import plot_operations as plot_ops
import db_operations as db_ops
import datetime as datetime

"""
Final Project - ADEV-3005
2025-10-29, Tanner Agar
weather_processor.py - Menu to launch and manage weather data processing and tasks
"""






class WeatherProcessor():

    """
    Using menu module, do not instantiate methods with () when passing as options to a menu.
    Without the parentheses, the function will only run when selected in the menu, as opposed to the building of the menu where it would run immediately.
    """

    def __init__(self):
        # inject an instance of DBOperations on start
            # Therefore non-decorated instance methods will be used.
        self.db_op = db_ops.DBOperations("weather.sqlite")


    ca.just_fix_windows_console()

    
    # 1.1 Build main menu options
    def build_main_menu(self):
        main_options = []

        main_options.append(("Download/Update Weather Data", self.setup_download_menu)) # After select decide between download or update.
        main_options.append(("Box Plot", self.select_box_plot)) # After select enter year range of interest, two values.
        main_options.append(("Line Plot", self.select_line_plot)) # After select enter a year and a month
        main_options.append(("Exit", menu.Menu.CLOSE))

        return main_options
    
    # 1. Setup the main menu
    def setup_main_menu(self):
        main_menu = menu.Menu(title="Weather Data Processor: Main Menu", options = self.build_main_menu(), prompt=">", auto_clear=False)
        main_menu.open()


    # 2. build the Download/Update menu
    def build_download_menu(self):
        download_options = []

        download_options.append(("Download data set from the beginning", self.db_op.download_database))

        # Param: @update 
        download_options.append(("Update existing data set", self.update_database))

        download_options.append(("Back to Main Menu", menu.Menu.CLOSE))

        return download_options
    
    def setup_download_menu(self):
        download_menu = menu.Menu(title="Download or Update Weather Data", options = self.build_download_menu(), prompt = ">", auto_clear=False)
        download_menu.open()

    def update_database(self):
        print("Getting latest date...")
        latest_date = self.db_op.get_latest_date()
        print("Latest date is: ", latest_date)
        recent_date = datetime.datetime.now()
        print("Today's date is: ", recent_date)

        scraper = scrape.WeatherScraper()

        update = scraper.scrape_weather(latest_date, recent_date)

        if update:
            print(f"Saving {len(update)} new records to the database.")
            self.db_op.save_data(update)
        


    def strike(text: str) -> str:
        STRIKE = "\x1b[9m"
        RESET = "\x1b[0m"
        return f"{STRIKE}{text}{RESET}"


    def select_box_plot(self):
        # User Input:
        start_year = input("Enter ranges: start year range to plot: ")
        end_year = input("Enter ranges: end year to plot: ")

        beginning_date = f"{start_year}-01-01"
        ending_date = f"{end_year}-12-31"

        data = self.db_op.fetch_data(beginning_date, ending_date, location="WINNIPEG A CS")
        print(f"Data fetched for box plot: {data}")

        # 1. Processing: Create a list of dictionaries to hold month as key, value list of mean temps
            # K: month
            # V: list of mean temps per month for a year
        plot_data = {}
        for row in data:
            # A row is a tuple which represents a record from database
            month = int(row[1].split("-")[1])
            location = row[2]
            min_temp = row[3]
            max_temp = row[4]
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
    
        # call box plot method with plot data sent to a list of values from dict
        plot.box_plot(list_plot_data, month_labels, start_year, end_year)

    def select_line_plot(self):

        # User Input:
        year = input("Enter a chosen year (YYYY): ") 

        # Force MM input by user by prompting until valid input is given
        month = input("Enter a chosen month (MM): ").zfill(2)

        fetch_data = self.db_op.fetch_data(f"{year}-{month}-01", f"{year}-{month}-31", location="WINNIPEG A CS")
        print(f"Data fetched for line plot: {fetch_data}")

        plot_data = {}
        for row in fetch_data:
            # A row is a tuple which represents a record from database
            month = row[1].split("-")[1]
            day = row[1].split("-")[2]
            location = row[2]
            min_temp = row[3]
            max_temp = row[4]
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
        plot.line_plot(list_plot_data, labels, year, month)





    # 1. Download a full set of weather data/update existing data
        # On update check today's date against latest date of weather available in database
        # If missing data between dates, download what's missing between these two dates/points
        # No duplicating data


    # 2. 


if __name__ == "__main__":
    wp = WeatherProcessor()
    wp.setup_main_menu()