"""
Final Project - ADEV-3005
2025-10-29, Tanner Agar
plot_operations.py - Plot operations using matplotlib for weather data
"""
import logging as log
import matplotlib.pyplot as plt


class PlotOperations():
    """
    Class containing methods for plot operations of weather data using matplotlib.
    """

    # Logger for the class
    logger = log.getLogger(__name__)

    def box_plot(self, data, labels, start_year: int, end_year: int):
        """
        Create a box plot give the passed data, labels, start year and end year.
        """
        try:
            plt.title(f'Box Plot of Daily Average Temperatures between {start_year} and {end_year}')
            plt.xlabel('Months')
            plt.ylabel('Average Daily Temperatures (°C)')

            # create box plot
            plt.boxplot(data)

            # for each tick use the label from the passed labels list
            plt.xticks(range(1, len(labels) + 1), labels)

            log.info("Generated box plot for years %s to %s.", start_year, end_year)

            plt.show()
        except Exception as e:
            print(f"Error generating box plot: {e}")
            log.error("Error generating box plot: %s", e)

    def line_plot(self, data, labels, year: int, month: int):
        """
        Create a line plot given the passed data, labels, year and month.
        """
        try:
            plt.title(f"Line Plot of Daily Average Temperatures for {month}/{year}")
            plt.xlabel("Days")
            plt.ylabel(f"Average Daily Temperature (°C) for {month}/{year}")

            # plot with markers for each data point
            plt.plot(range(1, len(data) + 1), data, marker='o')

            # set x-ticks: font size = 5, rotate 45 degrees, ha='right' to align labels
            plt.xticks(range(1, len(labels) + 1), labels, rotation=45, fontsize=5, ha='right')

            # subplot param for padding 0.133 bottom
            plt.subplots_adjust(bottom=0.133)

            # grid enable for legiblility
            plt.grid(True)

            log.info("Generated line plot for %s/%s.", month, year)

            plt.show()
        except Exception as e:
            print(f"Error generating line plot: {e}")
            log.error("Error generating line plot: %s", e)
            

