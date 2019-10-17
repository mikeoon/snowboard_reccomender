import requests
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
	col_names[3] = col_names[3][-4:]
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
	
	# cleans data to work with it easier later
	_perc_to_float(df_row)
	_str_to_inches(df_row)
	_range_to_bt(df_row)

	return df_row


# converts percent strings into decimals
def _perc_to_float(data):
	percents = ['days_w_morethan_6_inches', 'months_w_more_than_90_inches', 
			'months_w_lessthan_30_inches', 'north-facing_terrain', 'east-facing_terrain',
			'west-facing_terrain', 'south-facing_terrain']
	perc = lambda x: float(x[:-1]) * 0.01
	vfunc = np.vectorize(perc)
	
	for p in percents:
		data[p] = vfunc(np.array(data[p]))
	return data

# converts inches strings to actual float inches
def _str_to_inches(data):
	inches = lambda x: float(x[:-1])
	vfunc = np.vectorize(inches)
	data['truesnow'] = vfunc(np.array(data['truesnow']))
	return data

# converts base and top elevation into a more readable range
# Also makes 2 new columns, base and top
def _range_to_bt(data):
	ft = lambda x: float(x[:-1])
	vfunc = np.vectorize(ft)

	base = []
	top = []

	#splits the string into 2 useable floats
	for i in data['base_and_top_elev.']:
		temp = i.split('to')
		base.append(temp[0])
		top.append(temp[1])
	# makes two new columns
	data['base'] = vfunc(np.array(base))
	data['top'] = vfunc(np.array(top))
	data['base_and_top_elev.'] = [d.replace('to','-').replace('\'', '') for d in data['base_and_top_elev.']]
	return data


if __name__ == '__main__':
	# Runs the tables that they have now which are just 8
	pages = [1, 2, 3, 4, 5, 6, 7, 8]
	df_pickle = []
	print('Start scrape from zrankings')

	# Pulls from the 8 tables
	for p in pages:
		r_page = f'https://www.zrankings.com/ski-resorts/snow?_=1571261206007&amp;page={p}'
		p_data = _scrape_resort_table(r_page)
		df_pickle.append(pd.DataFrame(p_data))
		print(f'Done with page {p}')

	# Creates the pickled data frame for EDA and other use
	df_whole = pd.concat(df_pickle, ignore_index=True)
	df_whole.to_pickle('../data/resorts_data.pkl')
	print('\naLl DoNe')










