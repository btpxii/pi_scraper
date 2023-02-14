import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime
import json
import re
from alert import restockAlert

def checkPage(url):
    # request the given url, record the timestamp that the request is returned
    res = requests.get(url)
    timestamp = datetime.utcnow()
    if res.status_code == 200:
        page = BeautifulSoup(res.text, 'html.parser')
        prodTitle = page.find('h1', class_='productView-title').text.strip()
        # find script tag with BCData variable
        scripts = page.find_all('script', type="text/javascript")
        for script in scripts:
            if "BCData" in script.text:
                data = script.text
                break
        match = re.search(r'var BCData = (.+);', data)
        if match:
            data = json.loads(match.group(1))
            # look in BCData variable for instock attribute True
            if data['product_attributes']['instock'] == True:
                stock = data['product_attributes']['stock']
                restockAlert(url, prodTitle, stock, 'BCData instock is True', timestamp)
                time.sleep(30)
            else: # if no BCData, return that the product is out of stock
                print(f"[{timestamp}] {prodTitle} is not in stock. Refreshing...")
    else:
        print(f"[{timestamp}] Error getting page, response status code {res.status_code}")