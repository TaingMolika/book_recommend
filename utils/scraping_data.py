import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bs4 import BeautifulSoup
import requests
import pandas as pd
from config import user_agent

HEADERS = {
    'User-Agent': user_agent
}

def scrape_links(base_url, start_page=1, max_pages=None):
    """
    Scrape only book links from books.toscrape.com.
    """
    all_links = []  # List to collect links
    page = start_page

    while True:
        url = base_url.format(page)
        print(f"Scraping {url}")

        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            print("No more pages to scrape or page not found!")
            break

        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all("li", attrs={'class': "col-xs-6 col-sm-4 col-md-3 col-lg-3"})

        if not links:
            print("No more books found!")
            break

        for link in links:
            title_tag = link.find('h3').find('a')
            book_link = title_tag['href'].lstrip("../") if title_tag else None
            full_link = "https://books.toscrape.com/catalogue/" + book_link if book_link else None
            if full_link:
                all_links.append(full_link)

        page += 1

        if max_pages and page > max_pages:
            print(f"Reached max_pages = {max_pages}. Stopping.")
            break

    return all_links  


def scrap_data(links):
    upc = []
    all_images = []  # List to collect image URLs
    titles = []
    desc = []
    prices = []
    availability = []
    rate = [] 

    for link in links:
        response = requests.get(link, headers=HEADERS)
        
        if response.status_code != 200:
            print(f"Failed to fetch {link}")
            continue  # skip this link if error

        soup = BeautifulSoup(response.content, "html.parser")
        upc = soup.find("div", attrs = {"class" : "col-sm-6 product_main"}).find("h1")
        img_tag = soup.find('img')  # Now you have real soup object

        if img_tag:
            img_src = img_tag.get('src')  # safer way
            if img_src:
                img_src = img_src.lstrip("../../")  # Clean the leading ../
                full_img_url = "https://books.toscrape.com/" + img_src
                all_images.append(full_img_url)
                print(full_img_url)

    return all_images, upc

# --------------------
# USE THE FUNCTION
# --------------------

base_url = "https://books.toscrape.com/catalogue/page-{}.html"

book_links = scrape_links(base_url, max_pages=2)

image_links = scrap_data(book_links)
print(image_links)

# df = pd.DataFrame(book_links, columns=["Book Link"])
# df.to_csv("book_links.csv", index=False)

# print("Scraping completed and saved to book_links.csv!")
