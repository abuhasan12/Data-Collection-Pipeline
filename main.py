import sys
import time
from currys_scraper import CurrysLaptopScraper
from data_processing import process_data
from data_processing import process_data_from_to_dict
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import WebDriverException
from s3_upload import save_s3
from rds_upload import load_data

def main():
    laptop_scraper = CurrysLaptopScraper()
    laptop_scraper.scrape_urls()
    # test_urls = ['https://www.currys.co.uk/products/lenovo-ideapad-duet-3i-10.3-2-in-1-laptop-intel-celeron-64-gb-emmc-grey-10221285.html', 'https://www.currys.co.uk/products/acer-aspire-5-a51454-14-laptop-intel-core-i3-128-gb-ssd-silver-10212861.html']
    # test_urls_2 = ['https://www.currys.co.uk/products/lenovo-ideapad-duet-3i-10.3-2-in-1-laptop-intel-celeron-64-gb-emmc-grey-10221285.html', 'https://www.currys.co.uk/products/acer-aspire-5-a51454-14-laptop-intel-core-i3-128-gb-ssd-silver-10212861.html', 'https://www.currys.co.uk/products/dell-inspiron-14-5415-14-laptop-amd-ryzen-5-256-gb-ssd-silver-10230731.html', 'https://www.currys.co.uk/products/dynabook-toshiba-satellite-pro-c40-14-laptop-intel-core-i5-256-gb-ssd-dark-blue-10235541.html']
    # for url in test_urls_2:
    for url in laptop_scraper.urls[0:2]:
        laptop_scraper.go_to_page(url)
        try:
            attributes = laptop_scraper.scrape(url)
        except UnexpectedAlertPresentException:
            laptop_scraper.close_popup()
            attributes = laptop_scraper.scrape(url)
        except WebDriverException as e:
            if 'from target frame detached' in str(e):
                time.sleep(2)
                attributes = laptop_scraper.scrape(url)
            else:
                print(e)
                sys.exit()
        except Exception as e:
            print (e)
            sys.exit()
        if not attributes:
            continue
        try:
            save_s3(attributes, "data.json")
            processed_attributes = process_data_from_to_dict(attributes)
            save_s3(processed_attributes, f"{str(processed_attributes['productID'])}.json")
        except Exception as e:
            print(e)
            print("Could not save to s3. Storing data locally.")
            attributes = laptop_scraper.scrape(url)
            laptop_scraper.save_local(attributes)
    laptop_scraper.end_session()
    df = process_data(laptop_scraper.data)
    try:
        load_data(df)
    except Exception as e:
        print(e)
        print("Could not save data to RDS. Storing locally.")
        df.to_csv('Output.csv', index=False, mode='w+')

if __name__ == '__main__':
    main()