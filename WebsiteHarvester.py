import os
import time
import re
import requests
import phonenumbers
from bs4 import BeautifulSoup
import concurrent.futures
from urllib.parse import urlparse
import argparse
import csv
import xml.etree.ElementTree as ET

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'

def get_page_content(url):
    try:
        response = requests.get(url, headers={'User-Agent': USER_AGENT})
        response.raise_for_status()  
        return response.content

    except requests.exceptions.RequestException as e:
        print(f"Error while fetching the page: {e}")
        return None

def get_links_from_page(soup, base_url):
    try:
        links = []
        for a_tag in soup.find_all('a', href=True):
            link = a_tag['href']
            if link.startswith('http'):
                links.append(link)
            else:
                links.append(base_url + link)
        return links

    except Exception as e:
        print(f"Error while extracting links: {e}")
        return []

def scrape_phone_numbers(soup):
    try:
        page_text = soup.get_text()
        phone_numbers = set()

        for match in phonenumbers.PhoneNumberMatcher(page_text, None):
            phone_numbers.add(phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164))

        return list(phone_numbers)

    except Exception as e:
        print(f"Error while scraping phone numbers: {e}")
        return []

def scrape_emails(soup):
    try:
        page_text = soup.get_text()
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_text)
        return emails

    except Exception as e:
        print(f"Error while scraping emails: {e}")
        return []

def scrape_social_media_links(soup):
    try:
        social_media_links = re.findall(r'https?://(?:www\.)?(?:instagram\.com|instagr\.am)/[-\w.]+', soup.prettify())
        social_media_links += re.findall(r'https?://(?:www\.)?(?:facebook\.com|twitter\.com|linkedin\.com)/[-\w.]+', soup.prettify())
        return social_media_links

    except Exception as e:
        print(f"Error while scraping social media links: {e}")
        return []

def scrape_website_and_links(url, max_depth=2, visited=None):
    if visited is None:
        visited = set()

    if max_depth == 0 or url in visited:
        return [], [], []

    print(f"Scraping: {url}")
    visited.add(url)

    page_content = get_page_content(url)
    if page_content is None:
        return [], [], []

    soup = BeautifulSoup(page_content, 'html.parser')

    numbers = scrape_phone_numbers(soup)
    emails = scrape_emails(soup)
    social_media_links = scrape_social_media_links(soup)

    links = get_links_from_page(soup, url)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_link = {executor.submit(scrape_website_and_links, link, max_depth - 1, visited): link for link in links}
        for future in concurrent.futures.as_completed(future_to_link):
            sub_numbers, sub_emails, sub_social_media_links = future.result()
            numbers.extend(sub_numbers)
            emails.extend(sub_emails)
            social_media_links.extend(sub_social_media_links)

    return numbers, emails, social_media_links

def create_output_folder(domain):
    folder_name = domain
    timestamp = int(time.time())
    counter = 1

    while os.path.exists(folder_name):
        folder_name = f"{domain} ({timestamp}_{counter})"
        counter += 1

    os.makedirs(folder_name)
    return folder_name

def read_domains_from_file(file_path):
    try:
        with open(file_path, 'r') as file:

            domains = [line.strip() for line in file.readlines()]
            return domains
    except Exception as e:
        print(f"Error while reading file: {e}")
        return []

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Website Scraper")

    parser.add_argument("-l", "--url", type=str, help="URL to start scraping")
    parser.add_argument("-d", "--depth", type=int, help="Maximum depth to crawl (an integer) [Default:2]")
    parser.add_argument("-f", "--file", type=str, help="Path to a file with domains")

    args = parser.parse_args()

    if args.url and args.file:
        print("Error: Both -l and -f options cannot be used together.")
        parser.print_help()
        exit()

    if args.file:

        domains = read_domains_from_file(args.file)
        if not domains:
            print("No domains found in the file.")
            exit()

        max_depth_to_crawl = args.depth if args.depth else 2

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_domain = {executor.submit(scrape_website_and_links, domain, max_depth_to_crawl): domain for domain in domains}
            for future in concurrent.futures.as_completed(future_to_domain):
                domain = future_to_domain[future]
                scraped_numbers, scraped_emails, scraped_social_media_links = future.result()

                scraped_numbers = list(set(scraped_numbers))
                scraped_emails = list(set(scraped_emails))
                scraped_social_media_links = list(set(scraped_social_media_links))

                parsed_url = urlparse(domain)
                domain_name = parsed_url.netloc

                output_folder = create_output_folder(domain_name)
                print(f"Output for {domain} will be saved in the folder: {output_folder}")

                output_file_numbers = os.path.join(output_folder, "scraped_phone_numbers.txt")
                with open(output_file_numbers, "w", encoding="utf-8") as file:
                    for number in scraped_numbers:
                        file.write(number + "\n")

                print(f"Scraped phone numbers saved to {output_file_numbers}")

                output_file_emails = os.path.join(output_folder, "scraped_emails.txt")
                with open(output_file_emails, "w", encoding="utf-8") as file:
                    for email in scraped_emails:
                        file.write(email + "\n")

                print(f"Scraped emails saved to {output_file_emails}")

                output_file_social_media = os.path.join(output_folder, "scraped_social_media_links.txt")
                with open(output_file_social_media, "w", encoding="utf-8") as file:
                    for link in scraped_social_media_links:
                        file.write(link + "\n")

                print(f"Scraped social media links saved to {output_file_social_media}")

    elif args.url:

        starting_url = args.url
        max_depth_to_crawl = args.depth if args.depth else 2

        scraped_numbers, scraped_emails, scraped_social_media_links = scrape_website_and_links(starting_url, max_depth=max_depth_to_crawl)

        scraped_numbers = list(set(scraped_numbers))
        scraped_emails = list(set(scraped_emails))
        scraped_social_media_links = list(set(scraped_social_media_links))

        parsed_url = urlparse(starting_url)
        domain_name = parsed_url.netloc

        output_folder = create_output_folder(domain_name)
        print(f"Output will be saved in the folder: {output_folder}")

        output_file_numbers = os.path.join(output_folder, "scraped_phone_numbers.txt")
        with open(output_file_numbers, "w", encoding="utf-8") as file:
            for number in scraped_numbers:
                file.write(number + "\n")

        print(f"Scraped phone numbers saved to {output_file_numbers}")

        output_file_emails = os.path.join(output_folder, "scraped_emails.txt")
        with open(output_file_emails, "w", encoding="utf-8") as file:
            for email in scraped_emails:
                file.write(email + "\n")

        print(f"Scraped emails saved to {output_file_emails}")

        output_file_social_media = os.path.join(output_folder, "scraped_social_media_links.txt")
        with open(output_file_social_media, "w", encoding="utf-8") as file:
            for link in scraped_social_media_links:
                file.write(link + "\n")

        print(f"Scraped social media links saved to {output_file_social_media}")

    else:
        print("No URL or file specified. Use -h or --help for usage information.")