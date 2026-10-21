
import requests
from bs4 import BeautifulSoup
import csv
import json
import time
from pathlib import Path

BASE_URL = "https://books.toscrape.com/catalogue/"
START_URL = "https://books.toscrape.com/catalogue/page-1.html"
OUTPUT_DIR = Path("data")
MAX_PAGES = 5  # Start safely with 5 pages


def fetch_page(session, url, retries=3):
    """Download a page with retry handling."""
    for attempt in range(retries):
        try:
            response = session.get(url, timeout=15)
            response.raise_for_status()
            return response.text
        except requests.RequestException as error:
            print(f"Attempt {attempt + 1}/{retries} failed: {error}")
            if attempt < retries - 1:
                time.sleep(2)

    return None


def scrape_books():
    books = []
    seen_titles = set()
    next_url = START_URL

    with requests.Session() as session:
        session.headers.update({
            "User-Agent": "StudentLearningScraper/1.0"
        })

        for page_number in range(1, MAX_PAGES + 1):
            print(f"Scraping page {page_number}...")

            html = fetch_page(session, next_url)
            if html is None:
                print("Stopping because the page could not be downloaded.")
                break

            soup = BeautifulSoup(html, "html.parser")
            page_books = soup.select("article.product_pod")

            if not page_books:
                print("No books found. Stopping.")
                break

            for book in page_books:
                title_tag = book.select_one("h3 a")
                price_tag = book.select_one(".price_color")
                rating_tag = book.select_one("p.star-rating")

                if not title_tag or not price_tag:
                    continue

                title = title_tag.get("title", title_tag.get_text(strip=True))

                if title in seen_titles:
                    continue

                seen_titles.add(title)

                rating_classes = (
                    rating_tag.get("class", [])
                    if rating_tag else []
                )
                rating = next(
                    (item for item in rating_classes if item != "star-rating"),
                    "Unknown"
                )

                books.append({
                    "title": title,
                    "price": price_tag.get_text(strip=True),
                    "rating": rating,
                    "page": page_number
                })

            next_link = soup.select_one("li.next a")
            if not next_link:
                print("No next page found.")
                break

            next_url = BASE_URL + next_link["href"]
            time.sleep(1)

    return books


def save_data(books):
    if not books:
        print("No data to save.")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_DIR / "books.json", "w", encoding="utf-8") as file:
        json.dump(books, file, indent=4, ensure_ascii=False)

    with open(
        OUTPUT_DIR / "books.csv",
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=books[0].keys())
        writer.writeheader()
        writer.writerows(books)

    print(f"\nTotal unique books: {len(books)}")
    print(f"CSV: {OUTPUT_DIR / 'books.csv'}")
    print(f"JSON: {OUTPUT_DIR / 'books.json'}")


if __name__ == "__main__":
    records = scrape_books()
    save_data(records)
