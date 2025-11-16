from html.parser import HTMLParser
import selenium as se
from selenium.webdriver.common.by import By
import colorama as ca
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



class WeatherScraper(HTMLParser):

    def __init__(self):
        super().__init__()
        self.parser = HTMLParser()

        # Initialize a dictionary of dictionaries, i.e. daily_temps 
        # self.day = {}
        # self.daily_temps = {}
        # self._in_table = False
        # self._collect_temp = False
        # self._collect_day = False
    
    def handle_starttag(self, tag, attrs):
        # # print(f"Start tag: {tag}")
        # if tag == "abbr":
        #     print(f"abbr {ca.Fore.RED}{tag}")
        # print(f"Attributes: {attrs}")
        # attr_map = dict(attrs)

        # # Get the table with id dynamicDataTable
        # data_table = attr_map.get("id", "dynamicDataTable")
        # # self._in_table = True


        # # Select for rows in the data_table get call
        # rows = attr_map.get("element","tr").split()

        # # Select for a day in rows where title attribute contained within rows is day
        
        # print(f"Days: {data_table}")
        
        # # Get the first three td in tr
        # temps = attr_map.get("element", "td").split()
        # # temps = temps[:3]
        # print(f"Temps: {temps}")

        
        # if any()

        self._collect_temp = True
        self._collect_day = True

    def handle_endtag(self, tag):
        # print(f"End tag: {tag}")
        if tag == "abbr":
            print(f"end abbr {tag}")

        # self._collect_temp = False
        # self._collect_day = False

    def handle_data(self, data):
        print(f"Data: {data}")

        # If handle starttag completed, collect temperature and condition
        # if self._collect_temp and self._collect_condition is True:
        #     # 
        #     self.day['day'] = data.strip()
        #     self._collect_day = False
        #     self.daily_temps['temperature'] = data.strip()
        #     self._collect_temp = False



    """
    Input: The starting URL to scrape, encoded with today's date.
    """    
    def scrape_weather(self, url, start_year : str, end_year : str, start_month : str):



        # Setup driver for Selenium
        driver = se.webdriver.Chrome()


        # Scrape a speific range of years from start_year to end_year / input by WeatherProcessor
        date_range = [start_year, end_year]

        # Weather dictionary, dictionary of dictionaries
        daily_temps = {"Max" : str, "Min" : str, "Mean" : str}
        weather_data = {}
        MONTHS = "12"



        # Loop over start year to end year, scrape the data for each year.
            # Scrape the year and month specified in the URL
            # From start month to December, the scraper will scrape each month of the year specified.
        for year in range (int(date_range[0]), int(date_range[1])):

            # Month start from input if first year else set to January because the first year is done
            month_start = int(start_month) if year == int(start_year) else 1

            # Loop over months from start to December
            for month in range (month_start, int(MONTHS) + 1):

                print(f"Scraping year: {year}, month: {month}")
                url = f"https://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID=27174&timeframe=2&StartYear={year}&EndYear={year}&Day=1&Year={year}&Month={month:02d}"
                print(f"URLs: {url}")
                driver.get(url)
                html_page = driver.page_source
                parser = self.parser
                parser.feed(html_page)
                
                # When no more data is available, break from the loop.
                # if "Your request could not be completed because an error was found." in driver.page_source or  'https://climate.weather.gc.ca/historical_data/search_historic_data_e.html' in driver.current_url:
                #     print("No more data available to scrape.")
                #     break

                # Find all rows contained in the dynamicTableData ID
                location_element = driver.find_element(By.CLASS_NAME, "table-header").text
                location = location_element.split("\n")[0]
                rows = driver.find_elements(By.XPATH, "/html/body/main/div/div[5]/table/tbody/tr")
                print(f"Rows found: {len(rows)}")

                for row in rows:
                    try:

                        # Find all abbr tags with title attribute, this selector contains the days
                        day = row.find_element(By.CSS_SELECTOR, "th a[href]").text

                    
                        # Find the first three td elements in the table within the dynamicDataTable id, these contain the required Max, Min, Mean temperatures.
                        temps = row.find_elements(By.TAG_NAME, "td")
                        if len(temps) >= 3:
                            max_temp = temps[0].text
                            min_temp = temps[1].text
                            mean_temp = temps[2].text
                            daily_temps = {
                                "location": location,
                                "Max" : max_temp,
                                "Min" : min_temp,
                                "Mean" : mean_temp
                            }

                        # Assign full date to data per day
                        full_date = f"{year}-{month:02d}-{day}"

                        # Store the location and daily temps in the weather data dictionary
                        weather_data[full_date]= daily_temps
                    except se.common.exceptions.NoSuchElementException as e:
                        print(f"Element not found: {e}")
                        continue

                # Wait between page loads between each year
                # driver.implicitly_wait(5)

            # page_html = driver.page_source
            # self.feed(page_html)
            driver.quit()
            return weather_data
    
    def check_missing_dates(self, latest_date: str):

        driver = se.webdriver.Chrome()

        # Check today's date
        from datetime import datetime
        today = datetime.today().strftime('%Y-%m-%d')

        daily_temps = {"Max" : str, "Min" : str, "Mean" : str}
        weather_data = {}

        if latest_date == today:
            print("Database is up to date.")
        else:
            print(f"Missing dates between {latest_date} and {today}.")
            print("Scraping and updating missing data...")
            for year in range(int(latest_date.split("-")[0]), int(today.split("-")[0]) + 1):
                month_start = int(latest_date.split("-")[1]) if year == int(latest_date.split("-")[0]) else 1
                month_end = int(today.split("-")[1]) if year == int(today.split("-")[0]) else 12

                for month in range(month_start, month_end + 1):
                    url = f"https://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID=27174&timeframe=2&StartYear={year}&EndYear={year}&Day=1&Year={year}&Month={month:02d}"
                    print(f"Scraping missing data for year: {year}, month: {month}")
                    driver.get(url)
                    html_page = driver.page_source
                



                location_element = driver.find_element(By.CLASS_NAME, "table-header").text
                location = location_element.split("\n")[0]
                rows = driver.find_elements(By.XPATH, "/html/body/main/div/div[5]/table/tbody/tr")
                print(f"Rows found: {len(rows)}")

                for row in rows:
                    try:

                        # Find all abbr tags with title attribute, this selector contains the days
                        day = row.find_element(By.CSS_SELECTOR, "th a[href]").text

                    
                        # Find the first three td elements in the table within the dynamicDataTable id, these contain the required Max, Min, Mean temperatures.
                        temps = row.find_elements(By.TAG_NAME, "td")
                        if len(temps) >= 3:
                            max_temp = temps[0].text
                            min_temp = temps[1].text
                            mean_temp = temps[2].text
                            daily_temps = {
                                "location": location,
                                "Max" : max_temp,
                                "Min" : min_temp,
                                "Mean" : mean_temp
                            }

                        # Assign full date to data per day
                        full_date = f"{year}-{month:02d}-{day}"

                        # Store the location and daily temps in the weather data dictionary
                        weather_data[full_date]= daily_temps
                    except se.common.exceptions.NoSuchElementException as e:
                        print(f"Element not found: {e}")
                        continue

                # Wait between page loads between each year
                # driver.implicitly_wait(5)

            # page_html = driver.page_source
            # self.feed(page_html)
            driver.quit()
            return weather_data




if __name__ == "__main__":
    scraper = WeatherScraper()
    start_year = '2024'
    start_month = '01'
    end_year = '2026'
    url = f"https://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID=27174&timeframe=2&StartYear={start_year}&EndYear={end_year}&Day=1&Year={start_year}&Month={start_month}"
    grab_weather = scraper.scrape_weather(url, start_year, end_year, start_month)
    print((f"Data scraped: len{grab_weather} entries, {grab_weather}"))
