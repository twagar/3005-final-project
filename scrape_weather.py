"""
Final Project - ADEV-3005
2025-10-29, Tanner Agar
scrape_weather.py - Parse weather data from Environment Canada
"""
import datetime
import logging as log
import selenium as se
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WeatherScraper():
    """
    Class that contains methods to scrape weather data from Environment Canada.
    Scrape Winnipeg weather data from Environment Canada from current date to as far back
    in time as possible. Automatically detect when no more weather data is available for scraping.
    No hardcoded date for last available date. No fetching of the last date from any drop down menus.
    """

    # Logger for the class
    logger = log.getLogger(__name__)

    def scrape_weather(self, start_date: datetime, end_date: datetime):
        """
        Scrape weather that takes in a start date and end date as datetime objects.
        Returns a dictionary with a key value pair of date string and another dictionary of
        max, min, mean temperatures.
        """
        # Setup driver for Selenium
        driver = se.webdriver.Chrome()

        # Weather dictionary, dictionary of dictionaries
        weather_data = {}

        # Current date for while loop, replace day to 1 to iterate over months.
        current_date = start_date.replace(day=1)

        try:
            # While loop to iterate over months start to end date
            # Break when current date exceeds end date
            while current_date <= end_date:
                print(f"While loop current date: {current_date}")
                year = current_date.year
                month = current_date.month

                print(f"Scraping year: {year}-{month:02d}")
                url = (
                    f"https://climate.weather.gc.ca/climate_data/daily_data_e.html?"
                    f"StationID=27174&timeframe=2&StartYear={year}&EndYear={year}"
                    f"&Day=1&Year={year}&Month={month:02d}"
                )
                print(f"URL: {url}")

                driver.get(url)

                try:
                    # Wait until there is presence of the data table
                    table = WebDriverWait(driver, 4).until(
                        EC.presence_of_element_located((By.ID, "dynamicDataTable"))
                    )

                    # find collection of rows for a loop in table body by css selector
                    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
                    print(f"Rows found: {len(rows)}")

                # if table not found/time out, move to the next month
                except se.common.exceptions.TimeoutException as e:
                    print(f"Time while waiting for table to load: {e}")
                    next_month = current_date + datetime.timedelta(days=32)
                    current_date = next_month.replace(day=1)
                    log.warning("No data table found for %s-%02d, moving to next month.", year, month)
                    continue # Skip the rest of the loop

                try:
                    location_element = driver.find_element(By.CLASS_NAME, "table-header").text
                    location = location_element.split("\n")[0]
                except se.common.exceptions.NoSuchElementException as e:
                    # set location to unknown in rare case/website bug of not existing location element
                    print(f"Location element not found: {e}")
                    location = "Unknown Location"
                    log.warning("Location not found for %s-%02d, setting as Unknown Location.", year, month)

                # Iterate over each row in the table and extract date and temp data
                for row in rows:
                    try:
                        # Find all abbr tags with title attribute, this selector contains the days
                        day = row.find_element(By.CSS_SELECTOR, "th a[href]").text

                        # Skip rows with no day value
                        # continue to next row
                        if day is None or day.strip() == "":
                            log.info("No day found in row, skipping row.")
                            continue

                        # Construct full date string for comitting to database
                        row_date_str = f"{year}-{month:02d}-{int(day):02d}"

                        # Date object required for range checking/logic
                        row_date_object = datetime.datetime.strptime(row_date_str, "%Y-%m-%d")

                        # Skip dates outside the requested range
                        if row_date_object < start_date or row_date_object > end_date:
                            log.info("Date %s outside requested range, skipping.", row_date_str)
                            continue

                        # Find the first three td elements in the table within the dynamicDataTable id
                        temps = row.find_elements(By.TAG_NAME, "td")
                        if len(temps) >= 3:
                            # Helper to clean the value
                            def clean_temp(val):
                                try:
                                    return float(val)
                                except ValueError:
                                    return None

                            max_temp = clean_temp(temps[0].text)
                            min_temp = clean_temp(temps[1].text)
                            mean_temp = clean_temp(temps[2].text)

                            # Check if at least one temp value exists before store
                            if max_temp is not None or min_temp is not None or mean_temp is not None:
                                daily_temps = {
                                    "Location": location,
                                    "Max": max_temp,
                                    "Min": min_temp,
                                    "Mean": mean_temp
                                }

                                # Store the location and daily temps in the weather data dictionary
                                weather_data[row_date_str] = daily_temps
                                log.info("Completed pass for date: %s, data: %s", row_date_str, daily_temps)

                    # skip execution if no day element found in row
                    except se.common.exceptions.NoSuchElementException:
                        continue

                # Move to next month to trigger the while loop condition
                next_month = current_date + datetime.timedelta(days=32)
                current_date = next_month.replace(day=1)
                log.info("Completed scraping for %s-%02d, moving to next month.", year, month)

        except Exception as e:
            print(f"An error occurred: {e}")
            log.error("An error occurred during scraping: %s", e)
        finally:
            log.info("Closing the web driver.")
            driver.quit()
        return weather_data