import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime
import json
from pyfiglet import figlet_format

"""
TO DO
    multi-pid support
    proxy support
    use Twitter api to post when product restocks
    automate purchase (single account)
"""
def checkPage(pid):
    # request the given pid, record the timestamp that the request is returned
    res = requests.get(f"https://www.adafruit.com/product/{pid}")
    timestamp = datetime.utcnow()
    page = BeautifulSoup(res.text, 'html.parser')
    # initially set oos to True, change if checks below find product is in stock
    outOfStock = True
    # first check - look for form with class add_to_cart_form on page, return if found
    atc_form = page.find('form', class_='add_to_cart_form')
    if atc_form:
        print(f"[{timestamp}] ATC button found")
        getStock(page, timestamp)
        outOfStock = False
    else:
        # second check - look in structured date script tag for InStock availability status
        app_script = json.loads(page.findAll('script', {'type': 'application/ld+json'})[1].text)
        availability = app_script['offers']['availability']
        if "InStock" in availability:
            print(f"[{timestamp}] InStock status found")
            getStock(page, timestamp)
            outOfStock = False
        else: # if all checks fail, return that the product is out of stock
            print(f"[{timestamp}] Not in stock. Refreshing...")

    return outOfStock, timestamp

# get stock from page once product is found to be in stock
def getStock(page, timestamp):
    stock = page.find('div', class_='mobile-text-margins top-ten').text.strip()
    if stock == "In stock": # based on the currently in-stock products, I assume that adafruit displays "In Stock" instead of a number when they have 100+ items in inventory
        print(f"[{timestamp}] Units available: 100+")
    else:
        print(f"[{timestamp}] Units available: {stock.split()[0]}")


def startMonitor(pid, delay):
    print(figlet_format('Welcome to pi-scraper', font='avatar'))
    print("""\033[1;32;40m
   .~~.   .~~.
  '. \ ' ' / .'

   \033[0m
   \033[1;31;40m
   .~ .~~~..~.
  : .~.'~'.~. :
 ~ (   ) (   ) ~
( : '~'.~.'~' : )
 ~ .~ (   ) ~. ~
  (  : '~' :  ) 
   '~ .~~~. ~'
   \033[0m
   """)
    # initially sets outOfStock to True, calls checkPage function to check item page stock status until item is found to be in stock
    outOfStock = True
    while outOfStock:
        outOfStock, timestamp = checkPage(pid)
        # delay to prevent rate limiting
        time.sleep(delay)

pids = {
    '4B 1GB': '4295',
    '4B 2GB': '4292',
    '4B 4GB': '4296',
    '4B 8GB': '4564',
    'Zero WH': '3708',
    'Zero W': '3400',
    'Zero 2W': '5291'
}
startMonitor(pids['4B 8GB'], 5)