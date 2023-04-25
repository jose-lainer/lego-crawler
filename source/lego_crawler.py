import time
import datetime
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException

class LegoCrawler():
    def __init__(self):
        self.url = 'https://www.lego.com/en-us/themes'
        self.driver = None
        self.lego_data = []

    def __open_browser(self, url):
        options = webdriver.ChromeOptions()
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36")
        options.add_argument('--start-maximized')
        options.add_experimental_option("detach", True)
        driver_path = Service('C:/Users/laine/Downloads/chromedriver.exe')
        driver = webdriver.Chrome(service=driver_path, options=options)
        driver.get(url)
        return driver

    def __accept_cookies(self):
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                    (By.XPATH, "//button[@data-test='age-gate-grown-up-cta']"))).click()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                    (By.XPATH, "//button[@data-test='cookie-accept-all']"))).click()

    def __get_theme_links(self):
        theme_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[data-test='themes-link']")
        theme_links = [link.get_attribute("href") for link in theme_elements
                       if not link.get_attribute("href").endswith('about')]
        return theme_links

    def __get_product_links(self):
        product_links = []
        while True:
            product_elements = WebDriverWait(self.driver, 10).until(EC.visibility_of_all_elements_located(
                                    (By.CSS_SELECTOR, "a[data-test='product-leaf-title-link']")))
            time.sleep(5)
            product_links.extend([link.get_attribute("href") for link in product_elements])
            try:
                next_button = self.driver.find_elements(By.CSS_SELECTOR, "a[data-test='pagination-next']")
            except NoSuchElementException:
                next_button = 0
            if len(next_button) == 0:
                break
            else:
                next_button[0].click()
        return product_links

    def __get_product_data(self, prod):
        product_data = []
        # Item Code
        code_value = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "div[data-test='item-value'] span"))).text
        product_data.append(code_value)
        # Theme
        theme_value = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                            (By.XPATH, "/html/body/div[1]/div/main/div/ol/li[2]/a/span/span"))).text
        product_data.append(theme_value)
        # Name
        name_value = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "h1[data-test='product-overview-name'] span"))).text
        product_data.append(name_value)
        # Price
        price_value = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "span[data-test='product-price']"))).text.split('$')[1]
        product_data.append(price_value)
        # Rating
        try:
            rating_value = self.driver.find_element\
                            (By.XPATH, "/html/body/div[1]/div/main/div/div[1]/div/div[2]/div[1]/div/div/span").text
            rating_value = rating_value.replace('Average rating', '').replace('out of 5 stars', '')
        except NoSuchElementException:
            rating_value = 'NA'
        product_data.append(rating_value)
        # Pieces
        try:
            pieces_value = self.driver.find_element(By.CSS_SELECTOR, "div[data-test='pieces-value'] span").text
        except NoSuchElementException:
            pieces_value = 'NA'
        product_data.append(pieces_value)
        # VIP Points
        try:
            vip_points_value = self.driver.find_element(By.CSS_SELECTOR, "div[data-test='vip-points-value'] span").text
        except NoSuchElementException:
            vip_points_value = 'NA'
        product_data.append(vip_points_value)
        # URL
        product_data.append(prod)
        # Date of scraping
        date = datetime.datetime.now()
        scraped_date = date.strftime('%Y-%m-%d')
        product_data.append(scraped_date)
        return product_data

    def __get_lego_data(self, data):
        # Get DataFrame from data
        array = np.array(self.lego_data).reshape(-1, 9)
        lego_df = pd.DataFrame(array, columns=['code','theme','name','price','rating','pieces','vip_points','URL','scraped_on'])
        # Sort values by code and remove duplicates
        lego_df = lego_df.sort_values(by='code').drop_duplicates(subset='code')
        # Export data to CSV file
        lego_df.to_csv('lego_data.csv', index=False)

    def scrape(self):
        # Start timer
        start_time = time.time()

        # Enter the Lego site and accept cookies
        self.driver = self.__open_browser(self.url)
        self.__accept_cookies()

        # Get the links to each Lego theme
        theme_links = self.__get_theme_links()

        for theme in theme_links:
            self.driver.get(theme)
            time.sleep(5)
            print(f'======= Theme: {theme} =======')
            # Get the links to each of the products in the theme
            product_links = self.__get_product_links()

            for prod in product_links:
                self.driver.get(prod)
                # Get the data for each of the products of the theme
                product_data = self.__get_product_data(prod)
                self.lego_data.append(product_data)
                print(product_data)

        # Get data in a CSV file
        self.__get_lego_data(self.lego_data)

        # Show elapsed time
        end_time = time.time()
        print("\nelapsed time: " + str(round(((end_time - start_time) / 60), 2)) + " minutes")

driver = LegoCrawler()
driver.scrape()