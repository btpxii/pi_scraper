import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime
import json
from pyfiglet import figlet_format
from alert import restockAlert

"""
TO DO
    multi-pid support
    proxy support
    use Twitter api to post when product restocks
    automate purchase (single account)
"""
def checkPage(pid):
    # request the given pid, record the timestamp that the request is returned
    url = f"https://www.adafruit.com/product/{pid}"
    res = requests.get(url)
    timestamp = datetime.utcnow()
    if res.status_code == 200:

        page = BeautifulSoup(res.text, 'html.parser')
        prodTitle = page.find('div', class_='mobile-product-header').find('h1').text.strip()
        # initially set oos to True, change if checks below find product is in stock
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
                print(f"[{timestamp}] {pid} is not in stock. Refreshing...")
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

def startMonitor(pid, delay):
    print(figlet_format('Welcome to PInventory', font='avatar'))
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
    while True:
        checkPage(pid)
        # delay to prevent rate limiting
        time.sleep(delay)


pids = {
    '4B 1GB': '4295',
    '4B 2GB': '4292',
    '4B 4GB': '4296',
    '4B 8GB': '4564',
    'Zero WH': '3708',
    'Zero W': '3400',
    'Zero 2W': '5291',
    'test': '5695'
}
startMonitor(pids['test'], 5)