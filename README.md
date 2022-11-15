# Internal mailing and chatting app

setup postgresql in your device

https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-20-04
https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-22-04

configure db_config.ini
webapp/orm/database_folder/db_config.ini

run creating_tables.py to create tables
run models.py to create some basic users
{'name': 'admin1', 'username': 'username_admin1', 'email': 'admin1@admin.admin', 'password': 'admin1'}

pip install -r requirements.txt
python app.py
there are both views and api support which is independent of views

webapp/viewss contains views for normal purpose
webapp/api contains views fo apis

normal views doesnt use apis to collect data

both are impelmented separately for learning

url_config.py URL_DICTIONARY_API to see supported api calls

there is a real time chat for users which uses websocket,
