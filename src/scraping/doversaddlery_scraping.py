import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
from tqdm import tqdm
from pathlib import Path

PATH_OUTPUT = Path("./data/raw")
PATH_OUTPUT.mkdir(parents=True, exist_ok=True)

BASE = "https://www.doversaddlery.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def get_soup(url, sleep_seconds=4):
    resp = requests.get(url, headers=HEADERS, timeout=30)
    sleep(sleep_seconds)  # rate limit suave
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "lxml")

def scrape_listings(pages_per_category=2, sleep_seconds=5):
    rows = []
    url = f"{BASE}"
    soup = get_soup(url)

    a_categories = soup.select('ul[role="menubar"] > li.menu-item-has-children > a[href]')
    categories_urls = set()

    for a in a_categories:
        href = str(a.get("href"))
        if not href:
            continue

        category_url = url + href
        categories_urls.add(category_url)

    product_urls = set()

    for category_url in tqdm(categories_urls, total=len(categories_urls), desc="Scraping Product Categories", leave=False, position=0):
        for page in range(1, pages_per_category+1):
            try:
                cat_soup = get_soup(f"{category_url}?page={page}")
                a_products = cat_soup.select("a.product-card-title")
                for a in a_products:
                    href = str(a.get("href"))
                    if not href:
                        continue

                    product_url = url + href
                    product_urls.add(product_url)
                    break
            except Exception as e:
                break  # salimos de esta categoría
        break

    for product_url in tqdm(product_urls, total=len(product_urls), desc="Scraping Horse Profiles", leave=False, position=0):
        try:
            data = {}

            #Caracteristicas del producto
            psoup = get_soup(product_url)

            # Item ID
            el = psoup.select_one("p.product--text.style_vendor")
            item_id = el.get_text(strip=True).split(":")[-1].strip() if el else None

            # Product name
            el = psoup.select_one("h1.product-title.uppercase--false.heading-font")
            product_name = el.get_text(strip=True) if el else None

            # Price
            el = psoup.select_one("span.amount")
            price = el.get_text(strip=True) if el else None

            # Category
            category = product_url.split("/")[4]

            # Stock
            el = psoup.select_one("div.product-inventory-notice--text")
            stock = el.get_text(strip=True) if el else None

            # Description
            el = psoup.select_one("div.rte")
            description = el.get_text(separator="\n", strip=True) if el else None

            #Imagen
            a_imgs = psoup.select("a.product-single__media-zoom")
            img_urls = list() 
            for a in a_imgs:
                href = str(a.get("href"))
                if not href:
                    continue

                if href and href.startswith("//"):
                    img_url = "https:" + href
                else:
                    img_url = None   
                img_urls.append(img_url)

            data["Item_ID"] = item_id
            data["Name"] = product_name
            data["Stock"] = stock
            data["Description"] = description
            data["Price"] = price
            data["Category"] = category
            data["Images"] = img_urls
            data["URL"] = product_url

            rows.append(data)

        except Exception as e:
            print(f"Error scraping {product_url}: {e}")

    df = pd.DataFrame(rows)
    return df

if __name__ == "__main__":
    df = scrape_listings(pages_per_category=1)
    df.to_parquet(PATH_OUTPUT / "doversaddlery_products_listing.parquet", index=False)