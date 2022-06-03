# Data-Collection-Pipeline

This project an end-to-end data collection pipeline that scrapes the details of all laptops on the Currys.co.uk website and saves the resulting dataset to a database. The dataset can be used to perform any data analysis or as part of a data-science project to recommend the best laptop for a use-case.

## Requirements

* Python

## Installation

```python
pip install -r requirements.txt
```

## Run

```python
python currys_scraper.py
```

## Finding each laptop page

The `CurrysLaptopScraper` class uses a Selenium Chromedriver instance to launch the Currys homepage. Selenium is originally used for running test scripts for test automation. However, it makes a great candidate for web-scraping because it navigates through JavaScript object well. The first step it takes is accepting cookies before navigating to the page for all laptop results using the relevant URL. Once it has reached this page, the scraper will set the number of results per page to 50 so that it won't have to search through more than double the pages that's needed (the default is set to 20). The scraper will then begin to retrieve the individual URLs for each laptop listed on the page before moving to the next page and doing the same, until there are no more to retrieve. The URLs are stored in a Python list.

## Retrieving data for each laptop

Next, the scraper begins to collect details from each page in the Python list of URLs. Before it does that though, a UUID is generated for each laptop. All the details are saved in a python dictionary called `attributes`. The first key-value pair stored is the product code for each individual laptop. Then in order - `title`, `image`, `price`, `rating` (if present), `ratingCount` (if present) and specifcations. The specifications are retrieved when the scraper's selenium webdriver scrolls down the page and clicks on the specifcations section. Once the python dictionary is made for each laptop, the dictionary is saved to a json file in the working directory in a folder called `raw_data`. Each laptop page has its own entry with a `data.json` file containing all the key-value pairs, as well as an image file corresponding the laptop.