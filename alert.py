import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

def discord_webhook(title, url, stock, price, timestamp, logger):
    webhook = os.getenv("WEBHOOK")
    data = {
        "username": 'PInventory Monitor',
        "avatar_url": 'https://cdn-icons-png.flaticon.com/512/2718/2718539.png',
        "embeds": [{
            "title": f"{url.split('.')[1].upper()} RESTOCK: {title}",
            "url": url, 
            "fields": [{"name": "Price", "value": price, "inline": True}, {"name": "Stock:", "value": stock, "inline": True}],
            "footer": {"text": f"GitHub: btpxii | [ {timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} UTC ]"},
        }]
    }

    result = requests.post(webhook, data=json.dumps(data), headers={"Content-Type": "application/json"})
    if result.status_code != 204:
        logger.error(msg=f"Webhook failed, status code {result.status_code}")

def restockAlert(url, title, stock, price, method, timestamp, logger):
    # Send restock details to user's Discord server
    discord_webhook(title, url, stock, price, timestamp, logger)
    # Log details of restock
    logger.info(f"Restock @ {url}, found using \"{method}\" method")