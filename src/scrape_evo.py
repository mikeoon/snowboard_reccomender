import copy
import pandas as pd
from pymongo import MongoClient
import pprint


# Requests sends and recieves HTTP requests.
import requests

# Beautiful Soup parses HTML documents in python.
from bs4 import BeautifulSoup


def scrape_product(evo_url):
	#evo_url = 'https://www.evo.com/snowboards/capita-spring-break-slush-slasher-snowboard#image=161992/642522/capita-spring-break-slush-slasher-snowboard-2020-.jpg'
	#vo_url = 'https://www.evo.com/snowboards/jones-mountain-twin-snowboard#image=161602/640791/clone.jpg'
	r = requests.get(evo_url)


	soup = BeautifulSoup(r.content, "lxml")

	# find name of product
	product_name = soup.find(id='buy-grid').find('h1', {'class': 'pdp-header-title'})
	print(product_name.string)


	product_detail = soup.find('div', {'class':'mobile-accordion-group'})

	# gets from the Product Detail tabel
	product_rows = product_detail.find_all('div', {'class':'pdp-feature'})


	for i in product_rows:
		#product detail name
		print(i.find('h5').string)
		# product detail info
		print(i.find('p').find('em').string)

	# Gets from the Specs tabel
	product_specs = product_detail.find('ul', {'class':'pdp-spec-list'})
	product_specs_rows = product_specs.find_all('li')


	for i in product_specs_rows:
		# spec name
		print(i.find('span', {'class': 'pdp-spec-list-title'}).find('strong').string)
		# spec info
		print(i.find('span',{'class':'pdp-spec-list-description'}).string)


	product_mments = product_detail.find('table', {'class':'spec-table table'})
	product_sizes = product_mments.find('thead')
	size_title = product_sizes.find('th').string

	# Gets the size title
	print(size_title)

	for i in product_sizes.find_all('td'):
		# The different sizes, each index is corresponds to the values below at the same index
		print(i.string)

	product_mments_details = product_mments.find('tbody').find_all('tr')
	attributes = [tr.find_all('td') for tr in product_mments_details]


	for i,j in zip(product_mments_details,attributes):
		# name of mesurement
		print(i.find('th').string)
		# measurements indexed by sizes above, same order
		print([a.string for a in j])



def scrape_snwb_urls():
	pages = ['', '/p_2', '/p_3']
	evo_snwb_urls = []
	for p in pages:
		evo_url = f'https://www.evo.com/shop/snowboard/snowboards{p}/rpp_400'
		r = requests.get(evo_url)
		soup = BeautifulSoup(r.content, "lxml")

		snowboards = soup.find_all('div', {'class':'product-thumb js-product-thumb'})

		for s in snowboards:
			attach = s.find('a', {'class': 'product-thumb-link js-product-thumb-details-link'})['href']
			evo_snwb_urls.append(f'https://www.evo.com{attach}')
	return evo_snwb_urls





