from html.parser import HTMLParser
import selenium as se
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import colorama as ca
from datetime import datetime, timedelta
"""
Final Project - ADEV-3005
2025-10-29, Tanner Agar
scrape_weather.py - Parse weather data from Environment Canada
"""



"""
Scrape Winnipeg weather data from Environment Canada from current date to as far back in time as possible.
Automatically detect when no more weather data is available for scraping. No hardcoded date for last available date.
No fetching of the last date from any drop down menus.


"""



class WeatherScraper():

    """
    Input: The starting URL to scrape, encoded with today's date.
    """    
    def scrape_weather(self, start_date: datetime, end_date: datetime,):

        # Setup driver for Selenium
        driver = se.webdriver.Chrome()

        # Weather dictionary, dictionary of dictionaries
        daily_temps = {"Max" : str, "Min" : str, "Mean" : str}
        weather_data = {}

        # Current date for while loop, replace day to 1 to iterate over months.
        current_date = start_date.replace(day=1)


        try:
            while current_date <= end_date:
                print(f"While loop current date: {current_date}")
                year = current_date.year
                month = current_date.month

                print(f"Scraping year: {year}-{month:02d}")
                url = f"https://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID=27174&timeframe=2&StartYear={year}&EndYear={year}&Day=1&Year={year}&Month={month:02d}"
                print(f"URL: {url}")
                driver.get(url)

                try:
                    table = WebDriverWait(driver, 4).until(
                        EC.presence_of_element_located((By.ID, "dynamicDataTable"))
                    )

                    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
                    print(f"Rows found: {len(rows)}")

                except se.common.exceptions.TimeoutException as e:
                    print(f"Time while waiting for table to load: {e}")
                    next_month = current_date + timedelta(days=32)
                    current_date = next_month.replace(day=1)

                try:
                    location_element = driver.find_element(By.CLASS_NAME, "table-header").text
                    location = location_element.split("\n")[0]
                except se.common.exceptions.NoSuchElementException as e:
                    print(f"Location element not found: {e}")
                    location = "Unknown Location"
                

                for row in rows:
                    try:


                        # Find all abbr tags with title attribute, this selector contains the days
                        day = row.find_element(By.CSS_SELECTOR, "th a[href]").text

                        if day is None or day.strip() == "":
                            continue

                        row_date_str = f"{year}-{month:02d}-{int(day):02d}"
                        row_date_object = datetime.strptime(row_date_str, "%Y-%m-%d")

                        # Skip dates outside the requested range
                        if row_date_object < start_date or row_date_object > end_date:
                            continue

                        # Find the first three td elements in the table within the dynamicDataTable id, these contain the required Max, Min, Mean temperatures.
                        temps = row.find_elements(By.TAG_NAME, "td")
                        if len(temps) >= 3:
                            # Helper to clean the value
                            def clean_temp(temps):
                                try:
                                    return float(temps)
                                except ValueError:
                                    return None
                            max_temp = clean_temp(temps[0].text)
                            min_temp = clean_temp(temps[1].text)
                            mean_temp = clean_temp(temps[2].text)
                            
                            if max_temp is not None or min_temp is not None or mean_temp is not None:
                                daily_temps = {
                                    "Location": location,
                                    "Max" : max_temp,
                                    "Min" : min_temp,
                                    "Mean" : mean_temp
                                }

                                # Store the location and daily temps in the weather data dictionary
                                weather_data[row_date_str] = daily_temps

                    except se.common.exceptions.NoSuchElementException as e:
                        continue

                # Move to next month to trigger the while loop condition
                next_month = current_date + timedelta(days=32)
                current_date = next_month.replace(day=1)
            
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            driver.quit()
        return weather_data