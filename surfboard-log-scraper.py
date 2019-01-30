#! /usr/bin/env python3

import sys
from bs4 import BeautifulSoup
import urllib.request
import json 

soup = BeautifulSoup(urllib.request.urlopen(sys.argv[1]), 'html.parser')

table = soup.find('table', {'align': 'center'})

data = []
rows = table.find_all('tr')
for row in rows:
    cols = row.find_all('td')
    if cols == []: continue
    cols = [ele.text.strip() for ele in cols]
    data.append([ele for ele in cols if ele]) # Get rid of empty values



print(data)

