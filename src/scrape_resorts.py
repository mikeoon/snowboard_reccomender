import requests
import re
from bs4 import BeautifulSoup


resort_urls = 'https://www.zrankings.com'
r_page = '/ski-resorts/snow?_=1571261206007&amp;page=1'

r = requests.get(resort_urls+r_page)
soup = BeautifulSoup(r.content, "lxml")

resort_table = soup.find(id='snowtable')

resort_col_names = resort_table.find('tr').find_all('th')

col_names = []
for i in resort_col_names:
	if i.text != '' and i.text != ' ':
		col_names.append(i.text.lower().replace(' ', '_').replace('w/', 'w').replace('&', 'and'))
col_names[0] = col_names[0][-6:]
col_names[1] = col_names[1][-4:]

resort_rows = resort_table.find('tbody').find_all('tr')

resort_data = []
for r in resort_rows:
	row = []
	for i in r.text.split('\n'):
		data = i.lstrip().rstrip()
		if len(data) != 0 and '--' not in data:
			row.append(data)
	resort_data.append(row)


print(len(resort_data[0]))
for i in resort_data[0]:
	print(i)

df_row = {}



















