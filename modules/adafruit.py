import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime
import json
from alert import restockAlert

def checkPage(pid):
    # request the given pid, record the timestamp that the request is returned
    url = f"https://www.adafruit.com/product/{pid}"
    res = requests.get(url)
    timestamp = datetime.utcnow()
    if res.status_code == 200:
        page = BeautifulSoup(res.text, 'html.parser')
        prodTitle = page.find('div', class_='mobile-product-header').find('h1').text.strip()
        # first check - look for form with class add_to_cart_form on page
        if page.find('form', class_='add_to_cart_form'):
            stock = getStock(page)
            restockAlert(url, prodTitle, stock, 'add-to-cart button enabled', timestamp)
            time.sleep(30)
        else:
            # second check - look in structured date script tag for InStock availability status
            availability = json.loads(page.findAll('script', {'type': 'application/ld+json'})[1].text)['offers']['availability']
            if "InStock" in availability:
                stock = getStock(page)
                restockAlert(url, prodTitle, stock, 'InStock status enabled', timestamp)
                time.sleep(30)
            else: # if all checks fail, return that the product is out of stock
                print(f"[{timestamp}] {prodTitle} is not in stock. Refreshing...")
    else:
        print(f"[{timestamp}] Error getting page, response status code {res.status_code}")

# get stock from page once product is found to be in stock
def getStock(page):
    stock = page.find('div', class_='mobile-text-margins top-ten').text.strip()
    if stock == "In stock": # based on the currently in-stock products, I assume that adafruit displays "In Stock" instead of a number when they have 100+ items in inventory
        stock = "100+"
    else:
        stock = f"{stock.split()[0]}"
    return stock
