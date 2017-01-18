#!/usr/bin/python
# -*- coding: utf-8 -*-

import trello2redmine_config as cfg

import sys
import json
import requests
import urlparse

if len(sys.argv) > 3 or (len(sys.argv) == 2 and sys.argv[1] == '-h'):
	print('Usage: {0} [<options>])'.format(sys.argv[0]))
	print('See %s for configuration.' % cfg.__file__)
	print('Options:')
	print(' -h    Displays this information.')
	print(' -c    Commits the import. Otherwise does a dry run (prints resulting JSON to screen instead of sending it to Redmine).')
	sys.exit(0)

# If a dry run, JSON is printed instead of submitted to Redmine.
dry_run = len(sys.argv) < 2 or sys.argv[2] != '-c'
if dry_run:
	print('Making a dry run! Re-run with -c to commit the import into Redmine.')
else:
	print('Making a commit!')

url = urlparse.urlparse(cfg.trello_board_link)
if not url.netloc.endswith('trello.com'):
	print('URL does not seem to be a Trello board link. Are you sure this is correct?')
	sys.exit(1)

# ============================================================================
# Trello JSON processing starts here.
# ============================================================================

print('Downloading board JSON from Trello...')
sys.stdout.flush()

#board = json.loads(open(sys.argv[1]).read())
board = requests.get(cfg.trello_board_link + '.json').json()

print('Processing board JSON...')
sys.stdout.flush()

orig_lists_dict = {}
lists_dict = {}
for l in board["lists"]:
	name = l["name"]
	if name in cfg.list_map:
		name = cfg.list_map[name]
	lists_dict[l["id"]] = name
	orig_lists_dict[l["id"]] = l["name"]
	
checklists_dict = {}
for c in board["checklists"]:
	checklists_dict[c["id"]] = c["checkItems"]

members_dict = {}
for m in board["members"]:
	name = m["fullName"]
	if name in cfg.username_map:
		name = cfg.username_map[name]
	members_dict[m["id"]] = name

labels_dict = {}
for l in board["labels"]:
	label = l["name"]
	if label in cfg.label_map:
		label = cfg.label_map[label]
	labels_dict[l["id"]] = label

comments_dict = {}
for a in board["actions"]:
	if a["type"] == "commentCard":
		card_id = a["data"]["card"]["id"]
		author_id = a["idMemberCreator"]
		comment_list = comments_dict[card_id] if card_id in comments_dict else []
		comment_list.append({
			"author":	members_dict[author_id] if author_id in members_dict else '',
			"text":		a["data"]["text"],
		})
		comments_dict[card_id] = comment_list

#print('Members:\n' + str(members_dict))
#print('Lists:\n' + str(lists_dict))
#print('Checklists:\n' + str(checklists_dict))
#print('Comments:\n' + str(comments_dict))

# ============================================================================
# Redmine configuration processing starts here.
# ============================================================================

print('Querying Redmine configuration...')
sys.stdout.flush()

redmine_projects = requests.get(cfg.redmine_root_url + '/projects.json', verify=cfg.redmine_verify_certificates, headers={'X-Redmine-API-Key': cfg.redmine_api_key}).json()
redmine_project_id = -1
for rp in redmine_projects["projects"]:
	if rp["identifier"] == cfg.redmine_project_identifier:
		redmine_project_id = rp["id"]
		break

if redmine_project_id < 0:
	print('Project with identifier {0} does not exist in Redmine!\n\n{1}'.format(cfg.redmine_project_identifier, str(redmine_users_dict)))
	sys.exit(1)
#print('Redmine project ID: {0}'.format(redmine_project_id))

redmine_users = requests.get(cfg.redmine_root_url + '/users.json', verify=cfg.redmine_verify_certificates, headers={'X-Redmine-API-Key': cfg.redmine_api_key}).json()
redmine_users_dict = {}
for ru in redmine_users["users"]:
	fullname = u'{0} {1}'.format(ru["firstname"], ru["lastname"])
	redmine_users_dict[fullname] = ru["id"]

#print('Redmine users:\n' + str(redmine_users_dict))

if not cfg.redmine_default_user in redmine_users_dict:
	print('Default user does not exist in Redmine!\n\n{0}'.format(str(redmine_users_dict)))
	sys.exit(1)

redmine_priorities = requests.get(cfg.redmine_root_url + '/enumerations/issue_priorities.json', verify=cfg.redmine_verify_certificates, headers={'X-Redmine-API-Key': cfg.redmine_api_key}).json()
redmine_priorities_dict = {}
redmine_default_priority = "Normalny"
for rp in redmine_priorities["issue_priorities"]:
	redmine_priorities_dict[rp["name"]] = rp["id"]
	if "is_default" in rp and rp["is_default"]:
		redmine_default_priority = rp["name"]
		
#print(u'Redmine priorities:\n' + str(redmine_priorities_dict))

redmine_statuses = requests.get(cfg.redmine_root_url + '/issue_statuses.json', verify=cfg.redmine_verify_certificates, headers={'X-Redmine-API-Key': cfg.redmine_api_key}).json()
redmine_statuses_dict = {}
redmine_default_status = "Nowy"
for rs in redmine_statuses["issue_statuses"]:
	redmine_statuses_dict[rs["name"]] = rs["id"]
	if "is_default" in rs and rs["is_default"]:
		redmine_default_status = rs["name"]
		
#print(u'Redmine statuses:\n' + str(redmine_priorities_dict))

# ============================================================================
# Direct Trello-to-Redmine mappings are made here.
# ============================================================================

print('Generating configuration mappings...')
sys.stdout.flush()

user_map = {}
for id, fullname in members_dict.iteritems():
	if not fullname in redmine_users_dict:
		print(u'Warning: user {0} not found in Redmine, defaulting to {1}'.format(fullname, cfg.redmine_default_user))
		fullname = cfg.redmine_default_user
	redmine_id = redmine_users_dict[fullname]
	user_map[id] = redmine_id
	#print(u'Matched user {0}, Trello ID {1}, Redmine ID {2}'.format(fullname, id, redmine_id).encode('utf-8'))

#print(u'User ID map:\n{0}\nDefault user ID: {1}'.format(str(user_map), redmine_users_dict[cfg.redmine_default_user]).encode('utf-8'))

priority_map = {}
for id, name in labels_dict.iteritems():
	if not name in redmine_priorities_dict:
		print(u'Warning: Trello label {0} is not mapped to a Redmine priority, defaulting to {1}'.format(name, redmine_default_priority).encode('utf-8'))
		name = redmine_default_priority
	redmine_id = redmine_priorities_dict[name]
	priority_map[id] = redmine_id
	#print(u'Matched label {0}, Trello ID {1}, Redmine ID {2}'.format(name, id, redmine_id).encode('utf-8'))

#print('Redmine priorities:\n' + str(redmine_priorities_dict))

status_map = {}
for id, name in lists_dict.iteritems():
	if not name in redmine_statuses_dict:
		print(u'Warning: Trello list {0} is not mapped to a Redmine status, defaulting to {1}'.format(name, redmine_default_status).encode('utf-8'))
		name = redmine_default_status
	redmine_id = redmine_statuses_dict[name]
	status_map[id] = redmine_id
	#print(u'Matched list {0}, Trello ID {1}, Redmine ID {2}'.format(name, id, redmine_id).encode('utf-8'))

#print('Redmine statuses:\n' + str(redmine_statuses_dict))

# ============================================================================
# Finally, cards processing.
# ============================================================================

print ('Processing cards...')
sys.stdout.flush()

dry_run_counter = 0
for c in board["cards"]:
	desc = c["desc"]
	if c["idChecklists"]:
		desc += u'\n'
		for id in c["idChecklists"]:
			for item in checklists_dict[id]:
				desc += u'\n[{0}] {1}'.format(u'x' if item["state"] == u'complete' else u' ', item["name"])
	card = {
		"issue": {
			"subject": u'[{0}][{1}] {2}'.format(board["name"], orig_lists_dict[c["idList"]], c["name"]),
			"description": desc,
			"project_id": redmine_project_id,
			"assigned_to_id": user_map[c["idMembers"][0]] if c["idMembers"] else redmine_users_dict[cfg.redmine_default_user],
			"status_id": status_map[c["idList"]] if c["idList"] else redmine_statuses_dict[redmine_default_status],
			"priority_id": priority_map[c["idLabels"][0]] if c["idLabels"] else redmine_priorities_dict[redmine_default_priority],
			"is_private": False
		}
	}
	print(u'Importing {0}...'.format(card["issue"]["subject"]).encode('utf-8'))
	issue_id = -1
	if dry_run:
		dry_run_counter += 1
		issue_id = dry_run_counter
		print(json.dumps(card, sort_keys=False, indent=4, separators=(',', ': ')))
	else:
		result = requests.post(cfg.redmine_root_url + '/issues.json', data=json.dumps(card), verify=cfg.redmine_verify_certificates, headers={'X-Redmine-API-Key': cfg.redmine_api_key, "Content-Type": "application/json"})
		if result.status_code >= 400:
			print('Error {0}: Request headers:\n{1}\nResponse headers:\n{2}\nContent: {3}'.format(str(result), result.request.headers, result.headers, result.content))
			sys.exit(1)
		else:
			print(str(result))
			issue = result.json()
			issue_id = issue["issue"]["id"]
			#print(u'Response JSON:\n{0}\nIssue ID: {1}'.format(str(issue), issue_id).encode('utf-8'))
	if issue_id >= 0 and c["id"] in comments_dict:
		for index, comment in enumerate(reversed(comments_dict[c["id"]])):
			update = {
				"issue": {
					"notes": u'{0}:\n{1}'.format(comment["author"], comment["text"]).format('utf-8') if len(comment["author"]) > 0 else comment["text"]
				}
			}
			print(u'Importing comment {0} of {1}...'.format(index + 1, len(comments_dict[c["id"]])).encode('utf-8'))
			if dry_run:
				print(json.dumps(update, sort_keys=False, indent=4, separators=(',', ': ')))
			else:
				result = requests.put(cfg.redmine_root_url + '/issues/{0}.json'.format(issue_id), data=json.dumps(update), verify=cfg.redmine_verify_certificates, headers={'X-Redmine-API-Key': cfg.redmine_api_key, "Content-Type": "application/json"})
				if result.status_code >= 400:
					print('Error {0}: Request headers:\n{1}\nResponse headers:\n{2}\nContent: {3}'.format(str(result), result.request.headers, result.headers, result.content))
					sys.exit(1)
				else:
					print(str(result))

print('Done!')
