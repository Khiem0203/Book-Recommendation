from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import time
import re
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

BASE_URL = "https://www.fahasa.com/sach-trong-nuoc.html?order=created_at&limit=24&p={}"
DOMAIN = "https://www.fahasa.com"

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")

thread_local = threading.local()
csv_lock = threading.Lock()  # Đảm bảo ghi file an toàn

def get_thread_driver():
    if not hasattr(thread_local, "driver"):
        thread_local.driver = webdriver.Chrome(options=options)
    return thread_local.driver

def clean(text):
    return re.sub(r"\s+", " ", text.strip())

def extract_genre_from_breadcrumb(soup):
    breadcrumb = soup.select("ol.breadcrumb li a")
    genres = []
    for a in breadcrumb:
        if a.get_text(strip=True).lower() != "trang chủ":
            full_text = a.get("title") or a.get("aria-label") or a.get_text(strip=True)
            genres.append(full_text)
    return genres[-1] if genres else ""

def get_book_details(product_url):
    try:
        driver = get_thread_driver()
        driver.get(product_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#product_tabs_description_contents"))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")

        title_tag = soup.find("meta", property="og:title")
        title = title_tag["content"].strip() if title_tag else ""

        thumbnail_tag = soup.find("meta", property="og:image")
        thumbnail = thumbnail_tag["content"].strip() if thumbnail_tag else ""

        link_tag = soup.find("meta", property="og:url")
        link = link_tag["content"].strip() if link_tag else product_url

        desc_div = soup.select_one("div#product_tabs_description_contents")
        description = desc_div.get_text(separator="\n").strip() if desc_div else ""

        genre = extract_genre_from_breadcrumb(soup)
        categories = [genre] if genre else []

        author = publisher = publishing_year = num_pages = language = ""
        rows = soup.select("table.data-table tr")
        for row in rows:
            th = row.select_one("th.table-label")
            td = row.select_one("td .attribute_link_container")
            if th and td:
                label = th.get_text(strip=True).lower()
                value = td.get_text(strip=True)
                if "tác giả" in label:
                    author = value
                elif "nhà xuất bản" in label or "nhà cung cấp" in label:
                    publisher = value
                elif "năm xuất bản" in label or "năm xb" in label:
                    publishing_year = value
                elif "số trang" in label:
                    num_pages = value
                elif "ngôn ngữ" in label:
                    language = value

        return {
            "title": title,
            "description": description,
            "thumbnail": thumbnail,
            "author": author,
            "publisher": publisher,
            "publishing_year": publishing_year,
            "num_pages": num_pages,
            "language": language,
            "categories": " / ".join(categories),
            "link": link
        }
    except Exception as e:
        print(f"Error in get_book_details for {product_url}: {e}")
        return None

def scrape_all_products(start_page=1, end_page=200):
    links = []
    driver_main = webdriver.Chrome(options=options)
    for page in range(start_page, end_page + 1):
        driver_main.get(BASE_URL.format(page))
        driver_main.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        try:
            WebDriverWait(driver_main, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.item-inner"))
            )
        except:
            print(f"Timeout waiting for products on page {page}")
            continue
        soup = BeautifulSoup(driver_main.page_source, "html.parser")
        products = soup.select("div.item-inner")
        print(f"Page {page} - Found {len(products)} products")
        for product in products:
            link_tag = product.select_one("a.product-image")
            if not link_tag or not link_tag.get("href"):
                continue
            product_url = urljoin(DOMAIN, link_tag["href"])
            links.append(product_url)
    driver_main.quit()

    fieldnames = [
        "title", "description", "thumbnail", "author", "publisher",
        "publishing_year", "num_pages", "language", "categories", "link"
    ]

    with open("new/vi/fahasa_vi6.csv", mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

    def task(link, idx, total):
        print(f"[{idx}/{total}] Fetching: {link}")
        data = get_book_details(link)
        if data:
            with csv_lock:
                with open("new/vi/fahasa_vi6.csv", mode="a", encoding="utf-8-sig", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writerow(data)
        return data

    with ThreadPoolExecutor(max_workers=6) as executor:
        total = len(links)
        futures = {
            executor.submit(task, link, i + 1, total): link
            for i, link in enumerate(links)
        }
        for _ in as_completed(futures):
            pass

if __name__ == "__main__":
    scrape_all_products(start_page=171, end_page=271)
    print("Done")
