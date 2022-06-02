# Data-Collection-Pipeline

## Milestone 1 - Decide website

This scraper will scrape product details from the Currys website

## Milestone 2 - Prototype finding the individual page for each entry

I have created a scraper class that contains various methods to perform the function of webscraping. The webscraping is done using selenium chromedriver to navigate the web browser. Each instance of the class is initialised with the Currys homepage as the base URL. There are methods to accept cookies and perform a search based on the search input that the user picks. Once the search is performed, the program will go through each page of the page results and retrieve an individial link for each result into a list.