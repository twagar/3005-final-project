import colorama as ca
import menu as menu
import scrape_weather as scrape
import plot_operations as plot_ops
import db_operations as db_ops


"""
Final Project - ADEV-3005
2025-10-29, Tanner Agar
weather_processor.py - Menu to launch and manage weather data processing and tasks
"""






class WeatherProcessor():


    ca.just_fix_windows_console()

    def __init__(self):
        self.db_op = db_ops.DBOperations()


    
    def build_main_menu(self):
        main_options = []

        main_options.append(("Download/Update Weather Data", self.select_download)) # After select decide between download or update.
        main_options.append(("Box Plot", self.select_box_plot)) # After select enter year range of interest, two values.
        main_options.append(("Line Plot", self.select_line_plot)) # After select enter a year and a month
        main_options.append(("Exit", menu.Menu.CLOSE))

        return main_options

    def setup_main_menu(self):
        main_menu = menu.Menu(title="Weather Data Processor: Main Menu", options = self.build_main_menu(), prompt=">", auto_clear=False)
        main_menu.open()


    # Option 1. Main Menu -> Download/Update Weather Data
    def select_download(self):
        download_options = []

        download_options.append(("Download data set from the beginning", db_ops.download_database()))

        # Param: @update 
        download_options.append(("Update existing data set", db_ops.download_database(update=True)))

        download_options.append(("Back to Main Menu", menu.Menu.CLOSE))

        return download_options
    
    def update_download_menu(self):
        download_menu = menu.Menu("Download or Update Weather Data", options = self.select_download(), prompt = ">", auto_clear=False)
        download_menu.open()
    



    def strike(text: str) -> str:
        STRIKE = "\x1b[9m"
        RESET = "\x1b[0m"
        return f"{STRIKE}{text}{RESET}"


    def select_box_plot(self):
        # User Input:
        start_year = input("Enter ranges: start year range to plot: ")
        end_year = input("Enter ranges: end year to plot: ")

        # Input: fetch data from database based on year range for all months
        data = self.db_op.fetch_data(start_year, end_year, month="12", location="WINNIPEG A CS")



        # 1. Processing: Create a dictionary to hold month as key, value list of mean temps
            # K: month
            # V: list of mean temps per month for a year
        plot_data = {}
        for row in data:
            # A row is a tuple which represents a record from database
            month = row[1].split("-")[1]
            location = row[2]
            min_temp = row[3]
            max_temp = row[4]
            mean_temp = row[5]

            temperatures = {
                "min": min_temp,
                "max": max_temp,
                "mean": mean_temp
            }
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
        month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "July"]

        # instantiate plot operations 
        plot = plot_ops.PlotOperations()
    
        # call box plot method with plot data sent to a list of values from dict
        plot.box_plot(list_plot_data, month_labels, start_year, end_year)


    def select_line_plot(self):
        line_options = []
        line_options.append("Select year and a month", None)
        return line_options


    # 1. Download a full set of weather data/update existing data
        # On update check today's date against latest date of weather available in database
        # If missing data between dates, download what's missing between these two dates/points
        # No duplicating data


    # 2. 


if __name__ == "__main__":
    wp = WeatherProcessor()
    wp.setup_main_menu()