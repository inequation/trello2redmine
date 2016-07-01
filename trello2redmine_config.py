# -*- coding: utf-8 -*-

# This is the trello2redmine configuration file.
# All data here is exemplary, you need to fill it properly for the script to work!

# Trello configuration
trello_board_link = 'https://example.com'	# As found on the board in Menu -> More -> Link to this board.

# Redmine configuration
redmine_root_url = 'https://example.com'
redmine_project_identifier = 'ProjectID'	# As appears in the Redmine URLs.
redmine_default_user = 'Foo Bar'			# Trello cards which are unassigned or whose assignee does not have a mapping in username_map will be assigned to this Redmine user.
redmine_verify_certificates = False			# Whether to verify SSL certificates.
redmine_api_key = 'fake key'				# Redmine REST API key. See: http://www.redmine.org/projects/redmine/wiki/Rest_api#Authentication

# Trello card label to Redmine priority map.
label_map = {
	u'':				u'Normalny',	# Default for no label.
	u'Trivial':			u'Trywialny',
	u'Mało ważne':		u'Niski',
	u'Normalne':		u'Normalny',
	u'Ważne':			u'Wysoki',
	u'VSD':				u'Pilny',
	u'Krytyczne':		u'Natychmiastowy',
}

# Trello-to-Redmine username map. Both are displayed names, *not* logins or IDs! Redmine names are resolved to user IDs behind the scenes.
username_map = {
	u'Trello User':		u'Redmine User',
	u'Foo Bar':			u'Foo Bar',
	u'Nickname':		u'Full Name',
}

# Trello list to Redmine status map. Redmine statuses are displayed names, *not* IDs! Statuses are resolved to IDs behind the scenes.
list_map = {
	u'TODO':				u'Nowy',
	u'To Do':				u'Nowy',
	u'ToDo':				u'Nowy',
	u'Backlog':				u'Nowy',
	u'Doing':				u'W toku',
	u'In progress':			u'W toku',
	u'In Progress':			u'W toku',
	u'WIP':					u'W toku',
	u'Done':				u'Rozwiązany',
	u'Confirmed':			u'Zamknięty',
	u"Won't fix/No repro":	u'Odrzucony',
	u"Won't done/fix":		u'Odrzucony',
}