import matplotlib.pyplot as plt
import db_operations as db_ops


"""
Final Project - ADEV-3005
2025-10-29, Tanner Agar
plot_operations.py - Plot operations using matplotlib for weather data
"""


class PlotOperations():

    # Input is a dictionary of lists from DBOperations fetch_data method.
        # Dictionary key is the month
        # Data is all the mean temperatures for each day of that month for years (box plot) or a specific year (line plot).


    def box_plot(self, data, labels, start_year: int, end_year: int):
        plt.title(f'Box Plot of Daily Average Temperatures between {start_year} and {end_year}')
        plt.xlabel('Months')
        plt.ylabel('Average Daily Temperatures (°C)')   
        plt.boxplot(data)
        plt.show()




    def line_plot(self, data, year: int, month: int):
        plt.xlabel(f"Day")
        plt.ylabel(f"Average Daily Temperature (°C) for {month}/{year}")
        

