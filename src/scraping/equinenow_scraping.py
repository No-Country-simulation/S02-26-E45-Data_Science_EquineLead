import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urlparse
from time import sleep
from tqdm import tqdm

BASE = "https://www.equinenow.com"

FILTER_PATH = (
    "/browse-ssf--brf--clf--sxf--tgf--htf--agf--prf--"
    "auc-1-sdf-1-slf-1-orf--pg-{page}-"
    "rsf--dsf--svf--cnf--pnf--wbf--rgf-"
)

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

def scrape_listings(max_pages=2):

    rows = []
    listing_urls = set()

    for page in tqdm(range(0, max_pages), total=max_pages, desc="Scraping Pages", leave=True, position=0):
        url = f"{BASE}{FILTER_PATH.format(page=page)}"
        soup = get_soup(url)

        links = soup.select("a[href*='horse-ad'].btn.btn-details.btn-sm")

        for a in links:
            href = str(a.get("href"))
            if not href:
                continue

            # nos quedamos solo con el path /horse-ad-XXXX
            parsed = urlparse(href)
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            listing_urls.add(clean_url)

    for lurl in tqdm(listing_urls, total=len(listing_urls), desc="Scraping Horse Profiles", leave=False, position=0):
        try:
            data = {}
            data["Horse_ID"] = lurl.split("-")[-1]

            #Caracteristicas del caballo
            lsoup = get_soup(lurl).body
            if lsoup:
                ul_features_horse = lsoup.select_one("ul.meta-data.list-unstyled")


                for dl in ul_features_horse.select("dl.row"):
                    key = dl.find("dt").get_text(strip=True)
                    value = dl.find("dd").get_text(strip=True)

                    data[key] = value

                # Location
                h5_location = lsoup.select_one("div.col-xs-12.col-sm-5.no-padding-xs div header h5")
                location = h5_location.get_text(strip=True) if h5_location else None

                # Price
                span_price = lsoup.select_one("span.item-price")
                price = span_price.get_text(strip=True) if span_price else None

                # Skills / Disciplines
                dl = lsoup.find("dt", string="Skills / Disciplines")
                skills_disciplines = None
                if dl:
                    dd = dl.find_next_sibling("dd")
                    skills_disciplines = dd.get_text(strip=True) if dd else None

                # Additional comments (span[itemprop="description"])
                desc_span = lsoup.select_one('div.well p span[itemprop="description"]')
                additional_comments = desc_span.get_text(strip=True) if desc_span else None

                # Shipping (segundo <p> después de div.well)
                p_shipping = lsoup.select_one("div.well p ~ p")
                shipping = p_shipping.get_text(strip=True) if p_shipping else None

                # Company name (h4)
                h4_cn = lsoup.select_one("div.well h4")
                company_name = h4_cn.get_text(strip=True) if h4_cn else None

                # Company profile href (primer <a> dentro de los <p> después de h4)
                a_cp = lsoup.select_one("div.well h4 + p ~ p a")
                company_profile = a_cp.get("href") if a_cp else None

                data["Location"] = location
                data["Price"] = price
                data["Horse Profile"] = lurl
                data["Skills"] = skills_disciplines
                data["Comments"] = additional_comments
                data["Shipping"] = shipping
                data["Company Name"] = company_name
                data["Company Profile"] = company_profile

                rows.append(data)

        except Exception as e:
            print(f"Error scraping {lurl}: {e}")

    df = pd.DataFrame(rows)
    return df

df = scrape_listings(max_pages=400)
df.to_parquet("./data/raw/equinenow_horses_listings.parquet", index=False)

