from email import header
import requests
import json
import os
import time
import uuid
from attr import attr
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException

# go through and ask urself if i can understand from whats happening or do i need to make variables and document
# change to laptop scraper
# browsing?
# a way to exit while loops...
# for some reason, next page wasnt clicking when i searched for 'search' - think cos of lag I also got this selenium.common.exceptions.StaleElementReferenceException: Message: stale element reference: element is not attached to the page document
# the other error is the other element would receive click one for pop up - Tell us what you think. selenium.common.exceptions.ElementClickInterceptedException: Message: element click intercepted: Other element would receive the click: 

class CurrysLaptopScraper:
    def __init__(self):
        self.base_url = "https://www.currys.co.uk/"
        self.chromedriver_path = "./chromedriver102/chromedriver_win32/chromedriver" #insert your path to the chromedriver here
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(self.chromedriver_path, options=options)
    
    def create_session(self):
        self.driver.get(self.base_url)
        time.sleep(1)
        self.driver.delete_all_cookies()

    def accept_cookies(self):
        time.sleep(1)
        buttons = self.driver.find_elements_by_xpath('//button')
        for button in buttons:
            if "accept" in button.text.lower() and "cookies" in button.text.lower():
                accept_cookies_button = button
        accept_cookies_button.click()
    
    def perform_search(self):
        time.sleep(1)
        self.driver.get(self.base_url + "computing/laptops/laptops")
        time.sleep(2)
        results_count = self.driver.find_element_by_xpath('//*[contains(@id, "select2-sort-pagination")]')
        results_count.click()
        time.sleep(1)
        results_count_50 = self.driver.find_element_by_xpath('//option[@data-id="50"]')
        results_count_50.click()
    
    def get_search_result_links(self):
        self.search_result_links = set([])
        while True:
            time.sleep(2)
            links = self.driver.find_elements_by_xpath('//a[@class="link text-truncate pdpLink"]')
            for link in links:
                self.search_result_links.add(link.get_attribute('href'))
            try:
                time.sleep(1)
                next_page_button = self.driver.find_element_by_xpath('//a[@class="updateGrid page-next page-link"]')
                self.driver.execute_script("arguments[0].scrollIntoView();", next_page_button)
                time.sleep(1)
                next_page_button.click()
            except NoSuchElementException:
                break
        self.search_result_links = list(self.search_result_links)

    def get_product_code(self):
        product_code = self.driver.find_element_by_xpath('//*[@class="product-code"]').text
        return product_code[product_code.find(":")+2 :]
    
    def get_title(self):
        title = self.driver.find_element_by_xpath('//h1[@class="product-name"]').text
        return title
    
    def get_image(self):
        image_source =  self.driver.find_element_by_xpath('//div[@class="carouselitem active"]/a/img').get_attribute('src')
        return image_source
    
    def get_price(self):
        price = self.driver.find_elements_by_xpath('//span[@class="value"]')[1].text[1:]
        return price
    
    def get_rating(self):
        try:
            rating = self.driver.find_element_by_xpath('//span[@class="star-ratings"]').get_attribute('title')
            return rating[0:rating.find(' ')]
        except Exception as e:
            print("Failed 1")
            return None
    
    def get_rating_count(self):
        try:
            rating_count = self.driver.find_element_by_xpath('//span[@class="rating-count"]/a').text[1:-1]
            return rating_count
        except Exception as e:
            print("Failed 2")
            return None
    
    def get_specs(self):
        specs = self.driver.find_elements_by_xpath('//div[@class="tech-specification-body"]/div')
        return specs
    
    def get_spec_key(self, spec):
        spec_key = spec.find_element_by_xpath('.//div[@class="tech-specification-th col-6 col-lg-4"]').text
        return spec_key
    
    def get_spec_value(self, spec):
        spec_value = spec.find_element_by_xpath('.//div[@class="tech-specification-td col-6 col-lg-8"]').text
        return spec_value
    
    def scrape(self, laptop_link):
        time.sleep(1)
        self.driver.get(laptop_link)
        time.sleep(2)
        attributes = {}
        attributes['uuid'] = str(uuid.uuid4())
        attributes['href'] = laptop_link
        attributes['id'] = self.get_product_code()
        attributes['title'] = self.get_title()
        attributes['price'] = self.get_price()
        attributes['imageSource'] = self.get_image()
        time.sleep(1)
        attributes['rating'] = self.get_rating()
        attributes['ratingCount'] = self.get_rating_count()
        time.sleep(1)
        product_information_button = self.driver.find_element_by_xpath('//*[@id="accordion"]/div[1]/div/a')
        self.driver.execute_script("arguments[0].scrollIntoView();", product_information_button)
        time.sleep(1)
        specifications_button = self.driver.find_element_by_xpath('//*[@id="accordion"]/div[2]/div/a')
        specifications_button.click()
        specs = self.get_specs()
        for spec in specs:
            spec_key = self.get_spec_key(spec).title().replace(" ", "")
            spec_key = spec_key[0].lower() + spec_key[1:]
            spec_value = self.get_spec_value(spec)
            attributes[spec_key] = spec_value
        return attributes
    
    def save_scraped(self, attributes):
        raw_data_path = "raw_data/"
        folder_path = raw_data_path + attributes['id']
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            with open(os.path.join(folder_path, 'data.json'), 'w') as fp:
                json.dump(attributes, fp)
            image_file_name = attributes['id'] + '.jpg'
            request_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'}
            image_request = requests.get(attributes['imageSource'], headers=request_headers)
            with open(os.path.join(folder_path, image_file_name), 'wb') as f:
                f.write(image_request.content)
        else:
            print(f"Folder already exists for {attributes['id']}")


    def scrape_all(self):
        for result_link in self.search_result_links:
            scraped_attributes = self.scrape(result_link)
            self.save_scraped(scraped_attributes)
    
    def directory_check(self):
        raw_data_path = 'raw_data'
        if not os.path.exists(raw_data_path):
            os.makedirs(raw_data_path)
    
    def click_popup(self):
        buttons = self.driver.find_elements_by_xpath('//button')
        for button in buttons:
            if "accept" in button.text.lower() and "cookies" in button.text.lower():
                accept_cookies_button = button
        accept_cookies_button.click()

    def end_session(self):
        self.driver.quit()


if __name__ == '__main__':
    laptop_scraper = CurrysLaptopScraper()
    laptop_scraper.create_session()
    laptop_scraper.accept_cookies()
    laptop_scraper.perform_search()
    laptop_scraper.get_search_result_links()
    laptop_scraper.directory_check()
    first_forty = laptop_scraper.search_result_links[0:41]
    for each in first_forty:
        try:
            laptop_attributes = laptop_scraper.scrape(each)
        except ElementClickInterceptedException:
            laptop_scraper.click_popup()
            laptop_attributes = laptop_scraper.scrape(each)
        laptop_scraper.save_scraped(laptop_attributes)
    time.sleep(10)
    laptop_scraper.end_session()