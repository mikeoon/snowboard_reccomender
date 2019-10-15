import psycopg2
from collections import defaultdict
import requests
from bs4 import BeautifulSoup


def _scrape_product(evo_url):
	
	r = requests.get(evo_url)
	soup = BeautifulSoup(r.content, "lxml")
	new_snwb = dict()
	snwb_sizes = defaultdict(dict)

	print(f'Status for current page: {r}\n')

	# find name of product
	product_name = soup.find(id='buy-grid').find('h1', {'class': 'pdp-header-title'})
	new_snwb['name'] = product_name.string.strip()
	
	new_snwb['id'] = snwb_id = soup.find('span', {'class' : 'pdp-header-util-sku'}).string[4:].strip()
	
	product_detail = soup.find('div', {'class':'mobile-accordion-group'})

	# gets from the Product Detail tabel
	product_rows = product_detail.find_all('div', {'class':'pdp-feature'})


	for i in product_rows:
		#product detail name
		p_detail = i.find('h5').string.lower().replace(' ', '_')
		if p_detail == 'flex':
			p_data = int(i.find('p').find('em').string[:2].strip())
		# product detail info
		else:
			p_data = i.find('p').find('em').string
		new_snwb[p_detail] = p_data

	# Gets from the Specs tabel
	product_specs = product_detail.find('ul', {'class':'pdp-spec-list'})
	product_specs_rows = product_specs.find_all('li')


	for i in product_specs_rows:
		# spec name
		p_detail = i.find('span', {'class': 'pdp-spec-list-title'}).find('strong').string[:-1].lower().replace(' ', '_').replace('/', '_')
		# spec info
		p_data = i.find('span',{'class':'pdp-spec-list-description'}).string
		new_snwb[p_detail] = p_data

	# Gets the different size info
	product_mments = product_detail.find('table', {'class':'spec-table table'})
	product_sizes = product_mments.find('thead')

	# Creates the sizes table for each snowboard
	# Scrapes the sizes and makes unique ID from the snowboard ID (product ID) + size
	for i in product_sizes.find_all('td'):
		snwb_sizes[snwb_id+i.string]['size'] = i.string
		snwb_sizes[snwb_id+i.string]['snwb_id'] = snwb_id

	product_mments_details = product_mments.find('tbody').find_all('tr')
	attributes = [tr.find_all('td') for tr in product_mments_details]

	# Matches the scraped values with the proper parameter names
	for i,j in zip(product_mments_details, attributes):
		# name of mesurement
		param = i.find('th').string.lower().replace(' ', '_').replace('(', '').replace(')', '')
		# Matches the unique size IDs with the data
		for k, d in zip(snwb_sizes.keys(),j):
			if param in ['rider_weight_lbs', 'width']:
				snwb_sizes[k][param] = d.string
			else:
				snwb_sizes[k][param] = float(d.string)

	# final two dictionaries, printed for now but should insert method to get into postgresSQL
	print(snwb_sizes)
	print(new_snwb)

	print(f'Done with snowboard id: {snwb_id}')


def _create_postgres():
	conn = psycopg2.connect(dbname='postgres', user='postgres', host='localhost')
	cur = conn.cursor()



def _scrape_snwb_urls():
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


_scrape_product('https://www.evo.com/snowboards/capita-spring-break-slush-slasher-snowboard#image=161992/642522/capita-spring-break-slush-slasher-snowboard-2020-.jpg')


