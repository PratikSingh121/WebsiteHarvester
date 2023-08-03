# WebsiteHarvester: The Web Bounty Hunter

![WebsiteHarvester Logo](WebsiteHarvester_logo.png)

## Description

WebsiteHarvester is a powerful web scraping tool designed to extract phone numbers, emails, and social media links from web pages. It supports both URL and file inputs and saves the scraped data in domain-specific folders.

## Features

- Scrapes phone numbers, emails, and social media links.
- Supports single URL and file input for multiple domains.
- Saves results in domain-specific folders.
- Prevents duplication of scraped data.
- Customizable depth for website crawling.
- Multithreaded for faster scraping.

## Requirements

- Python 3.6+
- Libraries: requests, phonenumbers, BeautifulSoup

## How to Use

1. Clone the repository:

   ```bash
   git clone https://github.com/PratikSingh121/WebsiteHarvester.git
   cd WebsiteHarvester

2. Install the required libraries:
  
   ```bash
    pip install -r requirements.txt

3. To Scrape a single website:

   ```bash
    python main.py -u https://example.com

4. To scrape multiple domains from a file:

   Create a text file (e.g., domains.txt) with one domain URL per line.

   ```bash
    python main.py -f domains.txt

5. Depth Parameter
   The depth parameter specifies the maximum depth for website crawling. It controls how many levels of links to follow from the starting URL. For example, if         depth is set to 2, the scraper will follow links on the initial page and then follow links on those pages as well, but not beyond that level. Default depth is 2.
   ```bash
    python main.py -f domains.txt -d 3

 6. The scraped results will be saved in folders named after the domain names.
