import time
import json
from pyfiglet import figlet_format
import os
from datetime import datetime, timedelta
import modules.adafruit as ada
import modules.pishopus as ps
from alert import restockAlert

"""
TO DO
    1. add log for request errors
    2. proxy support (needs to be done before multithreading)
    3. concurrency for multiple pid support
    4. determine optimal request headers

    5. write monitors for the following sites
        sparkfun.com
        canakit.com
        shopify sites
            shop.pimoroni.com
            chicagodist.com
            vilros.com
            
    automate purchase (single account) (selenium or requests, not sure yet)
"""
def getModules():
    """
    Gets and returns all file names from modules folder
    """
    modules = []
    for file in os.listdir('modules'):
        if file.endswith('.py'):
            modules.append(file[0:file.find('.')])
    return modules

def selectModule(modules):
    """
    Prompts user to select a module,
    returns module name and import
    """
    while True:
        try:
            selectedModuleIndex = int(input("SELECT SITE:\n" + '\n'.join([str(i + 1) + ": " + x.upper() for i, x in enumerate(modules)]) + "\n")) - 1
            if selectedModuleIndex not in range(len(modules)):
                raise ValueError
            selectedModuleName = modules[selectedModuleIndex]
            # assign monitor variable to selected monitor's import
            if selectedModuleIndex == 0: module = ada 
            elif selectedModuleIndex == 1: module = ps
            return selectedModuleName, module
        except (ValueError, IndexError):
            print("Please enter a valid module number.")

def selectDelay():
    """
    Prompts user to enter a delay in ms (time.sleep to prevent rate limiting),
    returns delay in seconds 
    """
    while True:
        try:
            delay = int(input("ENTER DELAY (ms):\n")) / 1000
            if (delay > 60) or (delay < 0): raise OverflowError
            return delay
        except (ValueError):
            print("Please enter a valid delay.")
        except (OverflowError):
            print("Your delay must be between 0 and 60,000 ms.")

def getProducts():
    """
    Gets and returns up-to-date products.json file contents,
    including updated lastRestock times and added product id / titles
    """
    f = open('products.json')
    products = json.load(f)
    f.close()
    return products

def updateProdAttributes(moduleName, product, attrs):
    """
    Updates attributes to given values for a single product in products.json
    """
    try:
        with open('products.json', 'r') as f:
            data = json.load(f)
        for attr, val in attrs.items():
            if attr not in data[moduleName][product]:
                raise ValueError
            data[moduleName][product][attr] = str(val)
        with open('products.json', 'w') as f:
            json.dump(data, f, indent=4)
    except:
        print(f"Invalid attribute '{attr}' for product '{product}' in module '{moduleName}'")
        
def startMonitor():
    """
    Initializes monitor
    """
    print(figlet_format('Welcome to PInventory', font='avatar'), """\033[1;32;40m
   .~~.   .~~.
  '. \ ' ' / .'\033[0m\033[1;31;40m
   .~ .~~~..~.
  : .~.'~'.~. :
 ~ (   ) (   ) ~
( : '~'.~.'~' : )
 ~ .~ (   ) ~. ~
  (  : '~' :  ) 
   '~ .~~~. ~'\033[0m
   """)

    modules = getModules()
    moduleName, module = selectModule(modules=modules)
    delay = selectDelay()
    print(f"\nSTARTING {moduleName.upper()} MONITOR, {delay} SECOND DELAY\n--------------------------------------------")

    # start of monitor
    while True:
        products = getProducts()
        # sucky support for multiple pids (for now)
        for product, prodInfo in products[moduleName].items(): # split into key and value. key is used to update products.json, val is used for functionality everywhere else
            # require product to have an id attribute
            if prodInfo["id"]:
                res = module.checkPage(id=prodInfo["id"]) # runs checkPage function for selected monitor
                res['url'] = prodInfo["prodPage"] if res['url'] == None else res['url']
                res['title'] = prodInfo["title"] if res['title'] == None else res['title']
                if res['response_code'] // 100 < 4: # continue checking response if response code from checkPage wasn't an error
                    if res['instock'] is True: # instock status returned true from checkpage if a restock is found
                        # check timestamp to prevent pinging the same restock multiple times
                        try: # tries to convert current product's lastRestock attribute to a datetime obj
                            last_restock = datetime.strptime(prodInfo['lastRestock'], "%Y-%m-%d %H:%M:%S.%f")
                        except:
                            last_restock = datetime.strptime("2002-01-23 12:00:00.000000", "%Y-%m-%d %H:%M:%S.%f") # temporarily sets last_restock equal to an unimportant date that definitely isn't my birthday
                        if (res['timestamp'] - last_restock) > timedelta(minutes=10):
                            # print restock and send discord webhook
                            restockAlert(res['url'], res['title'], res['stock'], res['price'], res['method'], res['timestamp'])
                            # writes restock timestamp to products.json file
                            updateProdAttributes(moduleName=moduleName, product=product, attrs={'lastRestock': res['timestamp']})
                        else:
                            print(f"[{res['timestamp']}] {res['title']} is in stock, restock began at {last_restock.strftime('%Y-%m-%d %H:%M:%S')}. Refreshing...")
                    else: # print that product isn't in stock if instock status is returned false
                        print(f"[{res['timestamp']}] {res['title']} is not in stock. Refreshing...")
                else:
                    print(f"[{res['timestamp']}] Error checking {res['title']}, {res['response_code']} error. Refreshing...")
            elif ("prodPage" in prodInfo) and (prodInfo["prodPage"]): # if prodPage exists but id doesn't use getProdInfo function to request endpoint and return product id (only used for pishop.us at the moment)
                res = module.getProdInfo(prodInfo["prodPage"])
                if (res['response_code'] // 100 < 4) and (res['title'] != None) and (res['id'] != None):
                    updateProdAttributes(moduleName=moduleName, product=product, attrs={'id': res['id'], 'title': res['title']})
                    print(f"[{datetime.utcnow()}] Successfully retrieved and stored the product id for {res['title']}")
                else:
                    print(f"[{datetime.utcnow()}] Error retrieving product id from {prodInfo['prodPage']}, {res['response_code']} error. Refreshing...")
            else:
                continue # doesn't perform time.sleep(delay) if nothing is done with invalid products.json entry
            time.sleep(delay) # delay to prevent rate limiting

startMonitor()