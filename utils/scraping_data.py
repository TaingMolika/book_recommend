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
    all_links = []
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
    upcs = []
    all_images = []
    titles = []
    descs = []
    prices = []
    availability = []
    rates = []

    for link in links:
        response = requests.get(link, headers=HEADERS)
        
        if response.status_code != 200:
            print(f"Failed to fetch {link}")
            continue

        soup = BeautifulSoup(response.content, "html.parser")

        title = soup.find("div", class_="col-sm-6 product_main").find("h1").text.strip()
        titles.append(title)

        description_tag = soup.find("meta", attrs={"name": "description"})
        description = description_tag['content'].strip() if description_tag else "No description"
        descs.append(description)

        price_tag = soup.find("p", class_="price_color")
        prices.append(price_tag.text.strip() if price_tag else "N/A")

        avail_tag = soup.find("p", class_="instock availability")
        availability.append(avail_tag.text.strip() if avail_tag else "N/A")

        rating_tag = soup.find("p", class_="star-rating")
        rating_class = rating_tag.get("class")[1] if rating_tag else "None"
        rates.append(rating_class)

        upc_tag = soup.find("table", class_="table table-striped").find("tr")
        upcs.append(upc_tag.find("td").text if upc_tag else "N/A")

        img_tag = soup.find('img')
        if img_tag:
            img_src = img_tag.get('src').lstrip("../../")
            full_img_url = "https://books.toscrape.com/" + img_src
            all_images.append(full_img_url)
        else:
            all_images.append("No image")

    df = pd.DataFrame({
        "UPC": upcs,
        "Title": titles,
        "Description": descs,
        "Price": prices,
        "Availability": availability,
        "Rating": rates,
        "Image": all_images,
        "Product Link": links
    })

    return df

# base_url = "https://books.toscrape.com/catalogue/page-{}.html"

# book_links = scrape_links(base_url, max_pages=2)
# book_data_df = scrap_data(book_links)

# book_data_df.to_csv("data.csv", index=False)
# print("Scraping complete! Data saved to book_data.csv.")