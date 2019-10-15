import psycopg2
from collections import defaultdict
import requests
import re
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

	p_order = ['name', 'id']

	for i in product_rows:
		#product detail name
		p_detail = i.find('h5').string.lower().replace(' ', '_')
		if p_detail == 'flex':
			p_data = int(i.find('p').find('em').string[:2].strip())
		elif p_detail == 'rocker_type':
			p_data = (re.sub(r'[^\x00-\x7F]+',' ', i.find('p').find('em').string) + ' - ' + i.find('span').string).lower()
		# product detail info
		else:
			#p_data = i.find('p').find('em').string.replace(u"\u2122", '')
			p_data = re.sub(r'[^\x00-\x7F]+',' ', i.find('p').find('em').string).lower()
		new_snwb[p_detail] = p_data
		p_order.append(p_detail)

	# Gets from the Specs tabel
	product_specs = product_detail.find('ul', {'class':'pdp-spec-list'})
	product_specs_rows = product_specs.find_all('li')


	for i in product_specs_rows:
		# spec name
		p_detail = i.find('span', {'class': 'pdp-spec-list-title'}).find('strong').string[:-1].lower().replace(' ', '_').replace('/', '_')
		if p_detail == 'rocker_type':
			p_detail = p_detail+'_s'
		# spec info
		p_data = re.sub(r'[^\x00-\x7F]+',' ',i.find('span',{'class':'pdp-spec-list-description'}).string).lower()
		new_snwb[p_detail] = p_data
		p_order.append(p_detail)

	# Gets the different size info
	product_mments = product_detail.find('table', {'class':'spec-table table'})
	product_sizes = product_mments.find('thead')

	# Creates the sizes table for each snowboard
	# Scrapes the sizes and makes unique ID from the snowboard ID (product ID) + size
	size_order = []
	for i in product_sizes.find_all('td'):
		snwb_sizes[snwb_id+i.string]['size'] = i.string
		snwb_sizes[snwb_id+i.string]['snwb_id'] = snwb_id
		size_order.append(snwb_id+i.string)

	product_mments_details = product_mments.find('tbody').find_all('tr')
	attributes = [tr.find_all('td') for tr in product_mments_details]

	size_spec_order = []
	# Matches the scraped values with the proper parameter names
	for i,j in zip(product_mments_details, attributes):
		# name of mesurement
		param = i.find('th').string.lower().replace(' ', '_').replace('(', '').replace(')', '')
		# Matches the unique size IDs with the data
		for k, d in zip(size_order,j):
			if param in ['rider_weight_lbs', 'width']:
				snwb_sizes[k][param] = d.string
			else:
				snwb_sizes[k][param] = float(d.string)
		size_spec_order.append(param)

	# final two dictionaries, printed for now but should insert method to get into postgresSQL
	#print(snwb_sizes)
	#print(new_snwb)
	
	for k,v in new_snwb.items():
		print(f'KEY: {k}  VALUE: {v}')

	#print()

	#for k,v in snwb_sizes.items():
		#print(f'KEY: {k}  VALUE: {v}')

	for p in p_order:
		print(p+',')

	#print(size_order)
	#print(size_spec_order)

	#_insertp_postgres(p_order, new_snwb)

	print(f'Done with snowboard id: {snwb_id}')


def _insertp_postgres(p_order, p_data):
	sql = ''' INSERT INTO snowboards(name,
								id,
								rocker_type,
								flex,
								shape,
								core,
								laminates,
								sidewalls,
								base,
								edges,
								topsheet,
								graphics,
								additional_features,
								binding_compatibility,
								terrain,
								ability_level,
								rocker_type_s,
								shape,
								flex_rating,
								binding_mount_pattern,
								core_laminates,
								warranty)
			VALUES(%s);


		'''


	conn = psycopg2.connect(dbname='snowboardcollect', user='postgres', host='localhost')
	cur = conn.cursor()
	value = tuple(p_data[i] for i in p_order)
	cur.execute(sql, (value,))





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


