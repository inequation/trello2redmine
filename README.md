# trello2redmine

This is a tiny tool I've written to migrate all of our issue tracking data at once. It uses Trello's JSON export feature and the JSON flavour of [Redmine's REST API](http://www.redmine.org/projects/redmine/wiki/Rest_api).

We had been using [Trello](http://trello.com) as a stop-gap solution while our internal services (including [Redmine](http://www.redmine.org)) were being set up. Hence the limited scope of support for features – it was a one-time operation, and I don't really have a vested interest in the application, but it may be of use to others.

## Dependencies

Tested with Python 2.7, but was written with Python 3 compatibility in mind.

Beyond the standard library, the script only requires [Requests](http://docs.python-requests.org/en/master/user/install/) for HTTP support.

## Configuration and usage

Edit [trello2redmine_config.py](trello2redmine_config.py) and fill in the details of your installation. Then just run the script.

## Known issues

Not all features of Trello are supported. What works:

* creating Redmine issues from Trello cards,
* importing Trello card comments as Redmine issue comments,
* importing Trello checklists as plain text, appended to the issue description,
* mapping Trello users to Redmine users,
* mapping Trello lists to Redmine statuses,
* mapping Trello card labels to Redmine priorities.

What doesn't:

* multiple Trello card assignees: corresponding Redmine issue will only be assigned to the first one in Redmine,
* everything else.

## Licensing

```
        DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE 
                    Version 2, December 2004 

 Copyright (C) 2016 Leszek Godlewski

 Everyone is permitted to copy and distribute verbatim or modified 
 copies of this license document, and changing it is allowed as long 
 as the name is changed. 

            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE 
   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION 

  0. You just DO WHAT THE FUCK YOU WANT TO.
```