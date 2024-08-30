# Al Jazeera News Scraper
### This repository contains a web scraping tool designed to extract the latest news articles from the Al Jazeera website. The scraper uses Selenium to navigate the site, perform searches, and collect information on news articles based on a specified search phrase.

## Features
- Automated Web Scraping: The scraper automates the process of searching for news articles on Al Jazeera's website, filtering the results, and extracting relevant information.
- Search Configuration: Users can configure the search phrase, category, sorting criteria, and the maximum number of articles to be retrieved.
- Error Handling: Comprehensive error handling is implemented to capture and log any issues that occur during the scraping process, with specific error codes for different failure scenarios.
- Data Extraction: The scraper extracts essential details from each article, including the title, publication date, description, and image. If the article lacks certain elements, the scraper will gracefully handle the absence and continue processing.
- Image Downloading: Images associated with each news article are downloaded locally and saved with a sanitized filename.
- Excel Export: Extracted news data is saved in an Excel file for further analysis or reporting.

## How It Works
### Setup and Configuration:

- The scraper is initialized and configured with a search phrase, category, sorting order, and maximum results limit.
- The base URL for Al Jazeera is defined, and Selenium is used to open the website and perform the search.

### Handling Cookies and Ads:

- Upon loading the site, the scraper automatically closes any cookie consent banners to ensure uninterrupted operation.
- Advertisements are hidden to prevent interference with the article extraction process.

### Article Extraction:

- The scraper iterates through the list of articles found on the search results page.
- For each article, it retrieves the title, URL, publication date, and description.
- If an article does not contain a date or image, the scraper assigns a default value (e.g., "N/A").

### Image Handling:

Images are downloaded from the articles and saved locally with a sanitized filename that includes part of the article's title.

### Error Handling:

The scraper includes robust error handling to capture any issues that arise during the scraping process, logging them appropriately and continuing with the next article.

### Data Export:

All extracted data is compiled into a structured format and saved into an Excel file for easy access and further processing.
