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
    write recent restock time to products.json
    proxy support (needs to be done before multithreading)
    multithreaded multiple pid support (?)
    automate purchase (single account) (selinium or requests, not sure yet)
"""

def startMonitor():
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

    # get all modules
    monitors = []
    for file in os.listdir('modules'):
        if file.endswith('.py'):
            monitors.append(file[0:file.find('.')])
    # user selects module
    selected_monitor = int(input("SELECT MONITOR:\n" + '\n'.join([str(i + 1) + ": " + x.upper() for i, x in enumerate(monitors)]) + "\n"))
    delay = int(input("ENTER DELAY (ms):\n"))/1000 # user enters delay in milliseconds, converted to seconds for time.sleep
    print(f"\nSTARTING {monitors[selected_monitor-1].upper()} MONITOR, {delay} SECOND DELAY\n--------------------------------------------")
    # assign monitor variable to selected monitor's import
    if selected_monitor == 1: monitor = ada 
    elif selected_monitor == 2: monitor = ps
    while True: # start of monitor
        # get products from json file for each iteration through products list (updates lastRestock times)
        f = open('products.json')
        products = json.load(f)
        f.close()
        for product in products: # sucky support for multiple pids (for now)
            if products[product][monitors[selected_monitor-1]]["endpoint"]: # only check when product exists for site
                res = monitor.checkPage(products[product][monitors[selected_monitor-1]]["endpoint"]) # runs checkPage function for selected monitor
                if res: # data is returned from checkpage if a restock is found
                    # check timestamp to prevent pinging the same restock multiple times
                    try: # tries to convert current product's lastRestock attribute to a datetime obj
                        last_restock = datetime.strptime(products[product][monitors[selected_monitor-1]]['lastRestock'], "%Y-%m-%d %H:%M:%S.%f")
                    except:
                        last_restock = datetime.strptime("2002-01-23 12:00:00.000000", "%Y-%m-%d %H:%M:%S.%f") # temporarily sets last_restock equal to an unimportant date that definitely isn't my birthday
                    if (res['timestamp'] - last_restock) > timedelta(minutes=10):
                        # console log restock and send discord webhook
                        restockAlert(res['url'], res['title'], res['stock'], res['price'], res['method'], res['timestamp'])
                        # writes restock timestamp to products.json file
                        with open('products.json', 'r') as f:
                            data = json.load(f)
                        data[product][monitors[selected_monitor-1]]['lastRestock'] = str(res['timestamp'])
                        with open('products.json', 'w') as f:
                            json.dump(data, f)
                    else:
                        print(f"[{res['timestamp']}] {res['title']} is in stock, restock began at {last_restock.strftime('%Y-%m-%d %H:%M:%S')}. Refreshing...")
                time.sleep(delay) # delay to prevent rate limiting

startMonitor()