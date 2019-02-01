#! /usr/bin/env python3

import sys
from bs4 import BeautifulSoup
import urllib.request
import json 
import os.path
from pygelf import GelfUdpHandler
import logging

priorityMapping = {
	'6-Notice': logging.INFO,
	'5-Warning': logging.WARNING,
	'4-Error': logging.ERROR,
	'3-Critical': logging.CRITICAL,
}

lastErrorFile = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'last-error.json')

soup = BeautifulSoup(urllib.request.urlopen(sys.argv[1]), 'html.parser')

table = soup.find('table', {'align': 'center'})

data = []
rows = table.find_all('tr')
for row in rows:
    cols = row.find_all('td')
    if cols == []: continue
    cols = [ele.text.strip() for ele in cols]
    data.append([ele for ele in cols if ele]) # Get rid of empty values

last_error = []
try:
	if os.path.isfile(lastErrorFile):
		with open(lastErrorFile, 'r') as f:
			last_error = json.loads(f.read())
except json.decoder.JSONDecodeError:
	print("Couldn't parse last-error.json, assuming empty...", file=sys.stderr)
with open(lastErrorFile, 'w') as f:
	f.write(json.dumps(data[0]))

new_errors = []
for row in data:
	if row == last_error: break
	new_errors.insert(0,row)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
handler = GelfUdpHandler(sys.argv[2], port=int(sys.argv[3]), include_extra_fields=True)
handler.domain = sys.argv[4]
logger.addHandler(handler)

for reportedTime,originalPriority,code,message in new_errors:
	priority = priorityMapping[originalPriority] if originalPriority in priorityMapping else logging.WARNING
	logger.log(priority, message, extra={
		'originalPriority': originalPriority,
		'code': code,
		'reportedTime': reportedTime,
		})