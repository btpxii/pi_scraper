import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

def checkPage(endpoint):
    r_details = {'instock': False, 'response_code': None, 'url': f"https://www.adafruit.com/product/{endpoint}", 'title': None, 'stock': None, 'price': None, 'timestamp': None, 'method': None}
    # request the given endpoint, record the timestamp that the request is returned
    r = requests.get(r_details['url'])
    r_details['timestamp'] = datetime.utcnow()
    r_details['response_code'] = r.status_code
    if r.status_code == 200:
        page = BeautifulSoup(r.text, 'html.parser') # note that this line parsing with beautifulsoup takes a decent amount of time
        r_details['title'] = page.find('div', class_='mobile-product-header').find('h1').text.strip()
        r_details['price'] = page.find('div', class_='product-price').find('span').text.strip()
        # first check - look for form with class add_to_cart_form on page
        if page.find('form', class_='add_to_cart_form'):
            r_details['stock'] = getStock(page) # get stock from page
            # return product data to send out restock alert
            r_details['instock'] = True
            r_details['method'] = 'add-to-cart button enabled'
        else:
            # second check - look in structured date script tag for InStock availability status
            availability = json.loads(page.findAll('script', {'type': 'application/ld+json'})[1].text)['offers']['availability']
            if "InStock" in availability:
                r_details['stock'] = getStock(page) # get stock from page
                r_details['instock'] = True
                r_details['method'] = 'InStock status enabled'
    return r_details

# get stock from page once product is found to be in stock
def getStock(page):
    stock = page.find('div', class_='mobile-text-margins top-ten').text.strip()
    if stock == "In stock": # based on the currently in-stock products, I assume that adafruit displays "In Stock" instead of a number when they have 100+ items in inventory
        stock = "100+"
    else:
        stock = f"{stock.split()[0]}"
    return stock
