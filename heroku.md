## Heroku deploy commands

I need to verify this, but I did the following more or less. See also my notes [here](http://bobbelderbos.com/2016/12/learning-flask-building-quote-app/).

* Login, make app, add remote:

	$ heroku login
	$ heroku create deepwork
	$ heroku git:remote -a deepwork

* Set up install files for Heroku:

	$ pip freeze > requirements.txt
	$ echo "web: gunicorn api:app" > Procfile
	$ echo "python-3.5.2" > runtime.txt

* Add environment variables:

	$ heroku config:set SLACK_DW_CMD_TOKEN=xyz
	$ heroku config:set SLACK_DW_USER=xyz
	$ heroku config:set SLACK_DW_PW=xyz

* Push code and deploy:

	$ git push heroku master  
	$ heroku run python api.py deploy

* Additional steps:

	# had to scale dyno
	$ heroku ps:scale web=1
	# watch requests come in:
	$ heroku logs -t
