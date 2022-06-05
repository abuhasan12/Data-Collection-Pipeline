from timeit import timeit
import requests
import json
import os
import time
import uuid
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException

"""
go through and ask urself if i can understand from whats happening or do i need to make variables and document
change to laptop scraper
browsing?
a way to exit while loops...
for some reason, next page wasnt clicking when i searched for 'search' - think cos of lag I also got this selenium.common.exceptions.StaleElementReferenceException: Message: stale element reference: element is not attached to the page document
the other error is the other element would receive click one for pop up - Tell us what you think. selenium.common.exceptions.ElementClickInterceptedException: Message: element click intercepted: Other element would receive the click: 
some products like 359336 dont have a specs section but it didnt break the program
need to see the pop up thing and fix
selenium.common.exceptions.WebDriverException: Message: unknown error: cannot determine loading status
selenium.common.exceptions.WebDriverException: Message: target frame detached
selenium.common.exceptions.UnexpectedAlertPresentException: Alert Text: {Alert text :
//a[@data-close-type="x_close"] ^
here ^
try:
scraped_attributes = self.scrape(url)
except ElementClickInterceptedException:
self.click_popup()
scraped_attributes = self.scrape(url)
"""


class CurrysLaptopScraper:
    '''
    This class is used to create an instance of a web-scraper that will scrape the data for all laptops on the Currys website.
    The attribute base_url is set to "https://www.currys.co.uk/".
    The attribute urls will be populated with the URLs of all laptops on the website.
    '''

    def __init__(self, chromedriver_path: str):
        '''
        An instance of the CurrysLaptopScraper is a web-scraper object that will scrape the data for all laptops on the Currys website.
        The attribute base_url is set to "https://www.currys.co.uk/".
        The attribute urls will be populated with the URLs of all laptops on the website.
        The web-scraper uses a Selenium Chromedriver the path to the Chromedriver should be passed in when initializing the instance.
        '''
        self.__base_url = "https://www.currys.co.uk/"
        self.__urls = set([])
        print(self.__urls)
        self.chromedriver_path = chromedriver_path
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--start-maximized")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(self.chromedriver_path, options=self.options)
    
    @property
    def base_url(self) -> str:
        '''
        Getter for base_url attribute which is set to "https://www.currys.co.uk/" on initialization.
        '''
        return self.__base_url
    
    @property
    def urls(self):
        '''
        Getter for urls attribute which is an empty set on initialization. When calling get_urls() or get_all_urls(), the set will be populated with the URLs of all laptops on the laptops page.
        '''
        return self.__urls
    
    class PageScanner:
        '''
        The PageScanner nested class is used to scrape the information from the page of a laptop. The information received are:
        Product Code
        Title
        Image Source
        Price
        Rating
        Rating Count
        Specifications
        '''
        def __init__(self, driver):
            self.driver = driver

        def get_product_code(self) -> str:
            product_code = self.driver.find_element_by_xpath('//*[@class="product-code"]').text
            return product_code[product_code.find(":")+2 :]
        
        def get_title(self) -> str:
            return self.driver.find_element_by_xpath('//h1[@class="product-name"]').text
        
        def get_image(self) -> str:
            return self.driver.find_element_by_xpath('//div[@class="carouselitem active"]/a/img').get_attribute('src')
        
        def get_price(self) -> str:
            return self.driver.find_elements_by_xpath('//span[@class="value"]')[1].text[1:]
        
        def get_rating(self):
            try:
                rating = self.driver.find_element_by_xpath('//span[@class="star-ratings"]').get_attribute('title')
                return rating[0:rating.find(' ')]
            except:
                return None
        
        def get_rating_count(self):
            try:
                return self.driver.find_element_by_xpath('//span[@class="rating-count"]/a').text[1:-1]
            except:
                return None

        def get_specs(self) -> dict:
            specs_dict = {}
            specs = self.driver.find_elements_by_xpath('//div[@class="tech-specification-body"]/div')
            for spec in specs:
                spec_key = self.get_spec_key(spec).title().replace(" ", "")
                spec_key = spec_key[0].lower() + spec_key[1:]
                spec_value = self.get_spec_value(spec)
                specs_dict[spec_key] = spec_value
            return specs_dict
        
        def get_spec_key(self, spec) -> str:
            return spec.find_element_by_xpath('.//div[@class="tech-specification-th col-6 col-lg-4"]').text
        
        def get_spec_value(self, spec) -> str:
            return spec.find_element_by_xpath('.//div[@class="tech-specification-td col-6 col-lg-8"]').text

        def open_specs(self):
            time.sleep(1)
            product_information_button = self.driver.find_element_by_xpath('//*[@id="accordion"]/div[1]/div/a')
            self.driver.execute_script("arguments[0].scrollIntoView();", product_information_button)
            time.sleep(1)
            self.driver.find_element_by_xpath('//*[@id="accordion"]/div[2]/div/a').click()
    
    def __function_timer(func):
        '''
        Decorator function to time functions.
        '''
        def __timer(*args, **kwargs):
            start_time = time.time()
            func(*args, **kwargs)
            end_time = time.time()
            print(f"{func} took {end_time - start_time} seconds.")
        return __timer

    def __delay_1(func):
        '''
        Decorator function to delay function call by one second.
        '''
        def __add_sleep(*args, **kwargs):
            time.sleep(1)
            func(*args, **kwargs)
        return __add_sleep
    
    def __delay_2(func):
        '''
        Decorator function to delay function call by two seconds.
        '''
        def __add_sleep(*args, **kwargs):
            time.sleep(2)
            func(*args, **kwargs)
        return __add_sleep

    @__delay_1
    @__function_timer
    def go_to_page(self, url: str):
        '''
        Function to go to url of webpage that is passed as argument.
        '''
        self.driver.get(url)

    @__delay_1
    @__function_timer
    def accept_cookies(self):
        '''
        Function to find and accept the cookies button of the page, if it exists.
        '''
        buttons = self.driver.find_elements_by_xpath('//button')
        for button in buttons:
            if "accept" in button.text.lower() and "cookies" in button.text.lower():
                accept_cookies_button = button
        try:
            accept_cookies_button.click()
        except Exception as e:
            print(e)
            return e
    
    @__delay_1
    @__function_timer
    def search_laptops(self):
        '''
        Function to change the webpage to the laptop search results. The function also has added functionality to sort the page to 50 results per page.
        If the page results count cannot be changed to 50, it will try setting to 30, and then 20 if that also fails.
        '''
        self.driver.get(self.base_url + "computing/laptops/laptops")
        time.sleep(1)
        self.driver.find_element_by_xpath('//*[contains(@id, "select2-sort-pagination")]').click()
        time.sleep(1)
        try:
            self.driver.find_element_by_xpath('//option[@data-id="50"]').click()
        except NoSuchElementException:
            try:
                self.driver.find_element_by_xpath('//option[@data-id="30"]').click()
            except NoSuchElementException:
                try:
                    self.driver.find_element_by_xpath('//option[@data-id="20"]').click()
                except Exception as e:
                    print(e)
    
    @__delay_2
    @__function_timer
    def get_urls(self):
        '''
        Function to scrape the URLs of all the laptops listed on the current page and add them to the urls attribute of the object
        '''
        hrefs = self.driver.find_elements_by_xpath('//a[@class="link text-truncate pdpLink"]')
        for href in hrefs:
            self.__urls.add(href.get_attribute('href'))
    
    @__function_timer
    def get_all_urls(self):
        '''
        Function that calls get_urls() which scrapes the URLs of all the laptops listed on the current page and add them to the urls attribute of the object.
        Then this function will look for a 'next page' button to click. If it finds one, it will perform get_urls() again in a loop. Otherwise, it will stop.
        '''
        def click_next_page_button():
            next_page_button = self.driver.find_element_by_xpath('//a[@class="updateGrid page-next page-link"]')
            self.driver.execute_script("arguments[0].scrollIntoView();", next_page_button)
            time.sleep(1)
            next_page_button.click()

        page_not_searched = True
        while page_not_searched:
            self.get_urls()
            page_not_searched = False
            try:
                click_next_page_button()
                page_not_searched = True
            except NoSuchElementException:
                pass

    @staticmethod
    def directory_check():
        '''
        Function to check if a directory called 'raw_data' exists in the working directory. If not, it will create one for you. This directory will be used to save the scraped data in.
        '''
        if not os.path.exists('raw_data'):
            os.makedirs('raw_data')
    
    @__delay_2
    @__function_timer
    def scrape_and_save(self, url: str):
        '''
        Function to scrape the data (see help(CurrysLaptopScraper.PageScanner for a list) of a single laptop page.
        The scraped data is then saved into a file called data.json inside the directory created previously (raw_data - if this was not previously created, it will be created here.)
        The file will be inside the raw_data folder under another folder which corresponds to the ID of the laptop.
        There will also be an image file saved of the laptop.
        The data is scraped as a dictionary before saved as a json file. The dictionary key-value pairs correspond to the information received by PageScanner:
        (uuid is created using Pythons uuid library
        url is the url of the laptop page)
        productID = Product Cpde
        title = Title
        price = Price
        imgSrc = Image Source
        rating = Rating
        ratingCount = Rating Count
        (the key-value pairs of the specifications are dependent on what is available on the page under the Specifications tab.)
        '''
        def save(attributes):
            '''
            See help(CurrysLaptopScraper.scrape_and_save) for details.
            '''
            folder_path = "raw_data/" + attributes['productID']
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                with open(os.path.join(folder_path, 'data.json'), 'w') as fp:
                    json.dump(attributes, fp)
                image_file_name = attributes['productID'] + '.jpg'
                request_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'}
                image_request = requests.get(attributes['imgSrc'], headers=request_headers)
                with open(os.path.join(folder_path, image_file_name), 'wb') as f:
                    f.write(image_request.content)
            else:
                print(f"Folder already exists for {attributes['productID']}")
        
        self.directory_check()
        save(self.scrape(url))

    def scrape(self, url) -> dict:
        '''
        See help(CurrysLaptopScraper.scrape_and_save) for details.
        '''
        page_scanner = self.PageScanner(self.driver)
        attributes = {
            'uuid' : str(uuid.uuid4()),
            'url' : url,
            'productID' : page_scanner.get_product_code(),
            'title' : page_scanner.get_title(),
            'price' : page_scanner.get_price(),
            'imgSrc' : page_scanner.get_image(),
            'rating' : page_scanner.get_rating(),
            'ratingCount' : page_scanner.get_rating_count()
        }
        page_scanner.open_specs()
        time.sleep(1)
        specs = page_scanner.get_specs()
        attributes.update(specs)
        return attributes

    @__function_timer
    def scrape_urls(self):
        '''
        Function that loops through all URLs (if any) of the urls set (converted to a list) and runs scrape() on all of them.
        TODO: handle popups
        '''
        if len(self.urls) == 0:
            print("There are no URLs to scrape! Run get_urls()")
        else:
            self.__urls = list(self.__urls)
            for url in self.urls:
                self.go_to_page(url)
                try:
                    self.scrape_and_save(url)
                except ElementClickInterceptedException:
                    self.click_popup()
                    self.scrape_and_save(url)
    
    def click_popup(self):
        '''
        Function to handle popups when scraping information from a laptop's page.
        '''
        buttons = self.driver.find_elements_by_xpath('//button')
        for button in buttons:
            if "accept" in button.text.lower() and "cookies" in button.text.lower():
                accept_cookies_button = button
        accept_cookies_button.click()

    def end_session(self):
        '''
        Function to quit the Selenium Chromedriver
        '''
        self.driver.quit()


if __name__ == '__main__':
    laptop_scraper = CurrysLaptopScraper(chromedriver_path="./chromedriver102/chromedriver_win32/chromedriver")
    laptop_scraper.go_to_page(laptop_scraper.base_url)
    laptop_scraper.accept_cookies()
    laptop_scraper.search_laptops()
    laptop_scraper.get_all_urls()
    laptop_scraper.scrape_urls()
    # first_forty = laptop_scraper.urls[0:41]
    # for each in first_forty:
    #     try:
    #         laptop_attributes = laptop_scraper.scrape(each)
    #     except ElementClickInterceptedException:
    #         laptop_scraper.click_popup()
    #         laptop_attributes = laptop_scraper.scrape(each)
    #     laptop_scraper.save_scraped(laptop_attributes)
    time.sleep(10)
    laptop_scraper.end_session()