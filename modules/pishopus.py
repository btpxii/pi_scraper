import requests
from bs4 import BeautifulSoup
from datetime import datetime

def checkPage(id):
    r_details = {'instock': False, 'stock': None, 'price': None, 'method': None, 'response_code': None, 'url': None, 'title': None, 'timestamp': None}
    # request the given url, record the timestamp that the request is returned
    url = f"https://www.pishop.us/remote/v1/product-attributes/{id}"
    r = requests.get(url)
    r_details['timestamp'] = datetime.utcnow()
    r_details['response_code'] = r.status_code
    if r.status_code == 200:
        data = r.json()['data']
        r_details['price'] = data['price']['without_tax']['formatted']
        if data['instock']:
            r_details['stock'] = data['stock']
            r_details['instock'] = True
            r_details['method'] = 'pishop.us api'
    return r_details

def getProdInfo(prodPage):
    r_details = {'response_code': None, 'title': None, 'id': None}
    r = requests.get(prodPage)
    r_details['response_code'] = r.status_code
    if r.status_code == 200:
        page = BeautifulSoup(r.text, 'html.parser')
        details = page.find("div", class_="modal-body")
        r_details['title'] = details.find("h5", class_="product-title").text.strip()
        r_details['id'] = details.find("input", {"name":"product_id"})["value"]
    return r_details