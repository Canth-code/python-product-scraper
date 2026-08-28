import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import time
import logging
from database import save_products
from concurrent.futures import ThreadPoolExecutor
# ==========================================
# CONFIG
# ==========================================
START_TIME = time.time()
BASE_URL = "https://books.toscrape.com"
MAX_WORKERS = 10
MAX_RETRIES = 3
TIMEOUT = 10
# ==========================================
# LOGGING
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    filename="scraper.log",
    encoding="utf-8"
)
logger = logging.getLogger(__name__)
# ==========================================
# SESSION
# ==========================================
session = requests.Session()
# ==========================================
# CREATE URLS
# ==========================================

urls = [BASE_URL]

urls += [
    f"{BASE_URL}/catalogue/page-{page}.html"
    for page in range(2, 51)
]

print(f"Total URLs: {len(urls)}")

logger.info(f"Total URLs: {len(urls)}")


# ==========================================
# FETCH + PARSE PAGE
# ==========================================

def fetch_page(url):

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            response = session.get(
                url,
                timeout=TIMEOUT
            )

            response.raise_for_status()

            response.encoding = "utf-8"

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )
            books = soup.find_all(
                "article",
                class_="product_pod"
            )

            page_products = []

            for book in books:

                # --------------------------
                # TITLE
                # --------------------------

                title_element = book.find("h3")

                if not title_element:
                    continue

                title_link = title_element.find("a")

                if not title_link:
                    continue

                name = title_link.get("title")

                if not name:
                    continue


                    # --------------------------
                # URL
                # --------------------------

                href = title_link.get("href")

                if not href:
                    continue

                full_url = urljoin(
                    url,
                    href
                )


                # --------------------------
                # PRICE
                # --------------------------

                price_element = book.find(
                    "p",
                    class_="price_color"
                )

                if not price_element:
                    continue

                price_text = price_element.get_text(strip=True)

                price_text = (
                    price_text
                    .replace("£", "")
                    .replace("Â", "")
                    .strip()
                )

                price = float(price_text)

                # --------------------------
                # AVAILABILITY
                # --------------------------

                availability_element = book.find(
                    "p",
                    class_="instock availability"
                )

                if availability_element:

                    availability = (
                        availability_element
                        .get_text(strip=True)
                    )

                else:

                    availability = "Unknown"


                    # --------------------------
                # PRODUCT
                # --------------------------

                product = {
                    "name": name,
                    "price": price,
                    "url": full_url,
                    "availability": availability
                }

                page_products.append(product)


            logger.info(
                f"Success: {url} | "
                f"Products: {len(page_products)}"
            )

            return {
                "url": url,
                "products": page_products,
                "success": True
            }


        except requests.RequestException as error:

            logger.warning(
                f"Error: {url} | "
                f"Attempt: {attempt}/{MAX_RETRIES} | "
                f"{error}"
            )

            if attempt < MAX_RETRIES:

                time.sleep(
                    2 ** (attempt - 1)
                )


    logger.error(
        f"FAILED: {url}"
    )

    return {
        "url": url,
        "products": [],
        "success": False
    }


# ==========================================
# CONCURRENT SCRAPING
# ==========================================

scraping_start = time.time()

with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
) as executor:

    results = list(
        executor.map(
            fetch_page,
            urls
        )
    )


scraping_time = time.time() - scraping_start


# ==========================================
# MERGE RESULTS
# ==========================================

products = []

failed_urls = []

successful_pages = 0


for result in results:

    if result["success"]:

        successful_pages += 1

        products.extend(
            result["products"]
        )

    else:

        failed_urls.append(
            result["url"]
        )


    # ==========================================
# SCRAPING REPORT
# ==========================================

print(
    f"Successful pages: {successful_pages}"
)

print(
    f"Failed pages: {len(failed_urls)}"
)

print(
    f"Total products: {len(products)}"
)

print(
    f"Scraping time: {scraping_time:.2f} seconds"
)


logger.info(
    f"Successful pages: {successful_pages}"
)

logger.info(
    f"Failed pages: {len(failed_urls)}"
)

logger.info(
    f"Total products: {len(products)}"
)


if failed_urls:

    print("\nFailed URLs:")

    for failed_url in failed_urls:

        print(failed_url)

        logger.error(
            f"Failed URL: {failed_url}"
        )


    # ==========================================
# DATAFRAME
# ==========================================

df = pd.DataFrame(products)
df.insert(0,"id", range(1,len(df)+1))

print("\nDataFrame:")

print(df.head())


print(
    f"\nDataFrame rows: {len(df)}"
)


# ==========================================
# DATA VALIDATION
# ==========================================

if df.empty:

    logger.error(
        "DataFrame is empty!"
    )

    raise RuntimeError(
        "No products were scraped."
    )


if len(df) != 1000:

    logger.warning(
        f"Expected 1000 products, "
        f"got {len(df)}"
    )


# ==========================================
# REMOVE DUPLICATES
# ==========================================

before_duplicates = len(df)

df = df.drop_duplicates(
    subset=["url"]
)

after_duplicates = len(df)

print(
    f"Duplicates removed: "
    f"{before_duplicates - after_duplicates}"
)


# ==========================================
# EXCEL
# ==========================================

df.to_excel(
    "products.xlsx",
    index=False
)


# ==========================================
# CSV
# ==========================================

df.to_csv(
    "products.csv",
    index=False
)


# ==========================================
# JSON
# ==========================================

df.to_json(
    "products.json",
    orient="records",
    indent=4,
    force_ascii=False
)


save_products(df)

# ==========================================
# FINAL REPORT
# ==========================================

total_time = (
        time.time() - START_TIME
)


logger.info(
    "Excel file created"
)

logger.info(
    "CSV file created"
)

logger.info(
    "JSON file created"
)

logger.info(
    "SQLite database created"
)

logger.info(
    f"Total time: {total_time:.2f} seconds"
)


print("\n================================")
print("SCRAPING COMPLETED")
print("================================")

print(
    f"Products: {len(df)}"
)

print(
    f"Pages successful: {successful_pages}"
)

print(
    f"Pages failed: {len(failed_urls)}"
)

print(
    f"Total time: {total_time:.2f} seconds"
)

print(
    "Files created:"
)
print(
    "  products.xlsx"
)
print(
    "  products.csv"
)
print(
    "  products.json"
)
print(
    "  books.db"
)
print(
    "  scraper.log"
)