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
    delay = int(input("ENTER DELAY (ms):\n"))/1000 # user enters delay in milliseconds, converted to seconds for time.sleep
    print(f"\nSTARTING {monitors[selected_monitor-1].upper()} MONITOR, {delay} SECOND DELAY\n--------------------------------------------")
    # assign monitor variable to selected monitor's import
    if selected_monitor == 1: monitor = ada 
    elif selected_monitor == 2: monitor = ps
    while True: # start of monitor
        for product in products: # sucky support for multiple pids (for now)
            if products[product][monitors[selected_monitor-1]]["endpoint"]: # only check when product exists for site
                monitor.checkPage(products[product][monitors[selected_monitor-1]]["endpoint"]) # runs checkPage function for selected monitor
                time.sleep(delay) # delay to prevent rate limiting

startMonitor()