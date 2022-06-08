import unittest
from currys_scraper import CurrysLaptopScraper

class ScraperTestCase(unittest.TestCase):
    def setUp(self):
        self.test = CurrysLaptopScraper()
    
    def test_webpage_exists(self):
        self.test.go_to_page(self.test.base_url)
        self.assertTrue(" " in self.test.driver.page_source)
    
    def test_find_accept_cookies_button(self):
        self.test.go_to_page(self.test.base_url)
        e = self.test.accept_cookies()
        self.assertIsNone(e)
    
    def test_find_urls(self):
        self.test.go_to_page(self.test.base_url)
        self.test.accept_cookies()
        self.test.search_laptops()
        self.test.get_urls()
        self.assertNotEqual(len(self.test.urls), 0)
    
    def test_get_attributes(self):
        self.test.go_to_page(self.test.base_url)
        self.test.accept_cookies()
        self.test.search_laptops()
        self.test.get_urls()
        self.test.__urls = list(self.test.urls)
        test_laptop = self.test.__urls[0]
        self.test.go_to_page(test_laptop)
        self.assertTrue(self.test.scrape(test_laptop))

if __name__ == '__main__':
    unittest.main(argv=[' '], verbosity=2, exit=False)