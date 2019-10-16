import requests
import re
import numpy as np
from bs4 import BeautifulSoup
import pandas as pd
from collections import defaultdict

def _scrape_resort_table(table_url):

	r = requests.get(table_url)
	soup = BeautifulSoup(r.content, "lxml")

	resort_table = soup.find(id='snowtable')

	resort_col_names = resort_table.find('tr').find_all('th')

	# Collects column names just once
	# Formats the names to lowecase, no spaces and '/'
	col_names = ['rank']
	for i in resort_col_names:
		if i.text != '' and i.text != ' ':
			if len(col_names) == 2:
				col_names.append('state')
			col_names.append(i.text.lower().replace(' ', '_').replace('w/', 'w').replace('&', 'and'))

	# fix some names of the columns, resort, zone, tota-snow_scorew_preservation
	col_names[1] = col_names[1][-6:]
	col_names[2] = col_names[2][-4:]
	col_names[4] = col_names[4][:-1]
	col_names[-1] = col_names[-1][:-7].replace('rew','re')


	# Finds all the rows in the resorts table
	resort_rows = resort_table.find('tbody').find_all('tr')

	# Cleans up each row into just the text aka data
	resort_data = []
	for r in resort_rows:
		row = []
		for i in r.text.split('\n'):
			data = i.lstrip().rstrip()
			if len(data) != 0:
				# if the snow data is NOT estimated, will put nan here
				if '--' in data:
					row.append(np.nan)
				else:
					row.append(data)
		resort_data.append(row)

	df_row = defaultdict(list)
	df_list = []
	for r in resort_data:
		for c,d in zip(col_names, r):
			df_row[c].append(d)
	
	_perc_to_float(df_row)
	_str_to_inches(df_row)

	return df_row



def _perc_to_float(data):
	percents = ['days_w_morethan_6_inches', 'months_w_more_than_90_inches', 
			'months_w_lessthan_30_inches', 'north-facing_terrain', 'east-facing_terrain',
			'west-facing_terrain', 'south-facing_terrain']
	perc = lambda x: float(x[:-1]) * 0.01
	vfunc = np.vectorize(perc)
	
	for p in percents:
		data[p] = vfunc(np.array(data[p]))
	return data

def _str_to_inches(data):
	inches = lambda x: float(x[:-1])
	vfunc = np.vectorize(inches)
	data['truesnow'] = vfunc(np.array(data['truesnow']))
	return data


#pages = [1, 2, 3, 4, 5, 6, 7, 8]
pages = [1]
df_pickle = []

for p in pages:
	r_page = f'https://www.zrankings.com/ski-resorts/snow?_=1571261206007&amp;page={p}'
	p_data = _scrape_resort_table(r_page)
	df_pickle.append(pd.DataFrame(p_data))
	print(f'Done with page {p}')

#df_whole = pd.concat(df_pickle, ignore_index=True)
#df_whole.to_pickle('../data/resorts_data.pkl')
print(df_pickle[0])
print('alL dOnE')










