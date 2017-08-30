#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import print_function

import mysql.connector
from mysql.connector import errorcode
import json
import rem_backend.insert_query as insert_query

__author__ = "Daniel Denkovski, Valentin Rakovic"
__copyright__ = "Copyright (c) 2017, Faculty of Electrical Engineering and Information Technologies, UKIM, Skopje, Macedonia"
__version__ = "0.1.0"
__email__ = "{danield, valentin}@feit.ukim.edu.mk"

'''
Fills the REM data based with device with the predifined device locations, from configuration file.
'''

with open('device_locations.txt', 'r') as myfile:
	data=myfile.read()
	obj = json.loads(data)
	for gloloc in obj['global_locations']:
		loc = obj['global_locations'][gloloc]['coordinates']
		location_data = (gloloc, loc[0], loc[1], loc[2])
		locid = insert_query.insert_global_location(location_data)
		obj['global_locations'][gloloc]['loc_id'] = locid
		print(locid)
		print(obj['global_locations'])

	for device in obj['devices']:
		locloc = obj['devices'][device]['coordinates']
		floor = obj['devices'][device]['floor']
		locid = obj['global_locations'][obj['devices'][device]['global_loc_name']]['loc_id']
		device_data = (device, locloc[0], locloc[1], locloc[2], locid, floor, 0)
		insert_query.insert_device_location(device_data)

