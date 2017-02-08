import requests
import json
import os
import csv

if __name__ == '__main__':

	# name of csv output file
	pingdom_csv_file = "./pingdom_checks.csv"

	# get pingdom environmental variables
	pingdom_apiurl = os.getenv("PINGDOM_APIURL", None)
	pingdom_user = os.getenv("PINGDOM_USER", None)
	pingdom_password = os.getenv("PINGDOM_PASSWORD", None)
	pingdom_account_email = os.getenv("PINGDOM_ACCOUNT_EMAIL", None)
	pingdom_apikey = os.getenv("PINGDOM_APIKEY", None)

	# check for missing pingdom variables
	if pingdom_apiurl == None or pingdom_user == None or pingdom_password == None or pingdom_account_email == None or pingdom_apikey == None:
		print("@@@ Missing pingdom apiurl, user, password, account email and/or apikey @@@")
		exit(1)

	# get tag prefixes as variables
	pingdom_tag_tier = os.getenv("PINGDOM_TAG_TIER", None)
	pingdom_tag_systemcode = os.getenv("PINGDOM_TAG_SYSTEMCODE", None)

	# check for missing prefixes
	if pingdom_tag_tier == None or pingdom_tag_systemcode == None:
		print("@@@ Missing pingdom tag prefixes for teir and sysemcode tags")
		exit(1)

	# get cmdb api environmental variables
	cmdb_sysurl = os.getenv("CMDB_SYSURL", None)
	cmdb_apikey = os.getenv("CMDB_APIKEY", None)

	# check for missing pingdom variables
	if cmdb_sysurl == None or cmdb_apikey == None:
		print("@@@ Missing cmdb system url and/or apikey @@@")
		exit(1)

	# pingdom api call for list of checks
	print("Obtaining list of pingdom checks ...")
	url = pingdom_apiurl + "/api/2.0/checks?include_tags=true"
	payload = {}
	headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8', 'App-Key': pingdom_apikey, 'Account-Email':pingdom_account_email}
	response = requests.get(url, auth=(pingdom_user,pingdom_password), data=json.dumps(payload), headers=headers)

	# check for bad response
	if response.status_code != 200:
		print("@@@ failed to read pingdom api to gain list of checks: error="+str(response.status_code)+" @@@")
		exit(1)

	# loop through the checks
	print("Looping through the pingdom check to examine the tags ...")
	headings = []
	headings.append("name")
	headings.append("type")
	headings.append("hostname")
	headings.append("httpurl")
	headings.append("systemcode?")
	headings.append("tier?")
	rows = []
	for check in response.json().get('checks', []):
		# get the id so we can get the details of the check (the full URL to the system)
		checkid = check.get('id', None)
		if checkid:
			# pingdom api call for detail of the check
			detail_url = pingdom_apiurl + "/api/2.0/checks/" + str(checkid)
			detail_payload = {}
			detail_headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8', 'App-Key': pingdom_apikey, 'Account-Email':pingdom_account_email}
			detail_response = requests.get(detail_url, auth=(pingdom_user,pingdom_password), data=json.dumps(payload), headers=headers)

			# check for bad response
			if detail_response.status_code != 200:
				print("@@@ failed to read pingdom api to gain detail of check "+str(checkid)+": error="+str(detail_response.status_code)+" @@@")
				exit(2)

			# get http url from records that are http checks
			checkinfo = detail_response.json()['check']
			if check['type'] == "http":
				httpurl = checkinfo['type']['http']['url']
			else:
				httpurl = "?"
		else:
			httpurl = ""

#		print("@@@ check @@@"+str(check)+"@@@")
		tier = None
		systemcode = None
		checkname = check.get('name', None)#.encode('utf-8')
		checktype = check.get('type', None)#.encode('utf-8')
		hostname = check.get('hostname', None)#.encode('utf-8')
#		print("Checking: name="+str(checkname)+" type="+str(checktype)+" hostname="+str(hostname))
		row = {"name":checkname, "type": checktype, "hostname":hostname, "httpurl":httpurl}
#		print("  Tags:")
		for tag in check.get("tags", []):
			tagname = tag.get("name", "").lower()
#			print("    "+tagname)

			# extract tag prefix and suffix (assuming underscore is the separator)
			tagsplit = tagname.split('_')
			if len(tagsplit) == 2:
				tagprefix = tagsplit[0]
				tagsuffix = tagsplit[1]
			else:
				tagprefix = tagname
				tagsuffix = "Y"

			# add to putput row
			row.update({tagprefix:tagsuffix})

			# add prefix to csv headings if not already present
			if tagprefix not in headings:
				headings.append(tagprefix)

			# Explicit checks for "serviceTier" and "systemCode"
			if tagprefix == pingdom_tag_tier:
				tier = tagsuffix

			if tagprefix == pingdom_tag_systemcode:
				systemcode = tagsuffix

		# check if tags were found
		if tier:
			# store the existence of a service tier
			row.update({"tier?":"Present"})
		else:
#			print("@@@ "+str(checkname)+" is missing a service tier tag - please add tier_xxxx to the pingdom check @@@")
			row.update({"tier?":"@ MISSING @"})

		if systemcode == None:
#			print("@@@ "+str(checkname)+" is missing a systemcode tag - please add systemcode_xxxx to the pingdom check @@@") 
			row.update({"systemcode?":"@ MISSING @"})
		else:
			# now read the cmdb to see if the sytem code is valid
			cmdb_get_url = cmdb_sysurl + "/" + systemcode + "?apikey=" + cmdb_apikey
			cmdb_get_payload = {}
			cmdb_get_headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
			cmdb_response = requests.get(cmdb_get_url, data=json.dumps(cmdb_get_payload), headers=headers)

			# check for bad response
			if cmdb_response.status_code != 200:
#				print("@@@ systemcode "+systemcode+" not in cmdb: error="+str(cmdb_response.status_code)+" - should we add it? @@@")
				# store the existence of a service tier
				row.update({"systemcode?":"@ NOT IN CMDB @"})
			else:
				# store the existence of a service tier
				row.update({"systemcode?":"Yes"})
				# now check the servie tier against the cmdb value
				serviceTier = cmdb_response.json().get("serviceTier", "").lower()
				if tier:
					if serviceTier == tier:
						# store the existence of a service tier
						row.update({"tier?":"Matching CMDB"})
					else:
#						print("@@@ cmdb service tier of "+serviceTier+" for systemcode "+systemcode+" does not match pingdom tier of "+tier+" @@@")
						# store the existence of mismatched
						row.update({"tier?":"@ MISMATCH CMDB @"})

		# add row to list
		rows.append(row)

	# open output file
	print("Preparing report ...")
	csvfile = open(pingdom_csv_file, "w", newline='')
	writer = csv.writer(csvfile)

	# write headings
	writer.writerow(headings)

	# now lop through rows to output them to csv
	for values in rows:
		row = []
		# loop through headings
		for heading in headings:
			# extract and store appropriate value for heading name
			value = values.get(heading, '')
			row.append(value)

		# write row of output
		writer.writerow(row)

	# DONE
	print("./pingdom_checks.csv has been created")

	exit(0)