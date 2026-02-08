from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
from pathlib import Path

PATH_OUTPUT = Path("./data/raw")
PATH_OUTPUT.mkdir(parents=True, exist_ok=True)

BASE = "https://www.horsedeals.com.au"
FILTER_PATH = "/search/horses-for-sale?page={page}"

def get_soup_from_page(page, url):
    page.goto(url, timeout=30_000)
    page.wait_for_timeout(5000)
    html = page.content()
    return BeautifulSoup(html, "lxml")

def scrape_listings(max_pages=2):

    rows = []
    listing_urls = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=100)
        context = browser.new_context( 
            viewport={"width": 1280, "height": 800}, 
            user_agent=( 
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " 
                "AppleWebKit/537.36 (KHTML, like Gecko) " 
                "Chrome/120.0.0.0 Safari/537.36"), 
                )

        page = context.new_page()

        for page_num in tqdm(range(1, max_pages+1), total=max_pages, desc="Scraping Pages", leave=True, position=0):
            url = f"{BASE}{FILTER_PATH.format(page=page_num)}"
            soup = get_soup_from_page(page, url)

            links = soup.select("div.listingcard-module-pricingBox-Jfp > a[href*='/classifieds/item/horses/']")
             
            for a in links:
                href = str(a.get("href"))
                if not href:
                    continue

                card_url = BASE + href
                listing_urls.add(card_url)

        for lurl in tqdm(listing_urls, total=len(listing_urls), desc="Scraping Horse Profiles", leave=False):
            try:
                lsoup = get_soup_from_page(page, lurl)

                data = {}
                data["Horse_ID"] = lurl.split("-")[-1]
                data["Horse Profile"] = lurl

                #Name
                h1_name = lsoup.select_one("div.header-module-wrap-b4F > div > h1")
                name = h1_name.get_text(strip=True) if h1_name else None
                
                # Location
                span_location = lsoup.select_one("div.header-module-location-KUa > a > span")
                location = span_location.get_text(strip=True) if span_location else None

                # Price
                div_price = lsoup.select_one("div.header-module-AdPrice-7B-")
                price = div_price.get_text(strip=True) if div_price else None

                #Summary
                span_key_features = lsoup.select("div.summary-module-SummaryLeft-8TB > span")
                span_value_features = lsoup.select("div.summary-module-SummaryRight-okZ > span")
                
                for span_key, span_value in zip(span_key_features, span_value_features):
                    
                    key = span_key.get_text(strip=True) if span_key else None
                    value = span_value.get_text(strip=True) if span_value else None

                    data[key] = value

                a_rider_level = lsoup.select_one("div.summary-module-SummaryRight-okZ > a[href*='/rider-level/'] > span")
                rider_level = a_rider_level.get_text(strip=True) if a_rider_level else None
                
                a_breed = lsoup.select_one("div.summary-module-SummaryRight-okZ > a[href*='/breed/'] > span")
                breed = a_breed.get_text(strip=True) if a_breed else None

                a_disciplines = lsoup.select("div.summary-module-SummaryRight-okZ > a[href*='/disciplines/'] > span")
                discipline = [a_discipline.get_text(strip=True) if a_discipline else None for a_discipline in a_disciplines]

                #Description
                div_description = lsoup.select_one("div.summary-module-viewAll--b2")
                description = div_description.get_text(strip=True) if div_description else None

                data["Name"] = name
                data["Location"] = location
                data["Description"] = description
                data["Rider Level"] = rider_level
                data["Breed"] = breed
                data["Discipline"] = discipline
                data["Price"] = price
            
                rows.append(data)

            except Exception as e:
                print(f"Error scraping {lurl}: {e}")

    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = scrape_listings(max_pages=1)
    df.to_parquet(PATH_OUTPUT / "horsedeals_horses_listings.parquet", index=False)