import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

# browsing?
# a way to exit while loops...
# for some reason, next page wasnt clicking when i searched for 'search' - think cos of lag I also got this selenium.common.exceptions.StaleElementReferenceException: Message: stale element reference: element is not attached to the page document


class CurrysScraper:
    def __init__(self):
        self.base_url = "https://www.currys.co.uk/"
        self.chromedriver_path = "C:/Users/Abu Hasan/chromedriver102/chromedriver_win32/chromedriver"
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(self.chromedriver_path, options=options)
    
    def create_session(self):
        self.driver.get(self.base_url)
        self.driver.delete_all_cookies()
        time.sleep(2)

    def accept_cookies(self):
        buttons = self.driver.find_elements_by_xpath('//button')
        for button in buttons:
            if "accept" in button.text.lower() and "cookies" in button.text.lower():
                accept_cookies_button = button
        accept_cookies_button.click()
        time.sleep(1)
    
    def perform_search(self):
        while True:
            self.search_word = input("What item would you like to search for?")
            search_box = self.driver.find_element_by_xpath('//*[@id="Search"]')
            search_box.send_keys(self.search_word)
            time.sleep(1)
            search_box.send_keys(Keys.ENTER)
            time.sleep(2)
            try:
                self.driver.find_element_by_xpath('//*[contains(@id, "select2-sort-pagination")]').click()
                break
            except NoSuchElementException:
                print("Please try narrowing your search.")
        time.sleep(1)
        self.driver.find_element_by_xpath('//option[@data-id="50"]').click()
    
    def get_search_result_links(self):
        self.search_result_links = set([])
        while True:
            time.sleep(2)
            links = self.driver.find_elements_by_xpath('//a[@class="link text-truncate pdpLink"]')
            for link in links:
                self.search_result_links.add(link.get_attribute('href'))
            try:
                next_page_button = self.driver.find_element_by_xpath('//a[@class="updateGrid page-next page-link"]')
                next_page_button.click()
            except NoSuchElementException:
                break
        self.search_result_links = list(self.search_result_links)
    
    # def browse_or_search_option(self):
    #     select_browse_or_search = "not selected"
    #     while select_browse_or_search not in {"browse", "search"}:
    #         select_browse_or_search = input("Would you like to search for a specific item/keyword, or browse the website?").lower()
    #         if "browse" in select_browse_or_search:
    #             self.browse_or_search = "browse"
    #         elif "search" in select_browse_or_search or "item" in select_browse_or_search or "keyword" in select_browse_or_search:
    #             self.browse_or_search = "search"

    # def get_categories(self):
    #     self.category_names = []
    #     categories = self.driver.find_elements_by_xpath('/html/body/wainclude/div[1]/div[1]/header/section/div/div/div[2]/div[2]/div[1]/nav/div/ul/li/a')
    #     for category in categories:
    #         self.category_names.append(category.text)

    # def select_category(self):
    #     category = "not selected"
    #     while category not in self.category_names:
    #         category = input(f"Please select from one of the following categories: {self.category_names}").lower()
    #         if "tv" in category or "audio" in category:
    #             category = "TV & Audio"
    #         elif "home" in category or "outdoor" in category:
    #             category = "Home & Outdoor"
    #         else:
    #             category = category.title()
    #     self.category = category

    # def get_sub_categories(self):
    #     self.sub_category_names = []
    #     self.sub_categories = self.driver.find_elements_by_xpath('')

    # def select_sub_category(self):
    #     pass

    # def get_filters(self):
    #     pass

    # def get_filter_options(self):
    #     pass

    def end_session(self):
        self.driver.quit()

if __name__ == '__main__':
    currys_scraper = CurrysScraper()
    currys_scraper.create_session()
    currys_scraper.accept_cookies()
    currys_scraper.perform_search()
    currys_scraper.get_search_result_links()
    currys_scraper.driver.get(currys_scraper.search_result_links[1])
    time.sleep(10)    
    currys_scraper.end_session()