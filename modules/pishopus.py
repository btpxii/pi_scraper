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

# Save incase API method gets blocked, frontend method (not entirely up to date)
# def checkPage(endpoint):
#     # request the given url, record the timestamp that the request is returned
#     url = f"https://www.pishop.us/product/{endpoint}"
#     res = requests.get(url)
#     timestamp = datetime.utcnow()
#     if res.status_code == 200:
#         page = BeautifulSoup(res.text, 'html.parser')
#         prodTitle = page.find('h1', class_='productView-title').text.strip()
#         price = page.find('div', class_='productView-price').find('span', class_='price--withoutTax').text.strip()
#         # find script tag with BCData variable
#         scripts = page.find_all('script', type="text/javascript")
#         for script in scripts:
#             if "BCData" in script.text:
#                 data = script.text
#                 break
#         match = re.search(r'var BCData = (.+);', data)
#         if match:
#             data = json.loads(match.group(1))
#             # look in BCData variable for instock attribute True
#             if data['product_attributes']['instock'] == True:
#                 stock = data['product_attributes']['stock']
#                 return {'url': url, 'title': prodTitle, 'stock': stock, 'price': price, 'timestamp': timestamp, 'method': 'BCData instock is True'}
#             else: # if no BCData, return that the product is out of stock
#                 print(f"[{timestamp}] {prodTitle} is not in stock. Refreshing...")
#     else:
#         print(f"[{timestamp}] Error getting page, response status code {res.status_code}")