from datetime import datetime
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

def discord_webhook(title, url, stock, timestamp):
    webhook = os.getenv("WEBHOOK")
    data = {
        "username": 'PInventory Monitor',
        "avatar_url": 'https://cdn-icons-png.flaticon.com/512/2718/2718539.png',
        "embeds": [{
            "title": f"{url.split('.')[1].upper()} RESTOCK: {title}",
            "url": url, 
            "fields": [{"name": "Stock:", "value": stock, "inline": True}],
            "footer": {"text": "GitHub: btpxii"},
            "timestamp": str(timestamp),
        }]
    }

    result = requests.post(webhook, data=json.dumps(data), headers={"Content-Type": "application/json"})
    if result.status_code == 204:
        print(f"[{datetime.utcnow()}] Webhook sent")
    else:
        print(f"[{datetime.utcnow()}] Webhook failed")

def restockAlert(url, title, stock, method, timestamp):
    # Send restock details to user's Discord server
    discord_webhook(title, url, stock, timestamp)
    # Write details of restock to the console
    print(f"[{timestamp}] Restock @ {url}, found using \"{method}\" method")