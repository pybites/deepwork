# Deep Work Logger

See PyBites article: [Flask API part 2 - Building a Deep Work Logger with Flask, Slack and Google Docs](http://pybit.es/flask-api-part2.html) for more details.

Slack 'slash command' interface:

	/dw <time> (<activity>)
	- /dw is the slack command
	- time can be an int (hour) or more specifically hh:mm
	- activity is optional, if not provided it defaults to the name of the channel

---

![the complete flow](http://pybit.es/images/slackapi.png)
