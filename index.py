import time
import json
from pyfiglet import figlet_format
import modules.adafruit as ada
import modules.pishopus as ps
import os

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

    # get products from json file
    f = open('products.json')
    products = json.load(f)
    f.close()

    # get all modules
    monitors = []
    for file in os.listdir('modules'):
        if file.endswith('.py'):
            monitors.append(file[0:file.find('.')])
    # user selects module
    selected_monitor = int(input("SELECT MONITOR:\n" + '\n'.join([str(i + 1) + ": " + x.upper() for i, x in enumerate(monitors)]) + "\n"))
    print(f"\n{monitors[selected_monitor-1].upper()} MONITOR SELECTED")
    delay = int(input("ENTER DELAY (ms):\n"))/1000
    if selected_monitor == 1:
        while True:
            for product in products: # sucky support for multiple pids (for now)
                if products[product]["adafruit"]["pid"]: # only check when product exists for site
                    ada.checkPage(products[product]["adafruit"]["pid"])
                    # delay to prevent rate limiting
                    time.sleep(delay)
    elif selected_monitor == 2:
        while True:
            for product in products:
                if products[product]["pishop"]["url"]: # only check when product exists for site
                    ps.checkPage(products[product]["pishop"]["url"])
                    # delay to prevent rate limiting
                    time.sleep(delay)

startMonitor()