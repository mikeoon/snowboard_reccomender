import copy
import pandas as pd
from pymongo import MongoClient
import pprint


# Requests sends and recieves HTTP requests.
import requests

# Beautiful Soup parses HTML documents in python.
from bs4 import BeautifulSoup



evo_url = 'https://www.evo.com/snowboards/capita-spring-break-slush-slasher-snowboard#image=161992/642522/capita-spring-break-slush-slasher-snowboard-2020-.jpg'
r = requests.get(evo_url)


soup = BeautifulSoup(r.content, "lxml")

product_detail = soup.find('div', {'class':'mobile-accordion-group'})

product_rows = product_detail.find_all('div', {'class':'pdp-feature'})

for i in product_rows:
	print(i.find('h5'))
	print(i.find('p').find('em'))

















