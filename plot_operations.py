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
        plt.xticks(range(1, len(labels) + 1), labels) # For each tick use the label from the labels list
        plt.show()


    def line_plot(self, data, labels, year: int, month: int):
        plt.title(f"Line Plot of Daily Average Temperatures for {month}/{year}")
        plt.xlabel(f"Days")
        plt.ylabel(f"Average Daily Temperature (°C) for {month}/{year}")
        plt.plot(range(1, len(data) + 1), data, marker='o')

        # Set x-ticks: font size = 12, rotate 45 degrees
        plt.xticks(range(1, len(labels) + 1), labels, rotation=45, fontsize=5, ha='right')
        # subplot param for padding 0.133 bottom
        plt.subplots_adjust(bottom=0.133)
        plt.grid(True)
        plt.show()
        

